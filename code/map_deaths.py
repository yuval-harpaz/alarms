import numpy as np
import requests
import pandas as pd
from html import unescape
import os
import numpy as np
local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True
df = pd.read_csv('data/deaths.csv')
coo = pd.read_csv('data/coord.csv')
locu = [x for x in df['from'] if type(x) == str]
found = np.zeros(len(df), bool)
c = 0
for loc in np.unique(df['from']):
    if np.any(coo['loc'] == loc):
        found[c] = True
    else:
        print(f'{loc} not found')


