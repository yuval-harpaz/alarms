import pandas as pd
import numpy as np
import os


local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True
prev = pd.read_csv('data/alarms_by_date_and_distance.csv')
# prev = prev[(prev['origin'] != 'FA') & (prev['origin'] != 'Israel')]
# prev = prev.reset_index(drop=True)
# last_alarm = pd.to_datetime(prev['time'][len(prev)-1])
# last_alarm = last_alarm.tz_localize('Israel')

# date = np.array([d[:10] for d in prev['date']])
month = np.array([d[:7] for d in prev['date']])
monthu = np.unique(month)
# monthu = monthu[monthu >= ['2023-10']]
# now = np.datetime64('now', 'ns')
# nowisr = pd.to_datetime(now, utc=True, unit='s').astimezone(tz='Israel')
# nowstr = str(nowisr)[:16].replace('T', ' ')
##
# Make map
col = prev.columns[1:]
monthly = coo.copy()
df = pd.DataFrame(columns=prev.columns)
for imonth in range(len(monthu)):
    row = np.where(month == monthu[imonth])[0]
    data = [monthu[imonth]]
    for icol in range(len(col)):
        data.append(int(np.sum(prev[col[icol]].values[row])))
    df.loc[imonth] = data

df.to_excel('~/Documents/monthly_by_distance.xlsx', index=False)

df.to_csv('data/war23_alarms_by_month_and_distance.csv', index=False)
