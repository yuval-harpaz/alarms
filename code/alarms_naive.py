import requests
import pandas as pd
import numpy as np
import os





with open('.txt') as f:
    cities_url = f.readlines()[1][:-1]
cities = requests.get(cities_url).json()
locs = list(cities['cities'].keys())
for ii in range(len(locs)):
    if ',' in locs[ii]:
        split = locs[ii].split(',')
        split = [x.strip() for x in split]
        locs[ii] = split[0]
        locs.extend(split[1:])
coo = pd.read_csv('data/coord.csv')
center = [coo['lat'].mean(), coo['long'].mean()]
for loc in locs:
    if loc not in coo['loc'].values:
        print(loc)
##
df = pd.read_csv('data/alarms.csv')
df = df[df['time'] > '2023-10-07']
df = df.reset_index(drop=True)

for loc in locs:
    if loc not in df['cities'].values:
        print(loc)
