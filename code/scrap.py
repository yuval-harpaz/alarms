import pandas as pd
import numpy as np
import os
import json

dfm = pd.read_excel(os.path.expanduser('~/Documents/missing.xlsx'))
dfm = dfm[dfm['duplicate'].isnull()]
dfm.reset_index(inplace=True, drop=True)
dfm_time = pd.to_datetime(dfm['time']).values

df = pd.read_csv('data/alarms.csv')
df_time = pd.to_datetime(df['time'])
keep = []
for imiss in range(len(dfm)):
    delta = np.abs(df_time - dfm_time[imiss])
    isloc = np.array(df['cities'] == dfm['cities'][imiss].split(',')[0])
    iloc = np.where(isloc)[0]
    if len(iloc) == 0:
        print(f"Missing {imiss} {dfm['cities'][imiss]}")
        keep.append(False)
    else:
        imin = iloc[np.argmin(delta[isloc])]
        dmin = delta[imin]
        if dmin < np.timedelta64(2, 'm'):
            print(f"{imiss} {dfm['time'][imiss]} {dfm['cities'][imiss]} nearest: {dmin}")
            keep.append(False)
        else:
            keep.append(True)
dfk = dfm[np.array(keep)]
dfk.to_csv('~/Documents/missing_to_add.csv', index=False)
##
df = pd.read_csv('data/alarms.csv')
df_time = pd.to_datetime(df['time'])
dfk = pd.read_csv('~/Documents/missing_to_add.csv')
dfk_time = pd.to_datetime(dfk['time'])

rows_to_insert = []
for ii in range(len(dfk)):
    cities_str = dfk['cities'].iloc[ii]
    cities_list = [c.strip() for c in cities_str.split(',')]
    if len(cities_list) > 1 and 'אשדוד' not in cities_str:
        for city in cities_list:
            row = dfk.iloc[ii].copy()
            row['cities'] = city
            rows_to_insert.append(row)
    else:
        rows_to_insert.append(dfk.iloc[ii].copy())

for row in rows_to_insert:
    row = row.drop('duplicate', errors='ignore')
    row_time = pd.to_datetime(row['time'])
    if row_time > pd.Timestamp('2026-02-27') and row['threat'] == 0:
        row['origin'] = 'Iran'
    pos = np.searchsorted(df_time.values, row_time.to_datetime64(), side='right')
    row_df = pd.DataFrame([row])
    df = pd.concat([df.iloc[:pos], row_df, df.iloc[pos:]], ignore_index=True)
    df_time = pd.to_datetime(df['time'])

df.to_csv('data/alarms.csv', index=False)
print(f"Inserted {len(rows_to_insert)} rows")


dftest = pd.read_csv('data/alarms.csv')
dftest = dftest[dftest['time'] > '2026-02-28']
n = np.sum(dftest['cities'] == 'גן יבנה')
print(n)