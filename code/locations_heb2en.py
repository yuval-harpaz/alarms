import pandas as pd
import numpy as np
import os


local = '/home/innereye/alarms/'
os.chdir(local)
db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})
issues = pd.DataFrame(columns=['field', 'Hebrew', 'English', 'n'])
for columns in [['מקום האירוע','Event location'], ['מקום המוות','Death location']]:
    he = np.unique(db[columns[0]].astype(str).values)
    he = he[he != 'nan']
    for ii in range(len(he)):
        en = np.unique(db[columns[1]][db[columns[0]].astype(str).values == he[ii]].astype(str).values)
        if len(en) == 1:
            # check no nan
            if en[0] == 'nan':
                issues.loc[len(issues)] = [columns[0], he[ii], en[0], len(en)]
            else:
                # check if en is has any english characters
                has_english = any((ord(c) < 128) for c in en[0] if c.isalpha())
                if has_english:
                    print(f"'{he[ii][::-1]}':'{en[0]}',")
                    issues.loc[len(issues)] = [columns[0], he[ii], en[0], len(en)]
                else:
                    issues.loc[len(issues)] = [columns[0], he[ii], en[0], len(en)]
        else:
            issues.loc[len(issues)] = [columns[0], he[ii], '|'.join(en), len(en)]
issues.to_csv('~/Documents/location_translation_issues.csv', index=False)


##
dictionary = pd.read_csv('~/Documents/location_translation.csv')
keep = dictionary['field'].values == 'מקום האירוע'
for ii in np.where(~keep)[0]:
    if dictionary['Hebrew'][ii] not in dictionary['Hebrew'][keep].values:
        keep[ii] = True
        print(f"Adding {dictionary['Hebrew'][ii][::-1]}")
dictionary = dictionary[keep]
dictionary.to_csv('data/location_dictionary.csv', index=False)

## make sure english names fit the dictionary
dictionary = pd.read_csv('data/location_dictionary.csv')
db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})
for col in [['מקום האירוע','Event location'], ['מקום המוות','Death location']]:
    heb = db[col[0]].astype(str).values
    hebu = np.unique(heb)
    for ii in range(len(hebu)):
        if hebu[ii] not in dictionary['Hebrew'].values:
            print(f"Missing {hebu[ii][::-1]} in dictionary")
        else:
            en = dictionary['English'][dictionary['Hebrew'].values == hebu[ii]].values[0]
            index = np.where(heb == hebu[ii])[0]
            for jj in index:
                db.at[jj, col[1]] = en
db.to_csv('data/oct7database.csv', index=False)        