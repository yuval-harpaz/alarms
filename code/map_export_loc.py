"""Export data to html map."""
import pandas as pd
import numpy as np
import geojson
from urllib import request
import json
import os
import sys
from datetime import datetime
##
os.chdir('/home/innereye/alarms')
with open('.txt', 'r') as f:
    address = f.read().split('\n')[6]

db = pd.read_csv('data/oct7database.csv')
area = pd.read_csv('data/coord_area.csv')
coo = area['points'][0]
lon = [float(c.split(', ')[1]) for c in coo.split(';')]
lat = [float(c.split(', ')[0]) for c in coo.split(';')]
print('done prep')
def export_json(field='Country', criterion='not ישראל', language='heb'):
    with request.urlopen(address) as url:
        data = json.load(url)
    pid = np.array([x['properties']['pid'] for x in data['features']])
    mapname = field + '_' + criterion
    mapname = mapname.replace(' ', '_')
    telda = False
    if 'not ' in criterion:
        telda = True
        criterion = criterion.replace('not ', '')
    if '*' in criterion:
        index = db[field].str.contains(criterion.replace('*',''))
        index = index.values == True
    else:
        index = db[field].values == criterion
    if telda:
        index = ~index
    if sum(index) == 0:
        raise Exception('no cases passed criterion')
    selected = db[index]

    events = np.array([x.split(';')[0] for x in selected['Status'].values])
    geojson_features = []
    coos = []
    for event in ['killed', 'kidnapped']:
        df = selected[events == event]
        df = df.reset_index(drop=True)
        coo = np.zeros((len(df), 2))
        for jj in range(len(df)):
            item = np.where(pid == df['pid'][jj])[0]
            if len(item) == 1:
                latlon = data['features'][item[0]]['geometry']['coordinates']
                coo[jj, :] = latlon
            else:
                print(f"missing coordinates for : {df['first name'][jj]} {df['last name'][jj]} at {df['מקום האירוע'][jj]}")
        # Iterate over the dataframe to create features
        coo_string = np.array([f"{x[0]}, {x[1]}" for x in coo])
        # coo = np.array([x.split(', ')[::-1] for x in coo_string]).astype(float)
        coou_string = np.unique(coo_string)
        if len(coo_string) == 0:
            continue
        if coou_string[0] == '0.0, 0.0':
            coou_string = coou_string[1:]
        if len(coo_string) == 0:
            continue
        coou = np.array([x.split(', ') for x in coou_string]).astype(float)
        coos.extend(coou)
        for ii in range(len(coou)):
            rows = np.where(coo_string == coou_string[ii])[0]
            name = ''
            for row in rows:
                if language.lower()[:2] == 'en':
                    name = name + f"{df['first name'][row]} {df['last name'][row]}" + "<br>"
                else:
                    name = name + f"{df['שם פרטי'][row]} {df['שם משפחה'][row]}" + "<br>"
            name = name[:-4]
            properties = {
                "name": name,
                "event": event,
            }
            feature = geojson.Feature(
                properties=properties,
                geometry=geojson.Point(list(coou[ii]))
            )
            geojson_features.append(feature)
    geojson_data = geojson.FeatureCollection(geojson_features)
    geojson_path = f'/home/innereye/Documents/Map/{mapname}.geojson'
    # Save to a GeoJSON file
    with open(geojson_path, 'w') as f:
        geojson.dump(geojson_data, f)
    print(f"GeoJSON file created: {geojson_path}")
    return mapname, coos





def json2map(mapname, center, comment=None):
    if comment is None:
        comment = str(datetime.now())
    with open('/home/innereye/Documents/Map/'+mapname+'.geojson', 'r') as f:
        data = f.read()
    with open('/home/innereye/Documents/Map/tmp2.html', 'r') as f:
        html = f.read()
    before = html[:html.index("var geojsonData = {")]
    after = html[html.index("var Killed = L.layerGroup()"):]
    optxt = before + "var geojsonData = " + data + "\n" + after
    optxt = optxt.replace("center: [31.425145, 34.48899],", f"center: [{center[1]}, {center[0]}],")
    optxt = optxt.replace("Foreign", mapname)
    optxt = optxt.replace('<!-- comment -->', f"<!-- {comment} -->")
    mapfile = f'/home/innereye/Documents/Map/{mapname}.html'
    with open(mapfile, 'w') as f:
        f.write(optxt)
    print(f"map created: {mapfile}")
print('created functions')
if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('use: python map_export_loc.py LOCATION COMMENT')
        print('or: python map_export_loc.py FIELD VALUE COMMENT')
        print('you can use *VALUE or "not VALUE"')
        sys.exit()
        # dbg = False
        # if dbg:
        #     field = 'Role'
        #     criterion = 'שוטר'
        #     comment = 'debug'
        #     mapname, coos = export_json(field=field, criterion=criterion, language='He')
        #     center = np.mean(coos, 0)
        #     json2map(mapname, center, comment)
    elif len(sys.argv) == 2:
        if sys.argv[1][0] == 'p':
            print('polygons')
            sys.exit()
        else:
            print(f'option {sys.argv[1]} unknown')
            sys.exit()
    elif len(sys.argv) == 3:
        field = 'מקום האירוע'
        criterion = sys.argv[1]
        comment = sys.argv[2]
    elif len(sys.argv) == 4:
        field = sys.argv[1]
        criterion = sys.argv[2]
        comment = sys.argv[3]
    mapname, coos = export_json(field=field, criterion=criterion, language='He')
    center = np.mean(coos, 0)
    json2map(mapname, center, comment)
