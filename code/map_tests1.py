import pandas as pd
import os
import numpy as np
import Levenshtein


local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True
    # sys.path.append(local + 'code')

haa = pd.read_csv('data/deaths_haaretz+.csv')
names = pd.read_excel('data/deaths_by_loc.xlsx', 'export')
# names_row = np.array(names.index)+2
missing = []
for ii in range(2, len(names)+3):
    if ii not in haa['map_row'].values:
      missing.append(ii)

row = np.array([x for x in haa['map_row'] if not np.isnan(x)])
dup = []
for x in np.unique(row):
    if np.sum(row == x) > 1:
        dup.append(x)

maprow = 75
haarow = np.where(haa['map_row'] == maprow)[0][0]
print(haa['name'][haarow]+' '+names['fullName'][maprow-2])
#
# coo = pd.read_excel('data/deaths_by_loc.xlsx', 'coo')
# names = pd.read_excel('data/deaths_by_loc.xlsx', 'export')
# # names['location'] = names['location'].str.replace('?', 'בבירור')
# # coo = pd.read_csv('data/deaths_by_loc.csv')
# center = [coo['lat'].mean(), coo['long'].mean()]

#
# ##
# fixed = pd.read_excel('data/tmp.xlsx')
# blank = fixed[fixed['haaretz_row'].isnull()]
# blank.to_csv('data/tmp_nohaa.csv')
# imiss = [x for x in range(len(haa)) if x not in fixed['haaretz_row'].values]
# missed = haa.iloc[np.array(imiss)-2]
# missed = missed[missed['death_date'].values < '2023-10-10']
# missed.to_csv('data/tmp_unacc.csv')
# haarow = np.where(~fixed['haaretz_row'].isnull())[0]
# for ii in range(len(haarow)):
#     # print(haa['name'][fixed['haaretz_row'][haarow[ii]]-2]+' '+fixed['fullName'][haarow[ii]])
#     haa.at[fixed['haaretz_row'][haarow[ii]] - 2, 'map_row'] = haarow[ii]+2