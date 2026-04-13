"""
complete_rid.py
Match rows in data/alarms.csv that are missing a `rid` value to
dleshem's israel-alerts data, using location, threat type, and time
(within 1 minute).  Saves result to ~/Documents/alarms.csv for review.
"""

import os
import pandas as pd
def complete_rid():
    # os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    alarms_path = 'data/alarms.csv'
    # out_path = os.path.expanduser('~/Documents/alarms.csv')
    dleshem_url = 'https://github.com/dleshem/israel-alerts-data/raw/refs/heads/main/israel-alerts.csv'

    # ── 1. Load data ──────────────────────────────────────────────────────────────
    print('Reading alarms.csv ...')
    dfa = pd.read_csv(alarms_path)

    print('Reading dleshem data ...')
    dfd = pd.read_csv(dleshem_url)

    # ── 2. Parse datetimes ────────────────────────────────────────────────────────
    dfa['datetime'] = pd.to_datetime(dfa['time'])
    dfd['datetime'] = pd.to_datetime(dfd['date'] + ' ' + dfd['time'], dayfirst=True)

    # ── 3. Map dleshem category_desc → alarm description (substring match) ────────
    # alarms uses short canonical labels; dleshem may append " - האירוע הסתיים" etc.
    alarm_descriptions = dfa['description'].dropna().unique()
    dfd['alarm_type'] = None
    for desc in alarm_descriptions:
        mask = dfd['category_desc'].str.contains(desc, regex=False, na=False)
        dfd.loc[mask & dfd['alarm_type'].isna(), 'alarm_type'] = desc

    dfd_typed = dfd[dfd['alarm_type'].notna()].copy()
    print(f'dleshem rows with a matching alarm type: {len(dfd_typed):,}')

    # ── 4. Expand dleshem: one row per city ───────────────────────────────────────
    print('Expanding dleshem by city ...')
    dfd_typed = dfd_typed.assign(city=dfd_typed['data'].str.split(', ')).explode('city')
    dfd_typed['city'] = dfd_typed['city'].str.strip()
    # Drop duplicates so each (rid, city) pair appears only once
    dfd_typed = dfd_typed.drop_duplicates(subset=['rid', 'city'])

    # Minute-level floor no longer needed; kept only for reference
    # Build the right-hand side for merging
    dfd_merge = (
        dfd_typed[['city', 'alarm_type', 'rid', 'datetime']]
        .rename(columns={'city': 'cities', 'alarm_type': 'description',
                         'datetime': 'd_datetime'})
    )

    # ── 5. Prepare alarms rows that are missing rid ───────────────────────────────
    mask_no_rid = dfa['rid'].isna() | (dfa['rid'] == 0)
    alarms_no_rid = dfa.loc[mask_no_rid, ['cities', 'description', 'datetime']].copy()
    alarms_no_rid.index.name = 'alarms_idx'
    alarms_no_rid = alarms_no_rid.reset_index().sort_values('datetime')
    print(f'alarms rows to complete: {len(alarms_no_rid):,}')

    # ── 6. Match using merge_asof with a 60-second tolerance ─────────────────────
    print('Matching ...')
    dfd_right = (
        dfd_merge
        .rename(columns={'d_datetime': 'datetime'})
        [['cities', 'description', 'datetime', 'rid']]
        .sort_values('datetime')
    )

    all_matches = pd.merge_asof(
        alarms_no_rid,
        dfd_right,
        on='datetime',
        by=['cities', 'description'],
        tolerance=pd.Timedelta('60s'),
        direction='nearest'
    )
    all_matches = all_matches[all_matches['rid'].notna()]

    n_fixed = len(all_matches)
    print(f'Matched {n_fixed:,} rows out of {len(alarms_no_rid):,} '
          f'({100 * n_fixed / len(alarms_no_rid):.1f} %)')

    # ── 7. Write rid back into dfa ────────────────────────────────────────────────
    dfa.loc[all_matches['alarms_idx'].values, 'rid'] = all_matches['rid'].values

    # ── 8. Save for review ────────────────────────────────────────────────────────
    dfa.drop(columns=['datetime']).to_csv(alarms_path, index=False)
    print(f'Saved to {alarms_path}')


