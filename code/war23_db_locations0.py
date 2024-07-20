import pandas as pd
from selenium import webdriver
import os
from pyvirtualdisplay import Display
import time
import numpy as np

local = '/home/innereye/alarms/'


if os.path.isdir(local):
    os.chdir(local)
    local = True
    file = open('.txt')
    url = file.read().split('\n')[0]
    file.close()
map7 = pd.read_json(url)
## first from json
df = pd.read_csv('data/oct7database.csv')
pid = map7['pid'].values
for ii in range(len(df)):
    row = np.where(pid == df['pid'][ii])[0]
    if len(row) > 1:
        raise Exception('too many rows for pid ' + str(df['pid'][ii]))
    elif len(row) == 1:
        loc = map7['location'][row[0]]
        subloc = map7['sublocation'][row[0]]
        if type(subloc) == str:
            loc = loc+'; '+subloc
        df.at[ii, 'event_location'] = loc
        df.at[ii, 'event_location_class'] = map7['location_class'][row[0]]
        coo = map7['geotag'][row[0]]
        if type(coo) == str and coo[:3] == '31.':
            df.at[ii, 'event_coordinates'] = coo
    else:
        pass  # new cases not in map

##
map = pd.read_csv('data/oct_7_9.csv')
coo79 = pd.read_csv('data/deaths_by_loc.csv')
pid = map['pid'].values
for ii in np.where(df['event_location'].isnull())[0]:
    row = np.where(pid == df['pid'][ii])[0]
    if len(row) > 1:
        raise Exception('too many rows for pid ' + str(df['pid'][ii]))
    elif len(row) == 1:
        loc_heb = map['location'][row[0]]
        rowcoo = np.where(coo79['name'] == loc_heb)[0]
        if len(rowcoo) == 1:
            loc = coo79['eng'][rowcoo[0]].replace('Kibbutz ', '')
            df.at[ii, 'event_location'] = loc
            df.at[ii, 'event_location_class'] = 'oct_7_9'
            coo = f"{coo79['lat'][rowcoo[0]]}, {coo79['long'][rowcoo[0]]}"
            df.at[ii, 'event_coordinates'] = coo
    else:
        pass  # new cases not in map


## IDF
idf = pd.read_csv('/home/innereye/Downloads/deaths_IDF - Data.csv')
pid = idf['pid'].values
for ii in np.where(df['event_location'].isnull())[0]:
    row = np.where(pid == df['pid'][ii])[0]
    if len(row) > 1:
        raise Exception('too many rows for pid ' + str(df['pid'][ii]))
    elif len(row) == 1:
        loc_heb = idf['front'][row[0]]
        if loc_heb == 'עזה':
            loc_heb = 'רצועת עזה'
            region = idf['region'][row[0]]
            if region in ['צפון', 'מרכז', 'דרום']:
                loc_heb = region + ' ' + loc_heb
        elif loc_heb == 'לבנון':
            loc_heb = 'גבול לבנון'
        df.at[ii, 'event_location'] = loc_heb
        df.at[ii, 'event_location_class'] = 'idf'
    else:
        pass

df.to_csv('data/oct7database.csv', index=False)