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
map = pd.read_csv('data/oct_7_9.csv')
# nameh = map7['hebrew_name'].values
# namee = map7['name'].values[(map7['status'].values == 'Murdered') | (map7['status'].values == 'Killed on duty')]
name = map['eng'].values
namh = map['fullName'].values

map_match = pd.read_excel('/home/innereye/Documents/pid (1).xlsx')
##
n = np.arange(len(map)) + 1
df = pd.DataFrame(n, columns=['oct_7_9_id'])
df['oct_7_9_fullName'] = namh
df['oct_7_9_residence'] = map['residence']
manual = []
for ii in range(len(map_match)):
    row = np.where((map['fullName'].values == map_match['fullName'][ii]) & (map['fullName'].values == map_match['fullName'][ii]))[0]
    if len(row) == 1:
        row = row[0]
        pid = map_match['oct7map_pid'][ii]
        df.at[row, 'oct7map_pid'] = pid
        if not np.isnan(map_match['oct7map_pid'][ii]) and pid > 0:
            row7 = np.where(map7['pid'].values == pid)[0][0]
            df.at[row, 'oct7map_name'] = map7['name'][row7]
    else:
        manual.append(ii)
        print(map_match['fullName'][ii])
df['oct7map_pid'] = df['oct7map_pid'].values.astype(int)
df['oct7map_pid'][df['oct7map_pid'] < 0] = 0
df.to_csv('data/crossref.csv', index=False)
##
df = pd.read_csv('data/crossref.csv')
btl = pd.read_csv('data/batal.csv')
dfid = df['btl_id'].values
for ii in range(len(btl)):
    if btl['ID'][ii] in dfid:
        r = np.where(dfid == btl['ID'][ii])[0]
        if len(r) != 1:
            raise Exception('too many '+str(btl['ID'][ii]))
        else:
            r = r[0]
        if np.isnan(btl['oct_7_9_id'][ii]) or btl['oct_7_9_id'][ii] == 0:
            btl.at[ii, 'oct_7_9_id'] = df['oct_7_9_id'][r]
        if type(btl['oct_7_9_name'][ii]) == float and np.isnan(btl['oct_7_9_name'][ii]):
            btl.at[ii, 'oct_7_9_name'] = df['oct_7_9_fullName'][r]
        if type(df['btl_name'][r]) == float:
            df.at[r, 'btl_name'] = btl['full'][ii]
    else:
        parts = btl['full'][ii].replace('(', '').replace(')', '').split(' ')
        first = btl['first'][ii]
        parts = [x for x in parts if x not in [first, '']]

        row_first = df['oct_7_9_fullName'].str.contains(first).values.astype(int)
        row = row_first.copy()
        try:
            for part in parts:
                row = row + df['oct_7_9_fullName'].str.contains(part).values.astype(int)
            row = np.where(row_first.astype(bool) & (row > 1))[0]
            if len(row) == 1:
                df.at[row[0], 'btl_id'] = btl['ID'][ii]
                df.at[row[0], 'btl_name'] = btl['full'][ii]
                btl.at[ii, 'oct_7_9_id'] = row[0]
                btl.at[ii, 'oct_7_9_name'] = df['oct_7_9_fullName'][row[0]]
        except:
            print('issue with '+btl['full'][ii]+' '+str(ii))
        if ii%100 == 0:
            print(f'done {ii}')

##
df['btl_id'] = df['btl_id'].values.astype(int)
df['btl_id'][df['btl_id'] < 0] = 0
df.to_csv('data/crossref.csv', index=False)

btl['oct_7_9_id'] = btl['oct_7_9_id'].values.astype(int)
# btl['oct_7_9_id'][btl['oct_7_9_id'] < 0] = 0
btl.to_csv('data/batal.csv', index=False)
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