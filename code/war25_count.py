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
n_allover = len(np.unique(df['cities']))
country = ['Gaza','Lebanon','Yemen','Iran']
count = []
for ii in range(4):
    icountry = np.where(df['origin'].values == country[ii])[0]
    df_country = df.iloc[icountry]
    allover = sum(df_country['cities'] == 'ברחבי הארץ')
    count.append(len(df_country) - allover + allover * n_allover)

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
plt.show(block=True)

# check how many alarm events there where by grouping unique times
df = pd.read_csv('data/alarms.csv')
df = df[df['time'] > '2023-10-07']
df = df[df['description'] == 'ירי רקטות וטילים']
country = ['Gaza','Lebanon','Yemen','Iran']
distance = 15 # minutes
count = []
avg = []
# plt.figure()
for ii in range(4):
    icountry = np.where(df['origin'].values == country[ii])[0]
    df_country = df.iloc[icountry]
    time = pd.to_datetime(df_country['time'], format='%Y-%m-%d %H:%M:%S')
    diff = time.diff().dropna()
    diff = diff.dt.total_seconds().values / 60  # Convert to minutes
    diff = diff[diff > distance]
    allover = sum(df_country['cities'] == 'ברחבי הארץ')
    count.append(len(diff) + 1)  # +1 to count the first event
    # if allover:
    #     print(f"Allover: {allover} events in {country[ii]}")
    avg.append(int(np.round((len(time) + allover * n_allover - allover) / count[ii])))  # Average event size
    print(f"{country[ii]}: {count[ii]} events, avg size: {avg[ii]}")
    # plt.subplot(2, 2, ii+1)
    # h = plt.hist(diff, bins=100, color=['r','g','brown','k'][ii], zorder=3)
    # plt.title(country[ii])



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
plt.title(f'Alarm Events (>{distance}min quiet) by Origin')
plt.tight_layout()
plt.show(block=True)