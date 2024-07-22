# """
# collect event coordinates per person.
# 1. take personal coordinets from database
# 2. take from oct7map (maybe only Lahav)
# 3. take from oct_7_9
# 4. take from idf
# 5. take from haarets+
#
# """
# TODO: make a list of kidnap locations in kidnapped.csv
"""
first run war23_idf2db.py
then war23_map2db.py
test with war23_db_tests.py
push
download database as excel to ~/Documents/oct7database.xlsx

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
    kidnapped = ('idnap' in dbtype) | ('captivity' in dbtype) | pid in [915, 29, 568, 626]
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
##
#
# locs = pd.DataFrame(columns=['pid', 'oct_7_9_name', 'oct_7_9_loc', 'oct7map_loc'])
# # locs['oct_7_9_loc'] = map['location']
# for ii in range(len(pids)):
#     pid = pids[ii]
#     row = np.where(map7['pid'] == pid)[0][0]
#     loc = map7['location'][row]
#     sl = map7['sublocation'][row]
#     if type(sl) == str:
#         loc = loc+'; '+sl
#     locs.at[ii, 'oct7map_loc'] = loc
#     locs.at[ii, 'oct7map_coo'] = map7['geotag'][row]
#     locs.at[ii, 'pid'] = pid
#
# ## complete coordinates for missing geotag based on sublocation
# # subloc = np.unique(locs['oct7map_subloc'][locs['oct7map_coo'].isnull()].values.astype(str))
#
# for ii in range(len(locs)):
#     pid = locs['pid'][ii]
#     coo = str(locs['oct7map_coo'][ii])
#     row = np.where(map7['pid'] == pid)[0][0]
#     geotag = map7['geotag'][row]
#     sl = map7['sublocation'][row]
#     lc = map7['location'][row]
#     if type(geotag) == str and geotag[:2] == '31':
#         locs.at[ii, 'oct7map_coo'] = geotag
#     elif str(sl) not in ['nan', 'None']:
#         locs.at[ii, 'oct7map_coo'] = str(subloc[sl])[1: -1]
#     else:
#         lrow = np.where(maploc['oct7map'].values == lc)[0]
#         if len(lrow) == 1:
#             geotag = str(maploc['lat'][lrow[0]]) + ', ' + str(maploc['long'][lrow[0]])
#             locs.at[ii, 'oct7map_coo'] = geotag
#
#
# ## complete missing data based on location
# # maploc = pd.read_csv('data/deaths_by_loc.csv')
# # locrow = np.where(~maploc['oct7map'].isnull())[0]
# # for lr in locrow:
# #     trow = np.where(locs['oct7map_loc'].values == maploc['oct7map'][lr])[0]
# #     for tr in trow:
# #         if str(locs['oct7map_coo'][tr])[:2] != '31':
# #             locs.at[tr, 'oct7map_coo'] = str(maploc['lat'][lr])+', '+str(maploc['long'][lr])
#
# ## sublocations not represented in oct_7_9
# other = {'The pensioners bus in Sderot': '31.522808876615766, 34.59568825785523',
#          'Sderot Police Station': '31.522808876615766, 34.59568825785523',
#          'Erez': '31.55999246335105, 34.56505148304494',
#          'Kerem Shalom': '31.228310751744882, 34.28445082924824',
#          'COGAT Base': '31.55987823169991, 34.54622846569096'}
#
# for othr in list(other.keys()):
#     trow = np.where(locs['oct7map_loc'].values == othr)[0]
#     for tr in trow:
#         if str(locs['oct7map_coo'][tr])[:2] != '31':
#             locs.at[tr, 'oct7map_coo'] = other[othr]
# ##
# names = pd.read_csv('data/oct_7_9.csv')
# names = group_locs(names)
# for ii in range(len(locs)):
#     row = np.where(names['pid'] == locs['pid'][ii])[0][0]
#     lrow = np.where(maploc['name'].values == names['location'][row].split(';')[0])[0]
#     if len(lrow) == 0:
#         raise Exception(ii)
#     locs.at[ii, 'oct_7_9_name'] = names['fullName'][row]
#     locs.at[ii, 'oct_7_9_loc'] = names['location'][row]
#     geotag = str(maploc['lat'][lrow[0]]) + ', ' + str(maploc['long'][lrow[0]])
#     locs.at[ii, 'oct_7_9_coo'] = geotag
# locs = locs[~locs['oct7map_coo'].isnull()]
# locs.reset_index(inplace=True, drop=True)
# locs.to_csv('data/tmp_locs.csv', index=False)
# ## compute distance
#
# for ii in range(len(locs)):
#     coo79 = [float(x) for x in locs['oct_7_9_coo'][ii].split(',')]
#     coo7 = [float(x) for x in locs['oct7map_coo'][ii].split(',')]
#     dif = geodesic(coo7, coo79).km
#     locs.at[ii, 'dif'] = np.round(dif, 1)
# locs = locs.sort_values(['dif', 'oct7map_loc'], ignore_index=True, ascending=[False, True])
# locs.to_csv('data/tmp_locs.csv', index=False)
#
# ##
# difs = locs.copy()
# for exc in ['שיפא', 'חאן', 'רצועת עזה', 'באלי', 'נוסייר']:
#     difs = difs[~difs['oct_7_9_loc'].str.contains(exc)]
# # difs = difs[~difs['dif'].isnull()]
# # difs = difs.sort_values('dif', ascending=False, ignore_index=True)
# difs = difs[difs['dif'] > 1]
# difs.to_csv('data/tmp_dif.csv', index=False)
# ##
# # locs = pd.read_csv('data/tmp_locs.csv')
# # est = locs['oct7map_est'].values.astype(str)
# # est = np.array([x.strip() for x in est])
# # est[est == 'nan'] = 'None'
# # est[est == ''] = 'None'
# # estu = np.unique(est)
# # dif = locs['dif'].values
# # co = ['k*', '.c', '.b', '.g', '.k', '.r']
# # plt.figure()
# # for ig in range(len(estu)):
# #     x = np.where(est == estu[ig])[0]
# #     plt.plot(x, dif[x], co[ig], label=estu[ig])
# # plt.legend()
# # plt.xlabel('oct_7_9 row in table')
# # plt.ylabel('difference in km')
# # plt.grid()
# # plt.title('distance by estimate type')
#
#
#
# # nameh = map7['hebrew_name'].values
# # namee = map7['name'].values  # [(map7['status'].values == 'Murdered') | (map7['status'].values == 'Killed on duty')]
# # map = pd.read_csv('data/oct_7_9.csv')
# # name = map['eng'].values
# # ##
# # # missing = [x.strip() for x in namee if x.strip() not in name]
# # missing = []
# # for ii in range(len(name)):
# #     row = np.where(namee == name[ii])[0]
# #     if len(row) == 1:
# #         map.at[ii, 'oct7map_pid'] = map7['pid'][row[0]]
# #     else:
# #         map.at[ii, 'oct7map_pid'] = 0
# #         missing.append(ii)
# # map['oct7map_pid'] = map['oct7map_pid'].values.astype(int)
# # map.to_excel('/home/innereye/Documents/pid.xlsx', index=False)
#
# ##
