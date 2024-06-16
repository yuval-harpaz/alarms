import pandas as pd
import os
import numpy as np

local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True
map7 = pd.read_json('https://service-f5qeuerhaa-ey.a.run.app/api/individuals')
## first from json
df = pd.read_csv('data/oct7database.csv')
pid = map7['pid'].values
for ii in range(len(df)):
    row = np.where(pid == df['pid'][ii])[0]
    if len(row) > 1:
        raise Exception('too many rows for pid ' + str(df['pid'][ii]))
    elif len(row) == 1:
        df.at[ii, 'gender'] = map7['gender'][row[0]]
        status = map7['status'][row[0]]
        df.at[ii, 'status'] = status
        if 'Kidnap' in status or 'captivity' in status:
            df.at[ii, 'event_date'] = '2023-10-07'
df.to_csv('/home/innereye/Documents/db_tmp.csv', index=False)
##
df = pd.read_csv('/home/innereye/Documents/db_tmp.csv')
map = pd.read_csv('data/oct_7_9.csv')
gender = map['sex'].copy()
gender[gender.str.contains('ה')] = 'F'
gender[gender != 'F'] = 'M'
gender = gender.values
pid = map['pid'].values
df['death_date'] = df['event_date']
for ii in range(len(df)):
    if type(df['status'][ii]) == str and 'Kidnap' in df['status'][ii]:
         df.at[ii, 'death_date'] = np.nan
for ii in range(len(df)):
    row = np.where(pid == df['pid'][ii])[0]
    if len(row) > 1:
        raise Exception('too many rows for pid ' + str(df['pid'][ii]))
    elif len(row) == 1:
        if type(df['gender'][ii]) != str:
            df.at[ii, 'gender'] = gender[row[0]]
        if type(df['event_date'][ii]) != str:
            date = map['date'][row[0]]
            date = date[6:]+'-'+date[3:5]+'-'+date[:2]
            df.at[ii, 'event_date'] = date
            df.at[ii, 'death_date'] = date
        if type(df['status'][ii]) != str:
            df.at[ii, 'status'] = map['citizenGroup'][row[0]]
df.to_csv('/home/innereye/Documents/db_tmp.csv', index=False)
##
df = pd.read_csv('/home/innereye/Documents/db_tmp.csv')
idf = pd.read_csv('data/deaths_idf.csv')
pid = idf['pid'].values
for ii in range(len(df)):
    row = np.where(pid == df['pid'][ii])[0]
    if len(row) > 1:
        raise Exception('too many rows for pid ' + str(df['pid'][ii]))
    elif len(row) == 1:
        if type(df['gender'][ii]) != str:
            df.at[ii, 'gender'] = idf['gender'][row[0]]
        if type(df['event_date'][ii]) != str:
            date = idf['death_date'][row[0]]
            df.at[ii, 'death_date'] = date
            story = idf['story'][row[0]]
            if 'פצע' not in story and 'נפטר' not in story:
                df.at[ii, 'event_date'] = date
        df.at[ii, 'status'] = 'Killed on duty'
df.to_csv('/home/innereye/Documents/db_tmp.csv', index=False)


##
