"""Export data to html map."""
import pandas as pd
import numpy as np
import geojson
from urllib import request
import json
import os
import sys
from datetime import datetime
from polygons import load_polygons, assign, area_for
website = os.environ['WEBSITE']
##
os.chdir(os.environ['HOME'] + '/alarms')
with open('.txt', 'r') as f:
    address = f.read().split('\n')[6]

db = pd.read_csv('data/oct7database.csv')
areas = load_polygons()
area_by_name = {props['name_he']: props for props, _ in areas}
geom_by_name = {props['name_he']: geom for props, geom in areas}
def export_json(field='Country', criterion='not ישראל', language='heb', polygonize=False, exclude_from='2023-10-10'):
    print('reading data... ', end='')
    with request.urlopen(address) as url:
        data = json.load(url)
    print('done')
    if exclude_from is not None:
        db_filtered = db[db['Event date'].values < exclude_from]
    else:
        db_filtered = db
    pid = np.array([x['properties']['pid'] for x in data['features']])
    coo_by_pid = {}
    for feature in data['features']:
        if feature['geometry']:
            lon, lat = feature['geometry']['coordinates'][:2]
            coo_by_pid[feature['properties']['pid']] = (lat, lon)
    blur = {}
    if polygonize:
        # Perform polygonization here
        mapname = 'locations'
        # See polygons.area_for for the precedence. Geometry is the fallback, and
        # it is what catches the people the old string join used to drop: a place
        # name spelled differently from the polygon's matched nothing, and their
        # exact address was published instead of being blurred.
        for person, place in zip(db_filtered['pid'].values,
                                 db_filtered['מקום האירוע'].values):
            props = area_for(place, coo_by_pid.get(person), areas)
            if props is not None and not props['public_exact']:
                blur[person] = props['name_he']
        in_polygon = db_filtered['pid'].isin(list(blur))
        selected = db_filtered[~in_polygon]
        to_polygonize = db_filtered[in_polygon]
        print(f"Debug: {len(blur)} people blurred into {len(set(blur.values()))} areas")
    else:
        mapname = field + '_' + criterion
        mapname = mapname.replace(' ', '_')
        telda = False
        if 'not ' in criterion:
            telda = True
            criterion = criterion.replace('not ', '')
        if '*' in criterion:
            index = db_filtered[field].str.contains(criterion.replace('*',''))
            index = index.values == True
        else:
            index = db_filtered[field].values == criterion
        if telda:
            index = ~index
        if sum(index) == 0:
            raise Exception('no cases passed criterion')
        selected = db_filtered[index]

    events = np.array([x.split(';')[0].strip() for x in selected['Status'].values])
    geojson_features = []
    coos = []
    print(f"Debug: Found {sum(events == 'killed')} killed and {sum(events == 'kidnapped')} kidnapped in selected data")
    for event in ['killed', 'kidnapped']:
        df = selected[events == event]
        df = df.reset_index(drop=True)
        print(f"Debug: Processing {event}, found {len(df)} people")
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
        print(f"Debug: For {event}, unique coordinates: {coou_string[:5]}")
        if len(coo_string) == 0:
            print(f"Debug: Skipping {event} - no coordinates")
            continue
        if coou_string[0] == '0.0, 0.0':
            coou_string = coou_string[1:]
            print(f"Debug: Removed 0.0, 0.0 coordinate for {event}")
        if len(coou_string) == 0:
            print(f"Debug: Skipping {event} - only had 0.0, 0.0 coordinates")
            continue
        coou = np.array([x.split(', ') for x in coou_string]).astype(float)
        coos.extend(coou)
        for ii in range(len(coou)):
            rows = np.where(coo_string == coou_string[ii])[0]
            name = ''
            pid_str = ''
            for row in rows:
                pid_str = pid_str + f"{int(df['pid'][row])}" + ","
                if language.lower()[:2] == 'en':
                    name = name + f"{df['first name'][row]} {df['last name'][row]}" + "<br>"
                else:
                    name = name + f"{df['שם פרטי'][row]} {df['שם משפחה'][row]}" + "<br>"
            name = name[:-4]
            pid_str = pid_str[:-1]
            place_name = df['מקום האירוע'].values[rows[0]]
            # The publication link comes from the same area the person was
            # assigned to, so areas recorded by name only -- no ring ever drawn,
            # such as כפר עזה; דור צעיר -- still reach the tooltip.
            props = area_for(place_name, (coou[ii][1], coou[ii][0]), areas)
            link = props['source_url'] if props else ''
            link_text = props['source_text'] if props else ''
            if props and link and not link_text:
                print(f"Warning: {props['name_he']} has a source_url but no source_text")
            if isinstance(place_name, float) and np.isnan(place_name):
                raise ValueError(f"NaN place_name for pid(s) {pid_str}, event={event}, name={name!r}")
            properties = {
                "name": name,
                "event": event,
                "place_name": place_name,
                "link": link,
                "link_text": link_text,
                "pid": pid_str,
            }
            feature = geojson.Feature(
                properties=properties,
                geometry=geojson.Point(list(coou[ii]))
            )
            if name:  # Check if name is not empty
                geojson_features.append(feature)
                print(f"Debug: Added {event} feature for {name[:30]}...")
    print(f"Debug: Total geojson features created: {len(geojson_features)}")
    if polygonize:
        to_polygonize = to_polygonize.reset_index(drop=True)
        assigned = np.array([blur[p] for p in to_polygonize['pid'].values])
        for loc in sorted(set(blur.values())):
            place_name = loc
            rows = np.where(assigned == loc)[0]
            killed = ''
            kidnapped = ''
            pid_list = ''
            for row in rows:
                status = to_polygonize['Status'].values[row].split(';')[0].strip()
                pid_list = pid_list + f"{to_polygonize['pid'][row]}" + ","
                if status == 'killed':
                    killed = killed + f"{to_polygonize['שם פרטי'][row]} {to_polygonize['שם משפחה'][row]}" + ", "
                elif status == 'kidnapped':
                    kidnapped = kidnapped + f"{to_polygonize['שם פרטי'][row]} {to_polygonize['שם משפחה'][row]}" + ", "
                else:
                    raise Exception(f"unknown status {status}")
            pid_list = pid_list[:-1]  # Remove trailing comma
            if len(killed) == 0:
                details = kidnapped[:-2]
            elif len(kidnapped) == 0:
                details = killed[:-2]
            else:
                details = f"נהרגו: {killed[:-2]}<br>נחטפו: {kidnapped[:-2]}"
            polygon_coords = [list(c) for c in geom_by_name[loc].exterior.coords]
            properties = {
                "place_name": place_name,
                "name_en": area_by_name[loc]['name_en'],
                "details": details,
                "pid": pid_list,
            }
            feature = geojson.Feature(
                properties=properties,
                geometry=geojson.Polygon([polygon_coords])
            )
            geojson_features.append(feature)
    geojson_data = geojson.FeatureCollection(geojson_features)
    geojson_path = f'{website}{mapname}.geojson'
    # Save to a GeoJSON file
    with open(geojson_path, 'w') as f:
        geojson.dump(geojson_data, f)
    print(f"GeoJSON file created: {geojson_path}")
    return mapname, coos





def json2map(mapname, center, comment=None):
    if comment is None:
        comment = str(datetime.now())
    with open(website+mapname+'.geojson', 'r') as f:
        data = f.read()
    if comment == 'public map':  # polygons to anonymize
        with open(website+'tmp2p.html', 'r') as f:
            html = f.read()
    else:
        with open(os.environ['HOME']+'/Documents/Map/tmp2.html', 'r') as f:
            html = f.read()
    # if 'Polygon' in data:
    #     first_poly = data.index('Polygon')
    #     data_poly = data[first_poly-42:]
    #     data = data[: first_poly-44]
    # else:
    #     first_poly = None

        
    before = html[:html.index("var geojsonData = {")]
    if 'Polygon' in data:
        after = html[html.index("var Areas = L.layerGroup()"):]
    else:
        after = html[html.index("var Killed = L.layerGroup()"):]
    optxt = before + "var geojsonData = " + data + "\n" + after
    optxt = optxt.replace("center: [31.425145, 34.48899],", f"center: [{center[1]}, {center[0]}],")
    optxt = optxt.replace("Foreign", mapname)
    optxt = optxt.replace('<!-- comment -->', f"<!-- {comment} -->")
    mapfile = f"{os.environ['HOME']}/Documents/Map/{mapname}.html"
    if 'Polygon' in data:
        mapfile = f'{website}{mapname}.html'
    with open(mapfile, 'w') as f:
        f.write(optxt)
    print(f"map created: {mapfile}")
print('created functions')
if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('use: python map_export_loc.py LOCATION COMMENT')
        print('or: python map_export_loc.py FIELD VALUE COMMENT')
        print('you can use *VALUE or "not VALUE"')
        
        dbg = False
        if dbg:
            mapname, coos = export_json(polygonize=True)
            center = np.median(coos, 0)
            json2map(mapname, center, 'public map')
            sys.exit()
            # field = 'Role'
            # criterion = 'שוטר'
            # comment = 'debug'
            # mapname, coos = export_json(field=field, criterion=criterion, language='He')
            # center = np.mean(coos, 0)
            # json2map(mapname, center, comment)
        sys.exit()
    elif len(sys.argv) == 2:
        if sys.argv[1][0] == 'p':
            print('polygons')
            mapname, coos = export_json(polygonize=True)
            center = np.median(coos, 0)
            json2map(mapname, center, 'public map')
            sys.exit()
        else:
            print(f'option {sys.argv[1]} unknown')
            sys.exit()
    elif len(sys.argv) == 3:
        field = 'מקום האירוע'
        criterion = sys.argv[1]
        comment = sys.argv[2]
        language = 'He'
    elif len(sys.argv) == 4:
        if sys.argv[3].lower() in ['en', 'english']:
            field = 'מקום האירוע'
            criterion = sys.argv[1]
            comment = sys.argv[2]
            language = 'En'
        else:
            field = sys.argv[1]
            criterion = sys.argv[2]
            comment = sys.argv[3]
            language = 'He'
    elif len(sys.argv) == 5:
        field = sys.argv[1]
        criterion = sys.argv[2]
        comment = sys.argv[3]
        language = 'En' if sys.argv[4].lower() in ['en', 'english'] else 'He'
    else:
        print('Too many arguments')
        sys.exit()
    print(f'exporting map for {field} {criterion} in {language} with comment "{comment}"')
    mapname, coos = export_json(field=field, criterion=criterion, language=language)
    center = np.mean(coos, 0)
    json2map(mapname, center, comment)
