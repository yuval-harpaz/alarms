import pandas as pd
import os
import numpy as np
import sys
import Levenshtein


local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    local = True
    file = open('.txt')
    url = file.read().split('\n')[0]
    file.close()
map7 = pd.read_json(url)
# nameh = map7['hebrew_name'].values
namee = map7['name'].values[(map7['status'].values == 'Murdered') | (map7['status'].values == 'Killed on duty')]
map = pd.read_csv('data/oct_7_9.csv')
name = map['eng'].values
##
missing = [x.strip() for x in namee if x.strip() not in name]
##
matched = pd.read_excel('/home/innereye/Documents/pid (1).xlsx')

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