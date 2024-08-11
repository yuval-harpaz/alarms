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

base = pd.read_excel('~/Documents/מוצב נחל עוז.xlsx', 'נחל עוז')
##
db = pd.read_excel('~/Documents/oct7database.xlsx', 'Data')
# cref = pd.read_csv('data/crossref.csv')
map = pd.read_csv('data/oct_7_9.csv')
for ii in range(len(base)):
    pid = base['pid'][ii]
    loc = 'מוצב נחל עוז' + '; ' + base['מקום במוצב'][ii]
    dbrow = np.where(db['pid'].values == pid)[0][0]
    maprow = np.where(map['pid'].values == pid)[0]
    kidn = db['Status'][dbrow][:3] == 'kid'
    if len(maprow) == 1:
        maprow = maprow[0]
    else:
        maprow = None

    if db['מקום האירוע'][dbrow] == 'מוצב נחל עוז':
        db.at[dbrow, 'מקום האירוע'] = loc
    else:
        raise Exception('not nahal oz event for pid '+str(pid))
    if db['מקום המוות'][dbrow] == 'מוצב נחל עוז':
        db.at[dbrow, 'מקום המוות'] = loc
    if maprow is not None:
        if map['location'][maprow] == 'מוצב נחל עוז':
            map.at[maprow, 'location'] = loc
        else:
            print(map['fullName'][maprow])
    # if  is not None:
    #     print(ii)
    #     map.at[maprow, 'location']

##
db.to_csv('~/Documents/tmp_oct7database.csv', index=False)
map.to_csv('data/oct_7_9.csv', index=False)

##
db = pd.read_excel('~/Documents/oct7database.xlsx', 'Data')
coo = pd.read_csv('~/Documents/מוצב נחל עוז קואו.csv', header=None)
# cref = pd.read_csv('data/crossref.csv')
# map = pd.read_csv('data/oct_7_9.csv')
for ii in range(len(base)):
    pid = base['pid'][ii]
    dbrow = np.where(db['pid'].values == pid)[0][0]
    latlon = coo[1].values[coo[0] == base['מקום במוצב'][ii]][0]
    db.at[dbrow, 'event_coordinates'] = latlon

db.to_csv('~/Documents/tmp_oct7database.csv', index=False)