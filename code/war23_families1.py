"""Find groups of family members.

run this code (war23_families1.py), then war23_families_summary.py then then
war23_families_comments.py. then python code/war23_db_tests.py r.
"""
import os
import numpy as np
import pandas as pd
local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True

df = pd.read_csv('data/victims_relationship.csv')
val0 = np.where(df.columns == 'partners')[0][0]
val1 = np.where(df.columns == 'other')[0][0]
vals = df.values[:, val0:val1+1].astype(str)
vals[vals == 'nan'] = ''
relatives = []
size = []
for ii in range(vals.shape[0]):
    rel = []
    for jj in range(vals.shape[1]):
        rel.extend(vals[ii, jj].split(';'))
    rel = [int(float(x)) for x in rel if len(x) > 0]
    relatives.append(rel)
    size.append(len(rel))
##
group_prev = df['group'].values
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
    if group[ii] != group_prev[ii]:
        print(f" not same for {ii}")
df['group'] = group
df.to_csv('~/Documents/families.csv', index=False)
## Complete data
df = pd.read_csv('~/Documents/families.csv')
val0 = np.where(df.columns == 'partners')[0][0]
db = pd.read_csv('data/oct7database.csv')
dbcolumns = ['Residence', 'מקום האירוע', 'Event date', 'Status']
dfcolumns = ['residence', 'event location', 'event date', 'status']
for ii in range(len(df)):
    row = np.where(db['pid'].values == df['pid'][ii])[0][0]
    eng_name = f"{db['first name'][row]} {db['last name'][row]}"
    if df['eng name'][ii] != eng_name:
        df.at[ii, 'eng name'] = eng_name
    name = f"{db['שם פרטי'][row]} {db['שם משפחה'][row]}"
    if df['name'][ii] != name:
        df.at[ii, 'name'] = name
    for icol, col in enumerate(dbcolumns):
        if df[dfcolumns[icol]][ii] != db[col][row]:
            df.at[ii, dfcolumns[icol]] = db[col][row]
df.sort_values(['group', 'name'], inplace=True, ignore_index=True)
df.to_csv('~/Documents/families.csv', index=False)
df.to_excel('~/Documents/families.xlsx', index=False)

##

df.to_csv('data/victims_relationship.csv', index=False)
# ptn = df['partners'][~df['partners'].isnull()].values.astype(int)
# ptn
df = pd.read_csv('data/victims_relationship.csv')
db = pd.read_csv('data/oct7database.csv')
df_heb = df.copy()
df_eng = df.copy()
for ii in range(len(df)):
    row = np.where(db['pid'].values == df['pid'][ii])[0][0]
    eng_name = f"{db['first name'][row]} {db['last name'][row]}"
    name = f"{db['שם פרטי'][row]} {db['שם משפחה'][row]}"
    if df['name'][ii] != name:
        df.at[ii, 'name'] = name
    for icol, col in enumerate(dbcolumns):
        if df[dfcolumns[icol]][ii] != db[col][row]:
            df.at[ii, dfcolumns[icol]] = db[col][row]

