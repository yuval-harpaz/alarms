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
df = pd.read_csv('~/Documents/locations2eng.csv')
locations = pd.DataFrame(columns=['Event location', ''])
