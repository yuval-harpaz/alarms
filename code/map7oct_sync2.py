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
# nameh = map7['hebrew_name'].values
namee = map7['name'].values  # [(map7['status'].values == 'Murdered') | (map7['status'].values == 'Killed on duty')]
map = pd.read_csv('data/oct_7_9.csv')
name = map['eng'].values
##
# missing = [x.strip() for x in namee if x.strip() not in name]
missing = []
for ii in range(len(name)):
    row = np.where(namee == name[ii])[0]
    if len(row) == 1:
        map.at[ii, 'oct7map_pid'] = map7['pid'][row[0]]
    else:
        map.at[ii, 'oct7map_pid'] = 0
        missing.append(ii)
map['oct7map_pid'] = map['oct7map_pid'].values.astype(int)
map.to_excel('/home/innereye/Documents/pid.xlsx', index=False)

##
exact = map7[