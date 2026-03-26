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
# dleshem['telegram_id'] = 0
# dleshem.at[0, 'telegram_id'] = telegram['message id'][0]
# dleshem.at[rowd, 'telegram_id'] = telegram['message id'][rowt]
dleshem = pd.read_csv('~/alarms/data/dleshem_roar.csv')
# fill message id in dleshem
missing = np.where(dleshem['telegram_id'] == 0)[0]
missing = missing[missing > 100]
for jj in missing:
    near = np.abs(timet - timed[jj]) < np.timedelta64(10, 's')
    tomatch = dleshem['data'][jj]
    tomatch = tomatch.replace(',', ';')
    contains_r = telegram['locations'].str.contains('; ' + tomatch)
    contains_l = telegram['locations'].str.contains(tomatch + '; ')
    equal = telegram['locations'] == tomatch
    idxt = np.where((contains_r | contains_l | equal) & near)[0]
    if len(idxt) > 0:
        dleshem.at[jj, 'telegram_id'] = telegram['message id'][idxt[0]]
    else:
        prev = np.where(telegram['locations'].str.contains(tomatch) & (timet < timed[jj]))[0][-1]
        prev_time = timed[jj] - timet[prev]
        next = np.where(telegram['locations'].str.contains(tomatch) & (timet > timed[jj]))[0][0]
        next_time = timet[next] - timed[jj]
        # print times in seconds

        if prev_time < np.timedelta64(30, 's'):
            dleshem.at[jj, 'telegram_id'] = telegram['message id'][prev]
        elif next_time < np.timedelta64(30, 's'):
            dleshem.at[jj, 'telegram_id'] = telegram['message id'][next]
        else:
            print(f"prev {prev_time.astype('timedelta64[s]')} sec before, next {next_time.astype('timedelta64[s]')} sec after")
            print('no match < 30 sec')
        # for kk in np.where(near):
        #     if tomatch in telegram['locations'][kk]:
        #         print(kk)
    print(f'{jj}/{len(dleshem)}', end='\r')
dleshem.to_csv('~/alarms/data/dleshem_roar.csv', index=False)
##
matched = np.unique(dleshem['telegram_id'].values)[1:]
missed = telegram['message id'].values[~np.isin(telegram['message id'].values, matched)]
##
dleshem = pd.read_csv('~/alarms/data/dleshem_roar.csv')
for ii in range(len(telegram)):
    rid = dleshem['rid'][dleshem['telegram_id'] == telegram['message id'][ii]]
    if len(rid) > 0:
        telegram.at[ii, 'rid'] = '; '.join(rid.values.astype(str))
telegram.to_csv('~/alarms/data/telegram_messages.csv', index=False)

##
telegram = pd.read_csv('~/alarms/data/telegram_messages.csv')
dleshem = pd.read_csv('~/alarms/data/dleshem_roar.csv')
imissed = np.where(dleshem['telegram_id'] == 0)[0]
imissed = imissed[imissed > 100]
imissed = imissed[imissed < 298800]
ii = 0
missed_locations = dleshem['data'][imissed[ii]]
sus_message = telegram['locations'][telegram['message id'] == dleshem['telegram_id'][imissed[ii]-1]]

#
# print('now dleshem to telegram')
# print('')
# for ii in range(rowt+1, len(telegram)):
#     near = np.abs(timed - timet[ii]) < np.timedelta64(10, 's')
#     locations = telegram['locations'][ii].split('; ')
#     idxd = np.where(dleshem['data'].isin(locations) & near)[0]
#     if len(idxd) == len(locations):
#         telegram.at[ii, 'rid'] = ';'.join(dleshem['rid'][idxd].values.astype(str))
#     # else:
#     #     print('debug')
#     print(f'{ii}/{len(telegram)}', end='\r')
# telegram.to_csv('~/alarms/data/telegram_messages_roar.csv', index=False)