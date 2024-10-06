import pandas as pd
import os
import numpy as np
import sys
# sys.path.append('code')


db = pd.read_csv('data/oct7database.csv')
map79 = pd.read_csv('data/oct_7_9.csv')
young = np.where((db['Age'] < 19) & db['Status'].str.contains('killed'))[0]
pids = db['pid'].values[young]
for ii in range(len(db)):
    row = np.where(map79['pid'].values == pids[ii])[0]
    if len(row) == 0:
        print(f"not found: {db['שם פרטי'][young[ii]]} {db['שם משפחה'][young[ii]]}")
    else:
        age0 = db['Age'][young[ii]]
        age1 = map79['age'][row[0]]
        if age0 != age1:
            print(f"age issue for {pids[ii]} {map79['fullName'][row[0]]}")
            

