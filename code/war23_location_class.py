"""fill location class for db."""
import pandas as pd
import os
import numpy as np

local = '/home/innereye/alarms/'
# islocal = False
if os.path.isdir(local):
    os.chdir(local)
    local = True
db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str, 'Event location class': str, 'Death location class': str})
oct7 = pd.read_csv('~/Documents/oct7map.csv')
dbcoo = pd.read_excel('~/Documents/oct7database.xlsx', 'Data', dtype={'הספריה הלאומית': str})
issues = pd.read_csv('~/Documents/missing.csv')
## first swipe, only identical coordinates
for ii in range(len(db)):
    if str(db['Death location class'][ii]) == 'nan':
        lookup = db['pid'][ii]
        if lookup in issues['oct7database'].values:
            lookup = issues['oct7map'][issues['oct7database'] == lookup].values[0]
        row = np.where(oct7['pid'].values == lookup)[0]
        if len(row) == 1:
            row = row[0]
            oct7class = oct7['location_class'][row]
            oct7coo = oct7['geotag'][row]
            if type(oct7class) != str:
                print(oct7coo)
                break
            if str(oct7coo)[0] == '3':
                coo = dbcoo['death_coordinates'][ii]
                if coo == oct7coo:
                    db.at[ii, 'Event location class'] = oct7class
                    db.at[ii, 'match'] = 'same coordinates'
                    if db['Status'][ii].split(';')[0] == 'killed':
                        db.at[ii, 'Death location class'] = oct7class
                else:
                    coo = dbcoo['event_coordinates'][ii]
                    if coo == oct7coo:
                        db.at[ii, 'Event location class'] = oct7class
                        db.at[ii, 'match'] = 'same coordinates'
                        if db['Status'][ii].split(';')[0] == 'killed':
                            db.at[ii, 'Death location class'] = oct7class
                        
db.to_csv('~/Documents/oct7database_location_class.csv', index=False)
## after export_coordinates1.py, zero or very small difference
exp = pd.read_csv('~/Documents/locations.csv')
ievent = np.where(~dbcoo['event_coordinates'].isnull())[0]
for ii in ievent:
    if str(db['Death location class'][ii]) == 'nan':
        lookup = db['pid'][ii]
        if lookup in issues['oct7database'].values:
            lookup = issues['oct7map'][issues['oct7database'] == lookup].values[0]
        row = np.where(oct7['pid'].values == lookup)[0]
        diff = exp['personal - map7'][ii]
        if str(diff) != 'nan':
            mtch = False
            if diff == 0:
                mtch = True
                db.at[ii, 'match'] = 'diff 0'
            elif diff <= 0.1:
                mtch = True
                db.at[ii, 'match'] = 'diff < 0.1'
            if mtch:
                if db['Status'][ii].split(';')[0] == 'kidnapped':
                    db.at[ii, 'Event location class'] = oct7['location_class'][row].values[0]
                else:
                    db.at[ii, 'Death location class'] = oct7['location_class'][row].values[0]
                    if db['מקום האירוע'][ii] == db['מקום המוות'][ii]:
                        db.at[ii, 'Event location class'] = oct7['location_class'][row].values[0]
            # print(f"{exp['name'][ii]}: {np.round(diff,1)}")
db.to_csv('~/Documents/oct7database_location_class.csv', index=False)



## same sublocation
sublocu = np.unique([l for l in exp['oct7map loc'].astype(str).values if ';' in l])
# sldb = []
# for sl in sublocu:
#     # sldb.append(exp['event loc'][exp['oct7map loc'].astype(str) == sl].values[0])
#     #find the common sublocation in the db
#     candidates = exp['event loc'][exp['oct7map loc'].astype(str) == sl].values
#     counter = []
#     for cand in np.unique(candidates):
#         counter.append(len(candidates[candidates == cand]))
#     common = np.unique(candidates)[np.argmax(counter)]
#     sldb.append(common)
# converter  = pd.DataFrame({'sublocation': sublocu, 'sublocation db': sldb})
# converter.to_csv('~/Documents/sublocation_converter.csv', index=False, sep=',')
converter = pd.read_csv('~/Documents/sublocation_converter.csv')
#dict from df
conv = dict(zip(converter['sublocation'], converter['sublocation db']))
still_missing = np.where(db['Death location class'].isnull())[0]
still_missing = still_missing[still_missing < len(exp)]  # exp may be shorter than db
for ii in still_missing:
    if ';' in str(exp['oct7map loc'][ii]):
        if conv[exp['oct7map loc'][ii]] == exp['event loc'][ii] or \
           conv[exp['oct7map loc'][ii]] == exp['death loc'][ii]:
            lookup = db['pid'][ii]
            if lookup in issues['oct7database'].values:
                lookup = issues['oct7map'][issues['oct7database'] == lookup].values[0]
            row = np.where(oct7['pid'].values == lookup)[0]
            db.at[ii, 'Death location class'] = oct7['location_class'][row].values[0]
            if db['Event location'][ii] == db['Death location'][ii]:
                db.at[ii, 'Event location class'] = oct7['location_class'][row].values[0]
            db.at[ii, 'match'] = 'same sublocation'
db.to_csv('~/Documents/oct7database_location_class.csv', index=False)
db.to_excel('~/Documents/oct7database_location_class.xlsx', index=False)