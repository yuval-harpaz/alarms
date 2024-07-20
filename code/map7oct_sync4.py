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

# cref = pd.read_csv('data/crossref.csv')
## copy data to a new table
pids = np.sort([x for x in map7['pid'] if x in map['pid'].values])
##
locs = pd.DataFrame(columns=['pid', 'oct_7_9_name', 'oct_7_9_loc', 'oct7map_loc'])
# locs['oct_7_9_loc'] = map['location']
for ii in range(len(pids)):
    pid = pids[ii]
    row = np.where(map7['pid'] == pid)[0][0]
    loc = map7['location'][row]
    sl = map7['sublocation'][row]
    if type(sl) == str:
        loc = loc+'; '+sl
    locs.at[ii, 'oct7map_loc'] = loc
    locs.at[ii, 'oct7map_coo'] = map7['geotag'][row]
    locs.at[ii, 'pid'] = pid

## complete coordinates for missing geotag based on sublocation
# subloc = np.unique(locs['oct7map_subloc'][locs['oct7map_coo'].isnull()].values.astype(str))
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
##
maploc = pd.read_csv('data/deaths_by_loc.csv')
for ii in range(len(locs)):
    pid = locs['pid'][ii]
    coo = str(locs['oct7map_coo'][ii])
    row = np.where(map7['pid'] == pid)[0][0]
    geotag = map7['geotag'][row]
    sl = map7['sublocation'][row]
    lc = map7['location'][row]
    if type(geotag) == str and geotag[:2] == '31':
        locs.at[ii, 'oct7map_coo'] = geotag
    elif str(sl) not in ['nan', 'None']:
        locs.at[ii, 'oct7map_coo'] = str(subloc[sl])[1: -1]
    else:
        lrow = np.where(maploc['oct7map'].values == lc)[0]
        if len(lrow) == 1:
            geotag = str(maploc['lat'][lrow[0]]) + ', ' + str(maploc['long'][lrow[0]])
            locs.at[ii, 'oct7map_coo'] = geotag


## complete missing data based on location
# maploc = pd.read_csv('data/deaths_by_loc.csv')
# locrow = np.where(~maploc['oct7map'].isnull())[0]
# for lr in locrow:
#     trow = np.where(locs['oct7map_loc'].values == maploc['oct7map'][lr])[0]
#     for tr in trow:
#         if str(locs['oct7map_coo'][tr])[:2] != '31':
#             locs.at[tr, 'oct7map_coo'] = str(maploc['lat'][lr])+', '+str(maploc['long'][lr])

## sublocations not represented in oct_7_9
other = {'The pensioners bus in Sderot': '31.522808876615766, 34.59568825785523',
         'Sderot Police Station': '31.522808876615766, 34.59568825785523',
         'Erez': '31.55999246335105, 34.56505148304494',
         'Kerem Shalom': '31.228310751744882, 34.28445082924824',
         'COGAT Base': '31.55987823169991, 34.54622846569096'}

for othr in list(other.keys()):
    trow = np.where(locs['oct7map_loc'].values == othr)[0]
    for tr in trow:
        if str(locs['oct7map_coo'][tr])[:2] != '31':
            locs.at[tr, 'oct7map_coo'] = other[othr]
##
names = pd.read_csv('data/oct_7_9.csv')
names = group_locs(names)
for ii in range(len(locs)):
    row = np.where(names['pid'] == locs['pid'][ii])[0][0]
    lrow = np.where(maploc['name'].values == names['location'][row].split(';')[0])[0]
    if len(lrow) == 0:
        raise Exception(ii)
    locs.at[ii, 'oct_7_9_name'] = names['fullName'][row]
    locs.at[ii, 'oct_7_9_loc'] = names['location'][row]
    geotag = str(maploc['lat'][lrow[0]]) + ', ' + str(maploc['long'][lrow[0]])
    locs.at[ii, 'oct_7_9_coo'] = geotag
locs = locs[~locs['oct7map_coo'].isnull()]
locs.reset_index(inplace=True, drop=True)
locs.to_csv('data/tmp_locs.csv', index=False)
## compute distance

for ii in range(len(locs)):
    coo79 = [float(x) for x in locs['oct_7_9_coo'][ii].split(',')]
    coo7 = [float(x) for x in locs['oct7map_coo'][ii].split(',')]
    dif = geodesic(coo7, coo79).km
    locs.at[ii, 'dif'] = np.round(dif, 1)
locs = locs.sort_values(['dif', 'oct7map_loc'], ignore_index=True, ascending=[False, True])
locs.to_csv('data/tmp_locs.csv', index=False)

##
difs = locs.copy()
for exc in ['שיפא', 'חאן', 'רצועת עזה', 'באלי', 'נוסייר']:
    difs = difs[~difs['oct_7_9_loc'].str.contains(exc)]
# difs = difs[~difs['dif'].isnull()]
# difs = difs.sort_values('dif', ascending=False, ignore_index=True)
difs = difs[difs['dif'] > 1]
difs.to_csv('data/tmp_dif.csv', index=False)
##
# locs = pd.read_csv('data/tmp_locs.csv')
# est = locs['oct7map_est'].values.astype(str)
# est = np.array([x.strip() for x in est])
# est[est == 'nan'] = 'None'
# est[est == ''] = 'None'
# estu = np.unique(est)
# dif = locs['dif'].values
# co = ['k*', '.c', '.b', '.g', '.k', '.r']
# plt.figure()
# for ig in range(len(estu)):
#     x = np.where(est == estu[ig])[0]
#     plt.plot(x, dif[x], co[ig], label=estu[ig])
# plt.legend()
# plt.xlabel('oct_7_9 row in table')
# plt.ylabel('difference in km')
# plt.grid()
# plt.title('distance by estimate type')



# nameh = map7['hebrew_name'].values
# namee = map7['name'].values  # [(map7['status'].values == 'Murdered') | (map7['status'].values == 'Killed on duty')]
# map = pd.read_csv('data/oct_7_9.csv')
# name = map['eng'].values
# ##
# # missing = [x.strip() for x in namee if x.strip() not in name]
# missing = []
# for ii in range(len(name)):
#     row = np.where(namee == name[ii])[0]
#     if len(row) == 1:
#         map.at[ii, 'oct7map_pid'] = map7['pid'][row[0]]
#     else:
#         map.at[ii, 'oct7map_pid'] = 0
#         missing.append(ii)
# map['oct7map_pid'] = map['oct7map_pid'].values.astype(int)
# map.to_excel('/home/innereye/Documents/pid.xlsx', index=False)

##
