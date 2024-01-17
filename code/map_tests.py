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
    # sys.path.append(local + 'code')

coo = pd.read_excel('data/deaths_by_loc.xlsx', 'coo')
names = pd.read_excel('data/deaths_by_loc.xlsx', 'export')
# names['location'] = names['location'].str.replace('?', 'בבירור')
# coo = pd.read_csv('data/deaths_by_loc.csv')
center = [coo['lat'].mean(), coo['long'].mean()]
haa = pd.read_csv('data/deaths_haaretz+.csv')
nameh = haa['name'].values
##
for iname in range(len(names)):
    nm = names['fullName'][iname].split(' ')
    D = []
    for ih in range(len(haa)):
        nh = nameh[ih].split(' ')
        dist = []
        for name_parth in nh:
            d = []
            for name_part in nm:
                d.append(Levenshtein.distance(name_parth, name_part))
            dist.append(min(d))
        D.append(sum(dist))
    mind = min(D)
    if mind < 2:
        idx = np.where(np.array(D) == mind)[0]
        if len(idx) == 1:
            names.at[iname, 'haaretz_row'] = idx[0]+2
            names.at[iname, 'haaretz_name'] = nameh[idx[0]]
# names.to_csv('data/tmp.csv', index=False)
##
FIX MANUALLY
##
fixed = pd.read_excel('data/tmp.xlsx')
blank = fixed[fixed['haaretz_row'].isnull()]
blank.to_csv('data/tmp_nohaa.csv')
imiss = [x for x in range(len(haa)) if x not in fixed['haaretz_row'].values]
missed = haa.iloc[np.array(imiss)-2]
missed = missed[missed['death_date'].values < '2023-10-10']
missed.to_csv('data/tmp_unacc.csv')
haarow = np.where(~fixed['haaretz_row'].isnull())[0]
for ii in range(len(haarow)):
    # print(haa['name'][fixed['haaretz_row'][haarow[ii]]-2]+' '+fixed['fullName'][haarow[ii]])
    haa.at[fixed['haaretz_row'][haarow[ii]] - 2, 'map_row'] = haarow[ii]+2