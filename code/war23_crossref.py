import pandas as pd
import os
import numpy as np
import sys
import Levenshtein


local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True

map7 = pd.read_json('https://service-f5qeuerhaa-ey.a.run.app/api/individuals')
map = pd.read_csv('data/oct_7_9.csv')
cref = pd.read_csv('data/crossref.csv')
new = np.zeros(len(map), bool)
bad_start = np.where(map['fullName'].values[:len(cref)] != cref['oct_7_9_fullName'])[0]
if len(bad_start) > 0:
    err = ''
    for ii in range(len(bad_start)):
        err += f'\ncref: {cref["oct_7_9_fullName"][bad_start[ii]]} >> map: {map["fullName"][bad_start[ii]]}'
    print(err)
    resp = input('allow changes? y/!y')
    if resp.lower() == 'y':
        for ii in range(len(bad_start)):
            cref.at[bad_start[ii], "oct_7_9_fullName"] = map["fullName"][bad_start[ii]]
        cref.to_csv('data/crossref.csv', index=False)
    raise Exception('saved cref, start over')

if len(map) == len(cref):
    raise Exception('equal length lists')
for ii in range(len(map)):
    map.at[ii, 'id'] = ii + 1
new = map[len(cref):]
for inew in range(len(new)):
    idx = new.iloc[inew]['id']-1
    newline = len(cref)
    cref.at[newline,'oct_7_9_fullName'] = new['fullName'][idx]
    cref.at[newline, 'oct_7_9_id'] = new['id'][idx]
    cref.at[newline, 'oct_7_9_residence'] = new['residence'][idx]
cref.to_csv('data/crossref.csv', index=False)

# nameh = map7['hebrew_name'].values
# namee = map7['name'].values[(map7['status'].values == 'Murdered') | (map7['status'].values == 'Killed on duty')]
name = map['eng'].values
namh = map['fullName'].values
#
# map_match = pd.read_excel('/home/innereye/Documents/pid (1).xlsx')
# ##
# n = np.arange(len(map)) + 1
# df = pd.DataFrame(n, columns=['oct_7_9_id'])
# df['oct_7_9_fullName'] = namh
# df['oct_7_9_residence'] = map['residence']
no_pid = np.where((cref['oct7map_pid'].isnull().values) | (cref['oct7map_pid'].values == 0))[0]
manual = []
for row in no_pid:
    # print(cref['oct_7_9_fullName'][row])
    match = np.where(map7['hebrew_name'] == cref['oct_7_9_fullName'][row])[0]
    if len(match) != 1:
        match = np.where(map7['name'] == map['eng'][row])[0]
        # if len(match) == 1:
            # print(map7['name'][match[0]])
    if len(match) == 1:
        print(cref['oct_7_9_fullName'][row])
        row7 = match[0]
        pid = map7['pid'][row7]
        cref.at[row, 'oct7map_pid'] = pid
        cref.at[row, 'oct7map_name'] = map7['name'][row7]
    else:
        manual.append(cref['oct_7_9_fullName'][row])
    # row = np.where((map['fullName'].values == cref['fullName'][ii]) & (map['fullName'].values == map_match['fullName'][ii]))[0]
    # if len(row) == 1:
    #     row = row[0]
    # pid = map_match['oct7map_pid'][ii]
    #     df.at[row, 'oct7map_pid'] = pid
    #    if not np.isnan(map_match['oct7map_pid'][ii]) and pid > 0:
    # row7 = np.where(map7['pid'].values == pid)[0][0]
    #         df.at[row, 'oct7map_name'] = map7['name'][row7]
    # else:
    #     manual.append(ii)
    #     print(map_match['fullName'][ii])
cref['oct7map_pid'] = cref['oct7map_pid'].values.astype(int)
cref['oct7map_pid'][cref['oct7map_pid'] < 0] = 0
cref.to_csv('data/crossref.csv', index=False)
## AFTER MANUAL FIX

cref = pd.read_csv('data/crossref.csv')
no_map7_name = np.where((cref['oct7map_pid'].values > 0) & (cref['oct7map_name'].isnull().values))[0]
for row in no_map7_name:
    pid = cref['oct7map_pid'][row]
    cref.at[row, 'oct7map_name'] = map7['name'][map7['pid'] == pid].values[0]
cref.to_csv('data/crossref.csv', index=False)
##
# missing = [x.strip() for x in namee if x.strip() not in name]
# ##
# matched = pd.read_excel('/home/innereye/Documents/pid (1).xlsx')

# noheb = []
# for iname in range(len(names)):
#     nm = names['fullName'][iname].split(' ')
#     D = []
#     for ih in range(len(map7)):
#         if nameh[ih] is None:
#             if iname == 0:
#                 if 'idnap' not in map7.loc[ih, 'status']:
#                     noheb.append(map7.loc[ih, 'name'])
#             D.append(20)
#         else:
#             nh = nameh[ih].split(' ')
#             dist = []
#             for name_parth in nh:
#                 d = []
#                 for name_part in nm:
#                     d.append(Levenshtein.distance(name_parth, name_part))
#                 dist.append(min(d))
#             D.append(sum(dist))
#     mind = min(D)
#     if mind < 2:
#         idx = np.where(np.array(D) == mind)[0]
#         if len(idx) == 1:
#             names.at[iname, 'map7oct'] = map7.loc[idx[0], 'name']
# #
# # # names.to_csv('data/tmp.csv', index=False)
# # ##
# # FIX MANUALLY
# # ##
# # fixed = pd.read_excel('data/tmp.xlsx')
# # blank = fixed[fixed['haaretz_row'].isnull()]
# # blank.to_csv('data/tmp_nohaa.csv')
# # imiss = [x for x in range(len(haa)) if x not in fixed['haaretz_row'].values]
# # missed = haa.iloc[np.array(imiss)-2]
# # missed = missed[missed['death_date'].values < '2023-10-10']
# # missed.to_csv('data/tmp_unacc.csv')
# # haarow = np.where(~fixed['haaretz_row'].isnull())[0]
# # for ii in range(len(haarow)):
# #     # print(haa['name'][fixed['haaretz_row'][haarow[ii]]-2]+' '+fixed['fullName'][haarow[ii]])
# #     haa.at[fixed['haaretz_row'][haarow[ii]] - 2, 'map_row'] = haarow[ii]+2