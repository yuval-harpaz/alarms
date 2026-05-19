import pandas as pd
import numpy as np
import os
import requests
from datetime import date, timedelta

local = '/home/yuval/alarms/'
if os.path.isdir(local):
    os.chdir(local)
else:
    local = '/home/innereye/alarms/'
    if os.path.isdir(local):
        os.chdir(local)

url = os.environ['Seismo']
# Read existing data
df = pd.read_csv('data/earthquakes.csv')
original_ids = set(df['id'])

# Parse timestamps and extract date part
df['_date'] = pd.to_datetime(df['timestamp']).dt.date

# Use the last 3 calendar dates (today minus 2 days through today)
cutoff_date = date.today() - timedelta(days=2)
print(f"Removing rows from {cutoff_date} onwards (last 3 calendar dates) and re-fetching from API")

# Keep only rows older than the cutoff date
df_keep = df[df['_date'] < cutoff_date].drop(columns=['_date'])
print(f"Kept {len(df_keep)} rows before cutoff, dropped {len(df) - len(df_keep)} rows")

# Fetch new data from API: endDate is exclusive, so use tomorrow to include today
tomorrow = date.today() + timedelta(days=1)
start_str = cutoff_date.strftime('%Y-%m-%d')
end_str = tomorrow.strftime('%Y-%m-%d')
print(f"Fetching API data from {start_str} to {end_str}")

response = requests.get(url + f'?startDate={start_str}&endDate={end_str}')
data = response.json()
df_new = pd.DataFrame(data['earthquakes'])
print(f"Fetched {len(df_new)} rows from API")

# API returns oldest-first; reverse to get newest-first
df_new = df_new.iloc[::-1].reset_index(drop=True)

# Concatenate and sort newest-first
df_out = pd.concat([df_new, df_keep], ignore_index=True)
df_out = df_out.sort_values('timestamp', ascending=False, ignore_index=True)
print(f"Total rows after update: {len(df_out)}")
print(f"Latest timestamp: {df_out['timestamp'].iloc[0]}")
print(f"Oldest timestamp: {df_out['timestamp'].iloc[-1]}")

# Sanity check: verify all original rows are present in the new data
new_ids = set(df_out['id'])
missing = original_ids - new_ids
if missing:
    print(f"WARNING: {len(missing)} rows from the original file are MISSING in the new file:")
    print(df[df['id'].isin(missing)][['id', 'timestamp', 'region', 'magnitude']])
else:
    print(f"Sanity check passed: all {len(original_ids)} original rows are present in the new file")

    # Check for new rows
    added_ids = new_ids - original_ids
    print(f"New rows added: {len(added_ids)}")

    # Check for modified rows (same id, different data); equal_nan=True avoids NaN != NaN false positives
    shared_ids = original_ids & new_ids
    df_old_shared = df.set_index('id').loc[list(shared_ids)].drop(columns=['_date'])
    df_new_shared = df_out.set_index('id').loc[list(shared_ids)]
    common_cols = df_old_shared.columns.intersection(df_new_shared.columns)
    diff = df_old_shared[common_cols].compare(df_new_shared[common_cols], align_axis=1, result_names=('old', 'new'))
    modified_ids = diff.index
    print(f"Modified rows: {len(modified_ids)}")

    def is_significant_diff(old_val, new_val):
        """Return True only if the difference is meaningful."""
        old_empty = pd.isna(old_val) or old_val == ''
        new_empty = pd.isna(new_val) or new_val == ''
        if old_empty and new_empty:
            return False
        try:
            if np.isclose(float(old_val), float(new_val), rtol=1e-9):
                return False
        except (TypeError, ValueError):
            pass
        return old_val != new_val

    for mid in modified_ids:
        real_diffs = [
            f"    {col}: {df_old_shared.loc[mid, col]!r} -> {df_new_shared.loc[mid, col]!r}"
            for col in common_cols
            if is_significant_diff(df_old_shared.loc[mid, col], df_new_shared.loc[mid, col])
        ]
        if real_diffs:
            print(f"\n  id: {mid}")
            for d in real_diffs:
                print(d)

    significant_changes = sum(
        1 for mid in modified_ids
        if any(is_significant_diff(df_old_shared.loc[mid, col], df_new_shared.loc[mid, col])
               for col in common_cols)
    )
    print(f"Rows with significant changes: {significant_changes}")
    if len(added_ids) == 0 and significant_changes == 0:
        print("No new or modified data — file not saved")
    else:
        df_out.to_csv('data/earthquakes.csv', index=False)
        print("Saved data/earthquakes.csv")
