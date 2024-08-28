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
did = db['pid'].values[db['Status'].str.contains('killed') & db['מקום האירוע'].str.contains('פסטיבל נובה')]
map = df = pd.read_csv('data/oct_7_9.csv')
mid = map['pid'].values[map['location'].str.contains('פסטיבל נובה')]
idif = [id for id in mid if id not in did]  # guy iluz 775
idif0 = [id for id in did if id not in mid]  # ofir testa 139
# changes = pd.read_csv('~/Documents/changes.csv')
# ich = np.where(changes['fixed'].str.lower() == 'v')[0]
# for ii in ich:
#     row = np.where(db['pid'].values == changes['pid'][ii])[0][0]
#     db.at[row, 'Role'] = changes['Role'][ii]
# db.to_csv('data/oct7database.csv', index=False)