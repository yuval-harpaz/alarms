import sys
import pandas as pd
import os
import numpy as np
sys.path.append('code')
from map_deaths_name_search import group_locs


local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True
    sys.path.append(local + 'code')

coo = pd.read_csv('data/deaths_by_loc.csv')
db = pd.read_csv('data/oct7database.csv')
kid = db[db['Status'].str.contains('kidnapped')]
kid = kid.reset_index(drop=True)


kid['location'] = kid['מקום האירוע'].copy()
kid = group_locs(kid)
locu = np.unique(kid['location'])
kidonly = ['יער בארי', 'ישע גידולי אגו', 'מערבית לחורבת גררית']
kidonlyloc = ['31.42607410258214 34.47937875295837', '31.240036789420504 34.393274083720776', '31.413786 34.431981']
kidict = dict(zip(kidonly, kidonlyloc))
##
df = pd.DataFrame(columns=['location', 'coordinates', 'killed', 'kidnapped'])
df['location'] = coo['name']
df['killed'] = coo['total']
df['kidnapped'] = 0
for row in range(len(df)):
    df.at[row, 'coordinates'] = f"{coo['lat'][row]} {coo['long'][row]}"
for ii in range(len(locu)):
    row = np.where(coo['name'] == locu[ii])[0]
    if len(row) == 0:
        row = len(df)
        df.at[row, 'location'] = locu[ii]
        df.at[row, 'coordinates'] = kidict[locu[ii]]
        df.at[row, 'killed'] = 0
        df.at[row, 'kidnapped'] = np.sum(kid['location'] == locu[ii])
    else:
        row = row[0]
    #     # df.at[row, 'location'] = coo['name'][ii]
    #     df.at[row, 'coordinates'] = f"{coo['lat'][ii]} {coo['long'][ii]}"
    #     df.at[row, 'killed'] = coo['total'][row]
        df.at[row, 'kidnapped'] = np.sum(kid['location'] == locu[ii])

df.to_excel('~/Documents/map_ynet.xlsx')

