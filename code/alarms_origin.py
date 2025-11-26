import re
from matplotlib import colors
import folium
import pandas as pd
import numpy as np
import os
from ellipse_fit import guess_yemen, guess_iran



local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True
coo = pd.read_csv('data/coord.csv')

def guess_origin(df_toguess):
    okcat = (df_toguess['description'].values == 'ירי רקטות וטילים') | \
            (df_toguess['description'].values == 'חדירת כלי טיס עוין')
    toguess = df_toguess['origin'].isnull().values & okcat
    row_lat = np.array([coo['lat'][coo['loc'] == x].values[0] for x in df_toguess['cities'].values])
    row_long = np.array([coo['long'][coo['loc'] == x].values[0] for x in df_toguess['cities'].values])
    # syria = toguess & (row_long > 35.63) & (row_lat < 33.1)
    lebanon = toguess & (row_lat > 32.5)
    yemen = toguess & (row_lat < 30)
    gaza = toguess & (row_lat < 31.7) & (row_long < 34.7)
    origin = df_toguess['origin'].values
    origin[gaza] = 'Gaza'
    origin[lebanon] = 'Lebanon'
    # origin[syria] = 'Syria'
    # origin[syria] = 'Iraq'  # Golan hit by Lebanon nowadays
    origin[yemen] = 'Yemen'
    df_toguess['origin'] = origin
    return df_toguess


dfwar = pd.read_csv('data/alarms.csv')
dfwar = guess_yemen(dfwar, coo)
dfwar = guess_iran(dfwar)
dfwar = guess_origin(dfwar)
dfwar.to_csv('data/alarms.csv', index=False, sep=',')
# last_alarm = pd.to_datetime(dfwar['time'][len(dfwar)-1])
# last_alarm = last_alarm.tz_localize('Israel')

print('done origin')
