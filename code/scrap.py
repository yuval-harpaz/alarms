import pandas as pd
import os
import numpy as np
import sys
# sys.path.append('code')

## check haaretz
haa0 = pd.read_csv('data/deaths_haaretz.csv')
haa1 = pd.read_csv('data/deaths_haaretz+.csv')
# db = pd.read_csv('data/oct7database.csv')
# map79 = pd.read_csv('data/oct_7_9.csv')
# young = np.where((db['Age'] < 19) & db['Status'].str.contains('killed'))[0]
# pids = db['pid'].values[young]
names1 = haa1['name'].values
names0 = haa0['name'].values
for ii in range(len(names0)):
    for jj in range(len(names1)):
        found = False
        if names1[jj] in names0[ii]:
            found = True
            break
    if not found:
        print(', '.join(haa0.loc[ii].values.astype(str)))
    # if not any(haa0['name'].str.contains(names1[ii])):
    #     print(', '.join(haa1.loc[ii].values.astype(str)))
        
            

