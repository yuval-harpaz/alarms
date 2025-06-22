import pandas as pd
import numpy as np
import os
import requests
import matplotlib.pyplot as plt
import json
# How many cities make up "ברחבי הארץ"?
with open('/home/innereye/alarms/.txt') as f:
    cities_url = f.readlines()[1][:-1]
cities = requests.get(cities_url).json()
plac = []
for p in cities['cities'].keys():
    if p == 'חיפה - כרמל, הדר ועיר תחתית':
        plac.append('חיפה - כרמל, הדר ועיר תחתית')
    else:
        plac.extend(p.split(', '))
n_cities = len(plac)
if n_cities != 1435:
    print(f"Warning: Expected 1435 cities, found {n_cities} in the dataset.")
# Read the alarms data
df = pd.read_csv('data/alarms.csv')
# check names mismatch
prev_missing = json.load(open('data/missing_cities.json', 'r'))
ignore = ['ברחבי הארץ']
df_names = df[df['time'] > '2023-10-07']
missing = []
alternative = []
discontinued = []
for city in np.unique(df_names['cities']):
    if city[0] == "'":
        city = city[1:]+"'"
    if city not in plac and city not in prev_missing.keys() and city not in ignore:
        alternative.append('')
        if city.replace('-', ' ') in plac:
            alternative[-1] = city.replace('-', ' ')
        elif city.replace('-', ' - ') in plac:
            alternative[-1] = city.replace('-', ' - ')
        else:
            discontinued.append(city)
            print(f"City '{city}' is discontinued or not found in the cities dataset.")
        missing.append(city)

missing_dict = prev_missing.copy()
if len(missing) > 0:
    for city, alt in zip(missing, alternative):
        missing_dict[city] = alt
    # # make dict with missing cities, with keys for missing and alternative names or '' for values
    # missing_dict = {city: alt for city, alt in zip(missing, alternative)}
    # write missing_dict to a json file
    with open('data/missing_cities.json', 'w') as f:
        json.dump(missing_dict, f, ensure_ascii=False, indent=4)
        print(f"Missing cities: {missing}")

df_fixed = df.copy()
for city in missing_dict.keys():
    if city in df_fixed['cities'].values:
        if missing_dict[city] != '':
            df_fixed.loc[df_fixed['cities'] == city, 'cities'] = missing_dict[city]
    else:
        raise Exception(f"City '{city}' not found in the alarms data.")
df_fixed['cities'] = df_fixed['cities'].str.replace(' והפזורה', '')
# create a df with count of alarms from the beginning, from oct 7 2023 and from jun 13 2025
df_sum = pd.DataFrame(columns=['cities', df['time'][0][:10], '2023-10-07', '2025-06-13'])
names_unique = np.unique(df_fixed['cities'])
names_unique = list(names_unique)
_ = names_unique.pop(names_unique.index('ברחבי הארץ'))  # Remove 'ברחבי הארץ' from the list
# print(names_unique[313:317])
print('counting, takes time')
for icity, city in enumerate(names_unique):
    if city[0] == "'":
        city = city[1:]+"'"
    for date in df_sum.columns[1:]:
        count = np.sum((df_fixed['cities'] == city) & (df_fixed['time'].values > date))
        df_sum.at[icity, date] = count
df_sum['cities'] = names_unique
df_sum.to_csv('~/Documents/sum.csv', index=False)
# find empty alternatives in missing_dict and replace corresponding zeros with "" in df_sum
df_sum = pd.read_csv('~/Documents/sum.csv')
df_sum = df_sum.astype(str)
discontinued1 = []
for city in missing_dict.keys():
    if missing_dict[city] == '':
        discontinued1.append(city)
for city in discontinued1:
     row = np.where(df_sum['cities'].values == city)[0][0]
     for col in df_sum.columns[1:]:
         if df_sum[col][row] == '0':
             df_sum.at[row, col] = ''
    #  df_sum.loc[df_sum['cities'] == city, df_sum.columns[1:]] = ''
df_sum.to_csv('~/Documents/sum.csv', index=False)

df = df[df['time'].values > '2025-06-13']
# n_allover = len(np.unique(df['cities']))
orig = np.unique(df['origin'])
print('From Friday, June 13, 2025:')
for o in orig:
    n = np.sum(df['origin'] == o)
    if o == 'Iran':
        n = n - np.sum(df['cities'] == 'ברחבי הארץ') + n_cities * np.sum(df['cities'] == 'ברחבי הארץ')
    print(f"{o}: {n}")
iran = df[df['origin'] == 'Iran']
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
    icountry = np.where(df['origin'].values == country[ii])[0]
    df_country = df.iloc[icountry]
    allover = sum(df_country['cities'] == 'ברחבי הארץ')
    count.append(len(df_country) - allover + allover * n_cities)

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
    avg.append(int(np.round((len(time) + allover * n_cities - allover) / count[ii])))  # Average event size
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