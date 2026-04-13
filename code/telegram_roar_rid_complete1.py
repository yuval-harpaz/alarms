import pandas as pd
import numpy as np   
import os

# telegram = pd.read_excel('~/alarms/data/telegram_messages.xlsx', sheet_name='data')
telegram = pd.read_csv('~/alarms/data/telegram_messages.csv')
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

def has_exact_location(locs_str, target):
    if pd.isna(locs_str):
        return False
    locs = [l.strip() for l in str(locs_str).split(';')]
    return target in locs

def make_type_match(cat, t_type_series, t_msg_series):
    """Return boolean mask: telegram row matches a given dleshem category_desc.
    Handles direct type match (rockets/UAV), exact message match (מבזק/עדכון),
    and compound category_desc like 'ירי רקטות וטילים - האירוע הסתיים'."""
    msg_s = t_msg_series.str.strip()
    mask = (t_type_series == cat) | (msg_s == cat)
    mask = mask | msg_s.apply(lambda m: len(str(m)) > 5 and str(m) in cat)
    return mask

missing = np.where(dleshem['telegram_id'].astype(int) == 0)[0]
missing = missing[missing > 100]
# missing = [m for m in missing if m-1 not in missing or m+1 not in missing]
for jj in missing:
    if jj > missing[0] and dleshem['telegram_id'][prev] == 0:
        prev = jj
        continue
    prev = jj
    near = np.abs(timet - timed[jj]) < np.timedelta64(60, 's')
    tomatch = dleshem['data'][jj]
    tomatch = tomatch.split(', ')[0]
    cat = dleshem['category_desc'][jj]
    type_match = make_type_match(cat, telegram['type'], telegram['message'])

    # Check for exact location match (as a complete element in semicolon-separated list)

    # matches = telegram.apply(lambda row: has_exact_location(row['locations'], target_loc.split(', ')[0]), axis=1)
    matches = telegram.apply(lambda row: has_exact_location(row['locations'], tomatch), axis=1)
    idxt = np.where(matches & near & type_match)[0]
    if len(idxt) > 0:
        dleshem.at[jj, 'telegram_id'] = telegram['message id'][idxt[0]]
    else:
        # For fallback matching, also use exact location matching with type filter
        fallback_matches = telegram.apply(lambda row: has_exact_location(row['locations'], tomatch), axis=1)
        prev_idx = np.where(fallback_matches & type_match & (timet < timed[jj]))[0]
        next_idx = np.where(fallback_matches & type_match & (timet > timed[jj]))[0]
        
        if len(prev_idx) > 0:
            prev = prev_idx[-1]
            prev_time = timed[jj] - timet[prev]
            if len(next_idx) > 0:
                next = next_idx[0]
                next_time = timet[next] - timed[jj]
            else:
                next_time = np.timedelta64(10**18, 's')
        else:
            prev_time = np.timedelta64(10**18, 's')
            if len(next_idx) > 0:
                next = next_idx[0]
                next_time = timet[next] - timed[jj]
            else:
                next_time = np.timedelta64(10**18, 's')

        if prev_time < np.timedelta64(60, 's'):
            dleshem.at[jj, 'telegram_id'] = telegram['message id'][prev]
        elif next_time < np.timedelta64(60, 's'):
            dleshem.at[jj, 'telegram_id'] = telegram['message id'][next]
        else:
            if prev_time != np.timedelta64(10**18, 's'):
                print(f"prev {prev_time.astype('timedelta64[s]')} sec before, next {next_time.astype('timedelta64[s]')} sec after")
            print('no match < 60 sec')
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

## big mess from rid 352386
group_fix = [[268913, 268952, 21862],
             [314936, 315025, 22526],
             [315082, 315095, 22526],
             [355995, 356009, 23788]]

##
# telegram = pd.read_csv('~/alarms/data/telegram_messages.csv')
# dleshem = pd.read_csv('~/alarms/data/dleshem_roar.csv')
# imissed = np.where(dleshem['telegram_id'] == 0)[0]
# imissed = imissed[imissed > 100]
# imissed = imissed[imissed < 298800]
# ii = 0
# missed_locations = dleshem['data'][imissed[ii]]
# sus_message = telegram['locations'][telegram['message id'] == dleshem['telegram_id'][imissed[ii]-1]]

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