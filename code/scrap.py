import pandas as pd
import os
import numpy as np
import sys
sys.path.append('code')
from map_deaths_name_search import group_locs
local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    local = True


db = pd.read_csv('data/oct7database.csv')
prev = pd.read_csv('~/Documents/oct7database.csv')
dbn = db.to_numpy()
prevn = prev.to_numpy()

for ii in range(len(db)):
    changes = False
    for jj in range(len(db.columns)):
        if str(dbn[ii, jj]) != str(prevn[ii, jj]):
            print(' '.join(dbn[ii, 0:3].astype(str)), end=': ')
            print(f"{db.columns[jj]} {prevn[ii,jj]} >> {dbn[ii,jj]}")

