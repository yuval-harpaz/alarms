"""Set front for DB based on IDF front (Lebanon + North >> North etc)."""
import pandas as pd
# import Levenshtein
# import requests
import os
import numpy as np

local = '/home/innereye/alarms/'
# islocal = False
if os.path.isdir(local):
    os.chdir(local)
    local = True

idf = pd.read_csv('data/deaths_idf.csv')
idf_pid = idf['pid'].values
front = pd.read_csv('data/front.csv')
map79 = pd.read_csv('data/oct_7_9.csv')
map_pid = map79['pid'].values

db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})
idx = np.where(db['front'].isnull())[0]
if len(idx) == 0:
    print('front column full')
else:
    for ii in idx:
        if db['pid'][ii] in map_pid:
            db.at[ii, 'front'] = 'Gaza'
        elif db['pid'][ii] in idf_pid:
            row = np.where(idf_pid == db['pid'][ii])[0][0]
            frt = front['front'][row]
            if str(frt) == 'nan':
                db.at[ii, 'front'] = 'Other'
            elif 'עזה' in frt:
                db.at[ii, 'front'] = 'Gaza'
            elif frt == 'צפון' or 'לבנון' in frt:
                db.at[ii, 'front'] = 'North'
            elif frt == 'עורף':
                db.at[ii, 'front'] = 'Home'
            elif frt == 'יו"ש':
                db.at[ii, 'front'] = 'West Bank'
            elif frt == 'תאונה':
                db.at[ii, 'front'] = 'Accident'
            elif frt == 'נרצח כאזרח':
                db.at[ii, 'front'] = 'Other'
            else:
                raise Exception(f"not supposed to be {frt}")
        elif 'kidnapped' in db['Status'][ii]:
            db.at[ii, 'front'] = 'Gaza'
        else:
            db.at[ii, 'front'] = 'Other'
    db.to_csv('data/oct7database.csv', index=False)
    ## verify against ynet
    db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})
    ynet = pd.read_csv('data/ynetlist.csv')
    ynet_pid = ynet['pid'].values
    ignore = [2035, 2106]
    for ii in range(len(db)):
        if db['pid'][ii] in ynet_pid and db['pid'][ii] not in ignore:
            row = np.where(ynet_pid == db['pid'][ii])[0][0]
            yft = ynet['סיווג'][row]
            if type(yft) == str:
                if 'כה ביו' in yft:
                    if db['front'][ii] != 'West Bank':
                        print(f"{ynet['שם פרטי'][row]} {ynet['שם משפחה'][row]} pid {db['pid'][ii]} should be West Bank")
                if 'צפון' in yft:
                    if db['front'][ii] != 'North':
                        print(f"{ynet['שם פרטי'][row]} {ynet['שם משפחה'][row]} pid {db['pid'][ii]} should be North")
                if 'עזה' in yft:
                    if db['front'][ii] != 'Gaza':
                        print(f"{ynet['שם פרטי'][row]} {ynet['שם משפחה'][row]} pid {db['pid'][ii]} should be Gaza")
