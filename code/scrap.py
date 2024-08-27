import pandas as pd
import os
import numpy as np
import sys
sys.path.append('code')
from map_deaths_name_search import group_locs
local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    local = True


db = pd.read_csv('data/oct7database.csv')
party = np.where(~db['Party'].isnull())[0]
for ii in range(len(ka)):
    row = np.where(db['pid'].values == ka['pid'][ii])[0][0]
    if str(ka['visit'][ii]) != 'nan':
        db.at[row, 'event_coordinates'] = ka['visit'][ii]
