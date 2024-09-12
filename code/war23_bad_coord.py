import pandas as pd
import os
import numpy as np
local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True
    file = open('.txt')
    url = file.read().split('\n')[0]
    file.close()
map7 = pd.read_json(url)
##
data = pd.read_excel('~/Documents/oct7database.xlsx', 'Data')
data['revise'] = np.nan
for ii in np.where(~data['event_coordinates'].isnull())[0]:
    row = np.where(map7['pid'].values == data['pid'][ii])[0]
    if len(row) == 1:
        row = row[0]
        loc7 = map7['geotag'][row]
        if type(loc7) == str:
            loc = data['event_coordinates'][ii]
            if loc7 == loc and data['Event location class (oct7map)'][ii] == 'General vicinity':
                data.at[ii, 'revise'] = 'X'
data.to_csv('~/Documents/revise.csv', index=False)
