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
    # substring: telegram message text is contained in dleshem category_desc
    # (e.g. 'האירוע הסתיים' in 'ירי רקטות וטילים - האירוע הסתיים')
    mask = mask | msg_s.apply(lambda m: len(str(m)) > 5 and str(m) in cat)
    return mask

# fill message id in dleshem
for jj in range(rowd+1, len(dleshem)):
    near = np.abs(timet - timed[jj]) < np.timedelta64(10, 's')
    target_loc = dleshem['data'][jj]
    cat = dleshem['category_desc'][jj]
    type_match = make_type_match(cat, telegram['type'], telegram['message'])
    # Check for exact location match (as a complete element in semicolon-separated list)
    matches = telegram.apply(lambda row: has_exact_location(row['locations'], target_loc), axis=1)
    if not (matches & type_match).any():  # look for cases with ", " such as חיפה - כרמל, הדר ועיר תחתית
        matches = telegram.apply(lambda row: has_exact_location(row['locations'], target_loc.split(', ')[0]), axis=1)
    idxt = np.where(matches & near & type_match)[0]
    if len(idxt) == 1:
        dleshem.at[jj, 'telegram_id'] = telegram['message id'][idxt[0]]
    print(f'{jj}/{len(dleshem)}', end='\r')
dleshem.to_csv('~/alarms/data/dleshem_roar.csv', index=False)

print('now dleshem to telegram')
print('')
for ii in range(rowt+1, len(telegram)):
    near = np.abs(timed - timet[ii]) < np.timedelta64(10, 's')
    locations = [l.strip() for l in str(telegram['locations'][ii]).split(';')]
    msg_type = telegram['type'][ii]
    msg_text = str(telegram['message'][ii]).strip()
    # match dleshem rows whose category_desc equals type, equals message text,
    # or contains the message text (e.g. 'האירוע הסתיים' in 'ירי רקטות וטילים - האירוע הסתיים')
    type_mask = ((dleshem['category_desc'].values == msg_type) |
                 (dleshem['category_desc'].values == msg_text) |
                 (len(msg_text) > 5 and np.array([msg_text in c for c in dleshem['category_desc'].values])))
    # Match rows where ALL locations appear exactly in dleshem data with matching type
    idxd = np.where(np.isin(dleshem['data'].values, locations) & near & type_mask)[0]
    # Only assign if we found matches for all locations with the correct type
    if len(idxd) > 0 and all(loc in dleshem['data'].values[type_mask] for loc in locations):
        telegram.at[ii, 'rid'] = ';'.join(dleshem['rid'][idxd].values.astype(str))
    # else:
    #     print('debug')
    print(f'{ii}/{len(telegram)}', end='\r')
telegram.to_csv('~/alarms/data/telegram_messages_roar.csv', index=False)