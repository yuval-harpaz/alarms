from matplotlib import colors
import pandas as pd
import numpy as np
import os

local = '/home/innereye/alarms/'
os.chdir(local)
islocal = True
df = pd.read_csv('data/alarms.csv')
date = [x[:10] for x in df['time'].values]
df = df[np.array(date) == '2023-10-07']
loc = np.unique(df['cities'])
count = []
for iloc in range(len(loc)):
    count.append(np.sum(df['cities'] == loc[iloc]))
df_count = pd.DataFrame(loc, columns=['loc'])
df_count['count'] = count
df_count = df_count.sort_values('count')