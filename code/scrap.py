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

for imiss in range(len(dfm)):
    delta = np.abs(df_time - dfm_time[imiss])
    isloc = np.array(df['cities'] == dfm['cities'][imiss].split(',')[0])
    iloc = np.where(isloc)[0]
    if len(iloc) == 0:
        print(f"Missing {imiss} {dfm['cities'][imiss]}")
    else:
        imin = iloc[np.argmin(delta[isloc])]
        dmin = delta[imin]
        if dmin < np.timedelta64(3, 'm'):
            print(f"{imiss} {dfm['time'][imiss]} {dfm['cities'][imiss]} nearest: {dmin}")
