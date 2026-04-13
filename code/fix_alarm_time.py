import os
import pandas as pd

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

alarms_path = 'data/alarms.csv'
ref_path = os.path.expanduser('~/Documents/israel-alerts.csv.1')

dfa = pd.read_csv(alarms_path)
dfi = pd.read_csv(ref_path)

# Build a lookup: rid -> first datetime string in YYYY-MM-DD HH:MM:SS format
# dfi date is DD.MM.YYYY, time is HH:MM:SS
dfi_first = dfi.drop_duplicates(subset='rid', keep='first').copy()
dfi_first['datetime_fixed'] = pd.to_datetime(
    dfi_first['date'] + ' ' + dfi_first['time'], dayfirst=True
).dt.strftime('%Y-%m-%d %H:%M:%S')
# Use int keys to avoid float/int mismatch in dict lookup
rid_to_time = {int(k): v for k, v in dfi_first.set_index('rid')['datetime_fixed'].items()}

# Apply fix: update 'time' for rows whose rid has a match in the reference file
mask = dfa['rid'].notna() & dfa['rid'].isin(rid_to_time)
n_fixed = mask.sum()
dfa.loc[mask, 'time'] = dfa.loc[mask, 'rid'].astype(int).map(rid_to_time)

total_with_rid = dfa['rid'].notna().sum()
no_match = total_with_rid - n_fixed
print(f'Fixed {n_fixed} rows out of {total_with_rid} rows with rid values.')
print(f'Rows with rid but no match in reference file: {no_match}')

dfa.to_csv(alarms_path, index=False)
print(f'Saved updated alarms to {alarms_path}')

