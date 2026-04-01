import pandas as pd
import numpy as np   
import os

telegram = pd.read_excel('~/alarms/data/telegram_messages.xlsx', sheet_name='data')
dleshem = pd.read_csv('https://github.com/dleshem/israel-alerts-data/raw/refs/heads/main/israel-alerts.csv')
dleshem = dleshem[dleshem['alertDate'] > '2026-02-28']
dleshem.reset_index(drop=True, inplace=True)
timed = pd.to_datetime(dleshem['date'] + ' ' + dleshem['time'], dayfirst=True).values
timet = pd.to_datetime(telegram['message time']).values
telegram['rid'] = 0
telegram.at[0, 'rid'] = dleshem['rid'][0]
rowt = np.where(telegram['message id'] == 20978)[0][0]
rowd = np.where(dleshem['rid'] == 237230)[0][0]
telegram.at[rowt, 'rid'] = dleshem['rid'][rowd]
dleshem['telegram_id'] = 0
dleshem.at[0, 'telegram_id'] = telegram['message id'][0]
dleshem.at[rowd, 'telegram_id'] = telegram['message id'][rowt]
# fill message id in dleshem
for jj in range(rowd+1, len(dleshem)):
    near = np.abs(timet - timed[jj]) < np.timedelta64(10, 's')
    target_loc = dleshem['data'][jj]
    # Check for exact location match (as a complete element in semicolon-separated list)
    def has_exact_location(locs_str, target):
        if pd.isna(locs_str):
            return False
        locs = [l.strip() for l in str(locs_str).split(';')]
        return target in locs
    
    matches = telegram.apply(lambda row: has_exact_location(row['locations'], target_loc), axis=1)
    idxt = np.where(matches & near)[0]
    if len(idxt) == 1:
        dleshem.at[jj, 'telegram_id'] = telegram['message id'][idxt[0]]
    print(f'{jj}/{len(dleshem)}', end='\r')
dleshem.to_csv('~/alarms/data/dleshem_roar.csv', index=False)

print('now dleshem to telegram')
print('')
for ii in range(rowt+1, len(telegram)):
    near = np.abs(timed - timet[ii]) < np.timedelta64(10, 's')
    locations = [l.strip() for l in str(telegram['locations'][ii]).split(';')]
    # Match rows where ALL locations appear exactly in dleshem data
    matches = np.array([all(loc in dleshem['data'].values for loc in locations)])
    idxd = np.where(np.isin(dleshem['data'].values, locations) & near)[0]
    # Only assign if we found matches for all locations
    if len(idxd) > 0 and all(loc in dleshem['data'].values for loc in locations):
        telegram.at[ii, 'rid'] = ';'.join(dleshem['rid'][idxd].values.astype(str))
    # else:
    #     print('debug')
    print(f'{ii}/{len(telegram)}', end='\r')
telegram.to_csv('~/alarms/data/telegram_messages_roar.csv', index=False)