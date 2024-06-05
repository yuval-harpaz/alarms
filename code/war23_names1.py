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
    islocal = True
##
# map7 = pd.read_json('https://service-f5qeuerhaa-ey.a.run.app/api/individuals')
# map = pd.read_csv('data/oct_7_9.csv')
cref = pd.read_csv('data/crossref.csv')
# locs = pd.DataFrame(cref['oct_7_9_fullName'])
names = pd.read_excel('/home/innereye/Documents/names.xlsx')
df = pd.read_excel('/home/innereye/Documents/database.xlsx')
btl = pd.read_excel('/home/innereye/Documents/btl_yael_netzer.xlsx')
## complete foreign names
# df = map7.filter(['pid','name'], axis=1)
# df = df.sort_values('pid', ignore_index=True)
for ii in range(len(df)):
    pid = df['pid'][ii]
    icref = np.where(cref['oct7map_pid'] == pid)[0]
    if len(icref) == 1:
        icref = icref[0]
        if type(df['שם פרטי'][ii]) != str:
            name = cref['btl_name'][icref]
            if type(name) == str:
                name = name.split('  ')
                if len(name) == 2:
                    df.at[ii, 'שם משפחה'] = name[1]
                if ' ' in name[0]:
                    first = name[0][:name[0].index(' ')]
                    middle = name[0][name[0].index(' '):]
                else:
                    first = name[0]
                    middle = ''
                df.at[ii, 'שם פרטי'] = first
                df.at[ii, 'שם נוסף'] = middle
for col in df.columns[1:]:
    df[col] = df[col].str.strip()
df.to_excel('/home/innereye/Documents/database.xlsx', index=False)
## fix status
for ii in range(len(df)):
    row = np.where(map7['pid'] == df['pid'][ii])[0][0]
    df.at[ii, 'status'] = map7['status'][row]

## add soldiers and other empty
# nobtl = np.where(cref['btl_id'] == 0)[0]
# pidnobtl = cref['oct7map_pid'].values[nobtl]
# nobtl = nobtl[pidnobtl > 0]
# pidnobtl = pidnobtl[pidnobtl > 0]
# rows = [np.where(df['pid'] == x)[0][0] for x in pidnobtl]
## split english
rows = np.where(df['first name'].isnull())[0]
for ii in rows:
    name = df['name'][ii].split(' ')
    df.at[ii, 'first name'] = name[0]
    df.at[ii, 'last name'] = name[-1]
    if len(name) > 2:
        df.at[ii, 'middle name'] = ' '.join(name[1:-1])

## add oct_7_9
map = pd.read_csv('data/oct_7_9.csv')
included = []
for ii in range(len(df)):
    pid = df['pid'][ii]
    icref = np.where(cref['oct7map_pid'] == pid)[0]
    if len(icref) == 1:
        icref = icref[0]
        row = cref['oct_7_9_id'][icref]
        included.append(row-1)
notinc = [x for x in range(len(map)) if x not in included]
new = pd.DataFrame(columns=df.columns)
for ii in range(len(notinc)):
    pid = 2000+ii+1
    name = map['fullName'][notinc[ii]].split(' ')
    # df.at[ii, 'first name'] = name[0]
    firsth = name[-1]
    lasth = name[0]
    # df.at[ii, 'last name'] = name[-1]
    if len(name) > 2:
        middleh = ' '.join(name[1:-1])
    else:
        middleh = np.nan
    name = map['eng'][notinc[ii]].split(' ')
    # df.at[ii, 'first name'] = name[0]
    firste = name[0]
    laste = name[-1]
    # df.at[ii, 'last name'] = name[-1]
    if len(name) > 2:
        middlee = ' '.join(name[1:-1])
    else:
        middlee = np.nan
    newrow = [pid, map['fullName'][notinc[ii]], firste, laste, middlee, np.nan, firsth, lasth, middleh, np.nan, np.nan]
    new.loc[len(new)] = newrow
new.to_excel('/home/innereye/Documents/missing.xlsx', index=False)
## integrate new pid to rxisting lists
db = pd.read_csv('/home/innereye/Documents/oct7database.csv')
haa = pd.read_csv('/home/innereye/alarms/data/deaths_haaretz+.csv')
cref = pd.read_csv('data/crossref.csv')
map = pd.read_csv('data/oct_7_9.csv')

pids = db['pid'].values
for ii in range(len(cref)):
    pid = cref['oct7map_pid'][ii]
    if pid > 0:
        map_row = cref['oct_7_9_id'][ii] - 1
        map.at[map_row, 'pid'] = pid
map.to_csv('data/oct_7_9.csv', index=False)
##
for ii in range(len(map)):
    pid = map['pid'][ii]
    haa_row = np.where(haa['map_row'] == ii + 2)[0]
    if len(haa_row) == 1:
        haa.at[haa_row[0], 'pid'] = pid
haa.to_csv('data/deaths_haaretz+.csv', index=False)

idf = pd.read_csv('data/deaths_idf.csv')
recent = haa.filter(['pid', 'name', 'rank', 'death_date'])
recent = recent[recent['pid'].isnull()]
for ii in recent.index:
    idf_row = haa['idf_row'][ii] - 2
    if ~np.isnan(idf_row):
        name = idf['name'][idf_row]
        recent.at[ii, 'idf_name'] = name
        name = name.split(' ')
    else:
        name = haa['name'][ii].split(' ')
    recent.at[ii, 'שם פרטי'] = name[0]
    recent.at[ii, 'שם משפחה'] = name[-1]
    if len(name) > 2:
        middle = ' '.join(name[1:-1])
        recent.at[ii, 'שם נוסף'] = middle
recent.to_csv('/home/innereye/Documents/recent.csv', index=False)
##
recent = pd.read_csv('/home/innereye/Documents/recent.csv')
idf = pd.read_csv('data/tmp_idf_eng.csv')
for ii in range(len(recent)):
    namer = recent['name'][ii].split()
    fit = []
    for jj in range(len(idf)):
        namei = idf['heb'][jj]
        score = 0
        for part in namer:
            if part in namei:
                score += 1
        fit.append(score)
    cand = np.where(np.array(fit) > 1)[0]
    if len(cand) == 1:
        recent.at[ii, 'idf_eng'] = idf['eng'][cand[0]]
    print(ii)
##
recent = pd.read_csv('/home/innereye/Documents/recent_eng.csv')
for ii in range(len(recent)):
    name = recent['idf_eng'][ii]
    if type(name) == str:
        if '(res.)' in name:
            name = name[name.index('(res.)') + 6:].strip()
        elif 'class' in name.lower():
            name = name[name.lower().index('class') + 5:].strip()
        else:
            rank = [x for x in ['sergeant', 'sergent', 'captain', 'lieutenant', 'major'] if x in name.lower()]
            if len(rank) == 1:
                name = name[name.lower().index(rank[0]) + len(rank[0]):].strip()
        name = name.split(' ')
        recent.at[ii, 'first name'] = name[0]
        recent.at[ii, 'last name'] = name[-1]
        if len(name) > 2:
            recent.at[ii, 'middle name'] = ' '.join(name[1:-1])
        else:
            recent.at[ii, 'middle name'] = np.nan
recent.to_csv('/home/innereye/Documents/recent_eng.csv', index=False)
## look for duplicates
war = pd.read_csv('/home/innereye/Documents/oct7database - war.csv')
data = pd.read_csv('/home/innereye/Documents/oct7database - Data.csv')
namew = [war['שם פרטי'][x] + ' ' + war['שם משפחה'][x] for x in range(len(war))]
named = np.array([data['שם פרטי'][x] + ' ' + data['שם משפחה'][x] for x in range(len(data))])
dup = pd.DataFrame(columns=['pid','name'])
for ii in range(len(namew)):
    row = np.where(named == namew[ii])[0]
    if len(row) > 1:
        raise Exception(namew[ii])
    elif len(row) == 1:
        dup.loc[len(dup)] = [data['pid'].values[row][0], namew[ii]]
dup.to_csv('/home/innereye/Documents/duplicates.csv', index=False)

dup = pd.DataFrame(columns=['pid','name'])
for ii in range(len(namew)):
    row = np.where(named == named[ii])[0]
    row = row[row != ii]
    if len(row) == 1:
        dup.loc[len(dup)] = [data['pid'].values[row][0], named[ii]]

##
for ii in range(len(haa)):
    pid = haa['pid'][ii]
    if np.isnan(pid):
        row = np.where([(data['שם פרטי'][x] in haa['name'][ii]) & (data['שם משפחה'][x] in haa['name'][ii]) for x in range(len(data))])[0]
        if len(row) == 1:
            haa.at[ii, 'pid'] = data['pid'][row[0]]
haa.to_csv('data/deaths_haaretz+.csv', index=False)
## make sure hebrew names are okay
## add oct_7_9 not in oct7map
# nopid = np.where([
# for ii in
## break english


## add birth date
##
#         btl_id = cref['btl_id'][icref]
#         if btl_id > 0:
#             ibtl = np.where(btl['Column 1'] == btl_id)[0]
#             if len(ibtl) == 1:
#                 ibtl = ibtl[0]
#                 name = names['first'][icref]
#             if ord(name[0]) > 1487:
#                 df.at[ii, 'שם פרטי'] = name
#                 df.at[ii, 'שם משפחה'] = names['last'][icref]
#                 df.at[ii, 'שם נוסף'] = names['middle'][icref]
#                 df.at[ii, 'כינוי'] = names['nick'][icref]
#             else:
#                 df.at[ii, 'first name'] = name
#                 df.at[ii, 'last name'] = names['last'][icref]
#                 df.at[ii, 'middle name'] = names['middle'][icref]
#                 df.at[ii, 'nickname'] = names['nick'][icref]
# df['status'] = map7['status']
# df.to_excel('/home/innereye/Documents/database.xlsx', index=False)
## copy data to a new table
# for ii in range(len(locs)):
#     pid = cref['oct7map_pid'][ii]
#     if pid > 0:
#         row = np.where(map7['pid'] == pid)[0][0]
#         locs.at[ii, 'oct7map_name'] = map7['name'][row]
# locs['oct_7_9_loc'] = map['location']
# for ii in range(len(locs)):
#     pid = cref['oct7map_pid'][ii]
#     if pid > 0:
#         row = np.where(map7['pid'] == pid)[0][0]
#         locs.at[ii, 'oct7map_loc'] = map7['location'][row]
#         locs.at[ii, 'oct7map_subloc'] = map7['sublocation'][row]
#         locs.at[ii, 'oct7map_est'] = map7['Estimated location?'][row]
#         locs.at[ii, 'oct7map_coo'] = map7['geotag'][row]
#         locs.at[ii, 'oct7map_source'] = map7['location_source'][row]
# ## complete coordinates for missing geotag based on sublocation
# # subloc = np.unique(locs['oct7map_subloc'][locs['oct7map_coo'].isnull()].values.astype(str))
# subloc = {'232 Blocked Road': [31.399963, 34.474210],
#           'Alumim Bomb Shelter (West)': [31.450412, 34.516401],
#           "Be'eri Bomb Shelter": [31.428803, 34.496924],
#           'Gama Junction Bomb Shelter (North)': [31.381336, 34.447480],
#           'Gama Junction Bomb Shelter (West)': [31.380127, 34.447162],
#           "Hostage Situation in Be'eri": [],
#           'Main Stage': [31.397771, 34.469951],
#           'Nahal Grar Bridge': [31.400212, 34.474301],
#           'Nova Ambulance': [31.397351, 34.469556],
#           'Nova Bar': [31.398900, 34.470031],
#           'Nova Entrance Bomb Shelter': [31.400190, 34.473742],
#           "Re'im Bomb Shelter (East)": [31.389740, 34.459447],
#           "Re'im Bomb Shelter (West)": [31.3897815832395, 34.45805954741456],
#           'Yellow Containers': [31.398628, 34.470782]}
#
# for ii in range(len(locs)):
#     pid = cref['oct7map_pid'][ii]
#     coo = str(locs['oct7map_coo'][ii])
#     if pid > 0 and coo[:2] != '31':
#         row = np.where(map7['pid'] == pid)[0][0]
#         sl = map7['sublocation'][row]
#         if str(sl) not in ['nan', 'None']:
#             locs.at[ii, 'oct7map_coo'] = str(subloc[sl])[1: -1]
#
# ## complete missing data based on location
# maploc = pd.read_csv('data/deaths_by_loc.csv')
# locrow = np.where(~maploc['oct7map'].isnull())[0]
# for lr in locrow:
#     trow = np.where(locs['oct7map_loc'].values == maploc['oct7map'][lr])[0]
#     for tr in trow:
#         if str(locs['oct7map_coo'][tr])[:2] != '31':
#             locs.at[tr, 'oct7map_coo'] = str(maploc['lat'][lr])+', '+str(maploc['long'][lr])
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
# locs.to_csv('data/tmp_locs.csv', index=False)
# ## compute distance
# names = pd.read_csv('data/oct_7_9.csv')
# names = group_locs(names)
# # replace = [['בכניסה לעלומים'], ['ביה"ח שיפא'], ['סמוך לצומת גמה', 'צומת גמה'], ['מיגונית בצומת גמה', 'צומת גמה'],
# #            ['צומת בארי'], ['מיגונית בצומת רעים', 'צומת רעים'], ['סמוך לצומת רעים', 'צומת רעים'], ['חאן יונס'],['מיגונית חניון רעים', 'פסטיבל נובה'],
# #            ['רצועת עזה', 'רצועת עזה, לא פורסם מיקום מדוייק'], ['דיר אל בלח'], ['מיגונית מפלסים','סמוך למפלסים']]  #
# #
# # for uu in replace:
# #     names.loc[names['location'].str.contains(uu[0]), 'location'] = uu[-1]  # -1 allows for pairs, search term + what to change into
#
# for ii in range(len(locs)):
#     trow = np.where(maploc['name'].values == names['location'][ii])[0][0]
#     coo79 = [maploc['lat'][trow], maploc['long'][trow]]
#     try:
#         coo7 = np.array(locs['oct7map_coo'][ii].replace(' ', '').split(',')).astype(float)
#         dif = geodesic(coo7, coo79).km
#         locs.at[ii, 'dif'] = np.round(dif, 1)
#     except:
#         locs.at[ii, 'dif'] = np.nan
# locs.to_csv('data/tmp_locs.csv', index=False)
#
# ##
# difs = locs.copy()
# difs = difs[~difs['dif'].isnull()]
# difs = difs.sort_values('dif', ascending=False, ignore_index=True)
# difs = difs[difs['dif'] >= 1]
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
