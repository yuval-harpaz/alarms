import pandas as pd
import numpy as np
import os
import requests
with open('/home/innereye/alarms/.txt') as f:
    cities_url = f.readlines()[1][:-1]
cities = requests.get(cities_url).json()
n_cities = len(cities['cities'].keys())
df = pd.read_csv('data/alarms.csv')
df = df[df['time'].values > '2025-06-13']
orig = np.unique(df['origin'])
for o in orig:
    print(f"{o}: {np.sum(df['origin'] == o)}")
iran = df[df['origin'] != 'Yemen']
allover = np.sum(iran['cities'] == 'ברחבי הארץ')

print('Iran:')
for des in np.unique(iran['description']):
    n = np.sum(iran['description'] == des)
    if "רקטות" in des:
        n = n - allover + allover * n_cities
    print(f"{des}: {n}")
