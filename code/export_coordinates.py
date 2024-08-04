"""
first run war23_idf2db.py
consider using war23_map2db.py if something changed in oct_7_9.csv
test with war23_db_tests.py
push
refresh and download database as excel to ~/Documents/oct7database.xlsx
run this code

The code should make 3 columns of locations. oct7map, db by place name, and db coordinates. Check for large differences
"""
import pandas as pd
import os
import numpy as np
from geopy.distance import geodesic
import sys
sys.path.append('code')
from map_deaths_name_search import group_locs
local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    local = True
    file = open('.txt')
    url = file.read().split('\n')[0]
    file.close()
map7 = pd.read_json(url)
map = pd.read_csv('data/oct_7_9.csv')
map = group_locs(map)
# map = pd.read_csv('data/oct_7_9.csv')
db = pd.read_excel('~/Documents/oct7database.xlsx', 'Data')
# cref = pd.read_csv('data/crossref.csv')

##
subloc = {'232 Blocked Road': [31.399963, 34.474210],
          'Alumim Bomb Shelter (West)': [31.450412, 34.516401],
          "Be'eri Bomb Shelter": [31.428803, 34.496924],
          'Gama Junction Bomb Shelter (North)': [31.381336, 34.447480],
          'Gama Junction Bomb Shelter (West)': [31.380127, 34.447162],
          "Hostage Situation in Be'eri": [31.42804511392142, 34.49307314081499],
          'Main Stage': [31.397771, 34.469951],
          'Nahal Grar Bridge': [31.400212, 34.474301],
          'Nova Ambulance': [31.397351, 34.469556],
          'Nova Bar': [31.398900, 34.470031],
          'Nova Entrance Bomb Shelter': [31.400190, 34.473742],
          "Re'im Bomb Shelter (East)": [31.389740, 34.459447],
          "Re'im Bomb Shelter (West)": [31.3897815832395, 34.45805954741456],
          'Yellow Containers': [31.398628, 34.470782]}
sublocheb = {'אשקלון; בי"ח ברזילי': [31.6632444309682, 34.5578359719349],
             'בארי; ארוע בני ערובה': [31.423137676630546, 34.493090778786325],
             'יד מרדכי - נתיב העשרה; קבוצת ריצה': [31.57576149845013, 34.55275119619444],
             'כביש רעים – אורים (צפון)': [31.3830878311482, 34.4552414506731],
             'מטעים של בארי (מגורי עובדים)': [31.4054968725694, 34.4537661162609],
             'מיגונית בצומת גמה (דרום)': [31.380127,34.447162],
             'מיגונית בצומת גמה (מערב)': [31.380127, 34.447162],
             'מיגונית בצומת גמה (צפון)': [31.381336, 34.447480],
             'מיגונית בצומת רעים (מזרח)': [31.389740, 34.459447],
             'מיגונית בצומת רעים (מערב)': [31.389781, 34.458059],
             'סמוך למיגונית בצומת גמה (דרום)': [31.380216626100477, 34.44733662392307],
             'סמוך למיגונית בצומת גמה (צפון)': [31.381307046724753, 34.44754169695219],
             'עזה; ביה"ח שיפא': [31.399963, 34.474210],
             'עזה; מבנה סמוך לביה"ח שיפא': [31.399963, 34.474210],
             'דיר אל בלח; בי"ח חללי אל אקצא': [31.42097888989603, 34.35960647838112],
             'חאן יונס; ביה"ח נאצר': [31.351538612807232, 34.292552168121006],
             'מצרים; אלכסנדריה': [31.182732054836766, 29.896308654768227],
             "ג’נין; מחנה הפליטים": [32.461362867968454, 35.28754210285402],
             'עזה; מסגד סמוך לביה"ח שיפא': [31.399963, 34.474210],
             'פסטיבל נובה; אמבולנס': [31.397351, 34.469556],
             'פסטיבל נובה; במה מרכזית': [31.397771, 34.469951],
             'פסטיבל נובה; בר': [31.398900, 34.470031],
             'פסטיבל נובה; גשר נחל גרר': [31.400212, 34.474301],
             'פסטיבל נובה; חסימה בכביש 232': [31.399963, 34.474210],
             'פסטיבל נובה; מכולות צהובות': [31.398628, 34.470782],
             'שדרות; אוטובוס הגמלאים': [31.52677040015094, 34.60108324482743],
             'שדרות; תחנת משטרה': [31.52249812718559, 34.59202432204493]}

maploc = pd.read_csv('data/deaths_by_loc.csv')

##
pids = db['pid'].values
locations = pd.DataFrame(columns=['pid', 'name', 'event type', 'event loc', 'event coo', 'death loc', 'death coo',
                                  'oct7map loc', 'oct7map coo', 'oct7map source', 'db personal coo',
                                  'personal - event loc', 'personal - map7', 'event loc - map7'])
locations['pid'] = pids
for ii in range(len(pids)):
    pid = pids[ii]
    dbevent = db['מקום האירוע'][ii]
    dbdeath = db['מקום המוות'][ii]
    dbtype = str(db['Status (oct7map)'][ii])
    kidnapped = ('idnap' in dbtype) | ('captivity' in dbtype) | pid in [915, 29, 568, 626, 1068, 1730, 139]  # injured and died at different places
    name = (db['שם פרטי'][ii] + ';' +
            str(db['שם נוסף'][ii]) + ';' +
            db['שם משפחה'][ii]
            ).replace('nan', '').replace(';;', ' ').replace(';', ' ')
    row = np.where(map['pid'] == pid)[0]
    # if len(row) == 1:
    #     row = row[0]
    #     name = (dfdb['שם פרטי'][ii]+';'+str(dfdb['שם נוסף'][ii])+';'+dfdb['שם משפחה'][ii]).replace('nan', '').replace(';;', ' ').replace(';', ' ')
    locations.at[ii, 'name'] = name
    loc79 = db['מקום המוות'][ii]
    locations.at[ii, 'death loc'] = loc79
    if loc79 and str(loc79) != 'nan':
        if ';' in loc79:
            if loc79 in sublocheb.keys():
                coo = sublocheb[loc79]
                coo = f"{coo[0]}, {coo[1]}"
                locations.at[ii, 'death coo'] = coo
            else:
                print(f'no coo for {loc79}')
                if loc79 == "ג'נין; מחנה הפליטים":
                    print('x')
        else:
            li = np.where(maploc['name'] == loc79)[0]
            if len(li):
                coo = f"{maploc['lat'][li[0]]}, {maploc['long'][li[0]]}"
                locations.at[ii, 'death coo'] = coo
    loc79 = db['מקום האירוע'][ii]
    locations.at[ii, 'event loc'] = loc79
    if loc79 and str(loc79) != 'nan':
        if ';' in loc79:
            if loc79 in sublocheb.keys():
                coo = sublocheb[loc79]
                coo = f"{coo[0]}, {coo[1]}"
                locations.at[ii, 'event coo'] = coo
        else:
            li = np.where(maploc['name'] == loc79)[0]
            if len(li):
                coo = f"{maploc['lat'][li[0]]}, {maploc['long'][li[0]]}"
                locations.at[ii, 'event coo'] = coo
    if kidnapped:
        if str(db['Death date'][ii])[:10] == '2023-10-07':
            if db['מקום המוות'][ii] == db['מקום האירוע'][ii]:
                locations.at[ii, 'event type'] = 'kidnapped (body)'
            else:
                locations.at[ii, 'event type'] = 'kidnapped (killed)'
        elif 'urvivor' in db['Status'][ii]:
            locations.at[ii, 'event type'] = 'kidnapped (released)'
        elif str(db['Death date'][ii]) != 'nan':
            locations.at[ii, 'event type'] = 'kidnapped (killed)'
        else:
             locations.at[ii, 'event type'] = 'kidnapped'
    else:
        locations.at[ii, 'event type'] = 'killed'
    row = np.where(map7['pid'].values == pid)[0]
    if len(row) == 1:
        row = row[0]
        locations.at[ii, 'oct7map loc'] = db['Event location (oct7map)'][ii]
        if map7['location'][row] not in db['Event location (oct7map)'][ii]:
            raise Exception('loc7 do not match')
        locations.at[ii, 'oct7map source'] = map7['location_source'][row]
        if map7['geotag'][row]:
            locations.at[ii, 'oct7map coo'] = map7['geotag'][row]
        elif map7['sublocation'][row] in subloc.keys():
            coo7 = subloc[map7['sublocation'][row]]
            locations.at[ii, 'oct7map coo'] = coo7
        else:
            locrow = np.where(maploc['oct7map'].values == map7['location'][row])[0]
            if len(locrow):
                coo7 = f"{maploc['lat'][locrow[0]]}, {maploc['long'][locrow[0]]}"
                locations.at[ii, 'oct7map coo'] = coo7
    if str(db['event_coordinates'][ii])[:2] == '31':
        locations.at[ii, 'db personal coo'] = db['event_coordinates'][ii]
locations.to_csv('~/Documents/locations.csv', index=False)
## difs
def geodif(idx, col0, col1):
    coo0 = locations[col0][idx]
    coo1 = locations[col1][idx]
    if type(coo0) == str and type(coo1) == str:
        dif = geodesic(np.array(coo0.split(',')).astype(float), np.array(coo1.split(',')).astype(float)).km
    else:
        dif = np.nan
    return dif

col3 = [['personal - event loc', 'db personal coo', 'event coo'],
                    ['personal - map7', 'db personal coo', 'oct7map coo'],
                    ['event loc - map7', 'event coo', 'oct7map coo']]
for ii in range(len(locations)):
    for cols in col3:
        locations.at[ii, cols[0]] = geodif(ii, cols[1], cols[2])

locations.to_csv('~/Documents/locations.csv', index=False)
