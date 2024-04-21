import os
import pandas as pd

##
local = '/home/innereye/alarms/'
os.chdir(local)
#
df = pd.read_csv('data/oct_7_9.csv')
fn = df['fullName'].values
for ii in range(len(fn)):
    split = fn[ii].split(' ')
    df.at[ii, 'last'] = split[0]
    df.at[ii, 'first'] = split[1]
    df.at[ii, 'middle'] = ''
    if len(split) > 2:
        df.at[ii, 'middle'] = ' '.join(split[2:])
df.to_excel('tmp_names.xlsx', index=False)
