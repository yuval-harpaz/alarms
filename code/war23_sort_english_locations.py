import pandas as pd
import numpy as np
import os


db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})
locations = np.unique(list(db['מקום האירוע']) + list(db['מקום המוות']))[1:]
df = pd.DataFrame(columns=['Heb'])
df['Heb'] = locations
for iloc, location in enumerate(locations):
    eng = np.unique(list(db['Event location'][db['מקום האירוע'] == location]) +
                    list(db['Death location'][db['מקום המוות'] == location]))
    eng = [e for e in eng if str(e) != 'nan']
    for ii in range(len(eng)):
        df.at[iloc, ii + 1] = eng[ii]
df.to_csv('~/Documents/locations2eng.csv', index=False)

##
# raise Exception('do not run, open the csv and make sure there is only one translation')

##
df = pd.read_csv('~/Documents/locations2eng.csv')
for loc in df['1'].values:
    if np.sum(df['1'] == loc) > 1:
        print(loc)

##
db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})
df = pd.read_csv('~/Documents/locations2eng.csv')
h2e = {'מקום האירוע': 'Event location', 'מקום המוות': 'Death location'}
locations = pd.DataFrame(columns=['מקום האירוע', 'מקום המוות', 'Event location', 'Death location'])
for col in h2e.values():
    locations[col] = db[col]
for row_db in range(len(db)):
    for col in h2e.keys():
        loc = db.at[row_db, col]
        row_dict = np.where(df['Heb'] == loc)[0]
        if len(row_dict) == 1:
            row_dict = row_dict[0]
            eng = df.at[row_dict, 'Eng']
            locations.at[row_db, h2e[col]] = eng
        else:
            if str(loc) != 'nan':
                print(f'No translation for {loc}')

