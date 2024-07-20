import pandas as pd
import os
import numpy as np
# import re
local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True
    file = open('.txt')
    url = file.read().split('\n')[0]
    file.close()
map7 = pd.read_json(url)
db = pd.read_csv('data/oct7database.csv')
pid = map7['pid'].values
##
for ii in range(len(db)):
    row = np.where(pid == db['pid'][ii])[0]
    if len(row) == 1:
        row = row[0]
        loc = db['Event location (oct7map)'][ii]
        loc7 = map7['location'][row]
        subloc7 = map7['sublocation'][row]
        if subloc7:
            loc7 = loc7 + '; ' + subloc7
        if loc != loc7:
            issue = f"DB: {loc}, map7:{loc7}"
            print(issue)
            db.at[ii, 'Event location (oct7map)'] = loc7
        clas = db['Event location class (oct7map)'][ii]
        clas7 = map7['location_class'][row]
        if clas != clas7:
            issue = f"DB: {clas}, map7:{clas7}"
            print(issue)
            db.at[ii, 'Event location class (oct7map)'] = clas7
        stat = db['Status (oct7map)'][ii]
        stat7 = map7['status'][row]
        if stat != stat7:
            issue = f"DB: {stat}, map7:{stat7}"
            print(issue)
            db.at[ii, 'Status (oct7map)'] = stat7
    # locstr = str(db['Event location (oct7map)'][ii])
    # if ord(locstr[0]) > 1487:
    #     db.at[ii, 'Event location (oct7map)'] = np.nan
db.to_csv('data/oct7database.csv', index=False)
