import pandas as pd
import numpy as np
import os
from geopy.distance import geodesic

local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True

coo = pd.read_csv('data/coord.csv')

Gaza = np.array([34.490547, 31.596096, 34.5249, 31.5715, 34.559166, 31.546944, 34.558609, 31.533054,
                 34.539993, 31.514721, 34.513329, 31.498608, 34.478607, 31.471107, 34.4337, 31.4329,
                 34.388885, 31.394722, 34.364166, 31.360832, 34.373604, 31.314442, 34.334160, 31.259720,
                 34.267578, 31.216541])
Gaza = Gaza.reshape(int(len(Gaza)/2), 2)[:, [1, 0]]
coo['km_from_Gaza'] = np.nan
for ii in range(len(coo)):
    lat = coo.iloc[ii]['lat']
    long = coo.iloc[ii]['long']
    d = []
    for g in Gaza:
        d.append(geodesic([np.median(lat), np.median(long)], g).km)
    coo.at[ii, 'km_from_Gaza'] = np.min(d)
print('done')
coo['km_from_Gaza'] = np.round(coo['km_from_Gaza'], 3)
coo.to_csv('data/coord_km_gaza.csv', index=False)
