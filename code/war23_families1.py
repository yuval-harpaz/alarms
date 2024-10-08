import os
import numpy as np
import pandas as pd
local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True

df = pd.read_csv('data/victims_relationship.csv')
vals = df.values[:, 8:15].astype(str)
vals[vals == 'nan'] = ''
relatives = []
size = []
for ii in range(vals.shape[0]):
    rel = []
    for jj in range(vals.shape[1]):
        rel.extend(vals[ii, jj].split(';'))
    rel = [int(x) for x in rel if len(x) > 0]
    relatives.append(rel)
    size.append(len(rel))
##
group = np.zeros(len(size), int)
cur = 0
for ii in range(len(size)):
    pid = df['pid'][ii]
    imember = np.where([pid in x for x in relatives])[0]
    if len(imember) > 0:
        grp = np.unique(group[imember])
        grp1 = [x for x in grp if x > 0]
        if len(grp1) == 0:  # new family
            cur += 1
            group[imember] = cur
            group[ii] = cur
        else:
            if len(grp1) != 1:
                raise Exception('too many groups')
            else:
                group[imember] = grp1[0]
                group[ii] = grp1[0]
    df['group'] = group
df.to_csv('~/Documents/families.csv', index=False)


##
ptn = df['partners'][~df['partners'].isnull()].values.astype(int)
ptn



