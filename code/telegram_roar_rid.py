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
    contains_r = telegram['locations'].str.contains('; ' + dleshem['data'][jj])
    contains_l = telegram['locations'].str.contains(dleshem['data'][jj] + '; ')
    equal = telegram['locations'] == dleshem['data'][jj]
    idxt = np.where((contains_r | contains_l | equal) & near)[0]
    if len(idxt) == 1:
        dleshem.at[jj, 'telegram_id'] = telegram['message id'][idxt[0]]
    print(f'{jj}/{len(dleshem)}', end='\r')
dleshem.to_csv('~/alarms/data/dleshem_roar.csv', index=False)

print('now dleshem to telegram')
print('')
for ii in range(rowt+1, len(telegram)):
    near = np.abs(timed - timet[ii]) < np.timedelta64(10, 's')
    locations = telegram['locations'][ii].split('; ')
    idxd = np.where(dleshem['data'].isin(locations) & near)[0]
    if len(idxd) == len(locations):
        telegram.at[ii, 'rid'] = ';'.join(dleshem['rid'][idxd].values.astype(str))
    # else:
    #     print('debug')
    print(f'{ii}/{len(telegram)}', end='\r')
telegram.to_csv('~/alarms/data/telegram_messages_roar.csv', index=False)