import pandas as pd
import numpy as np
import os
import requests
import matplotlib.pyplot as plt
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

df = pd.read_csv('data/alarms.csv')
df = df[df['time'] > '2023-10-07']
country = ['Gaza','Lebanon','Yemen','Iran']
count = []
for ii in range(4):
    count.append(np.sum(df['origin'].values == country[ii]))

plt.figure()
# Set up grid first with lower zorder
plt.grid(axis='y', zorder=0)
# Draw bars with higher zorder to appear in front
for ii in range(4):
    plt.bar(ii, count[ii], 0.667, color=['r','g','brown','k'][ii], zorder=3)
for ii in range(4):
    formatted_count = f"{count[ii]:,}"
    plt.text(ii, 1000, formatted_count, ha='center', va='bottom', color='w')
plt.xticks(range(4), country)
plt.ylabel('Number of Alarms')
plt.title('Alarms by Origin')
plt.tight_layout()

# check how many alarm events there where by grouping unique times
df = pd.read_csv('data/alarms.csv')
df = df[df['time'] > '2023-10-07']
df = df[df['description'] == 'ירי רקטות וטילים']
time = df['time'].values
time = [t[:-3] for t in time]
df['time'] = time
country = ['Gaza','Lebanon','Yemen','Iran']
count = []
for ii in range(4):
    df_country = df[df['origin'].values == country[ii]]
    count.append(len(np.unique(df_country['time'])))


plt.figure()
# Set up grid first with lower zorder
plt.grid(axis='y', zorder=0)
# Draw bars with higher zorder to appear in front
for ii in range(4):
    plt.bar(ii, count[ii], 0.667, color=['r','g','brown','k'][ii], zorder=3)
for ii in range(4):
    formatted_count = f"{count[ii]:,}"
    plt.text(ii, 150, formatted_count, ha='center', va='bottom', color='k')
plt.xticks(range(4), country)
plt.ylabel('Number of Events')
plt.title('Alarm Events by Origin')
plt.tight_layout()