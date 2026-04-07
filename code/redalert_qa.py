import pandas as pd
import numpy as np   
import os
import requests
import sys
from datetime import datetime, timedelta
# from matplotlib import pyplot as plt

key = os.environ['RedAlert']
start = datetime.strptime('2026-02-28', '%Y-%m-%d')
end = datetime.now()
dates = [(start + timedelta(days=x)).strftime("%Y-%m-%d") for x in range((end-start).days + 1)]

today = datetime.now().strftime('%Y-%m-%d')
alarms = pd.read_csv('https://github.com/yuval-harpaz/alarms/raw/refs/heads/master/data/alarms.csv')
alerts = pd.read_csv('https://github.com/dleshem/israel-alerts-data/raw/refs/heads/main/israel-alerts.csv')
# TODO: copmplete categoty from dleshem (no zeros below)
red2alerts= {'missiles': [1, 'ירי רקטות וטילים'],
             'earthQuake': [0, 'רעידת אדמה'],
             'earthQuakeDrill': [0, 'תרגיל רעידת אדמה'],
             'endAlert': [13, 'האירוע הסתיים'],
             'general': [0, 'כללי'],
             'hazardousMaterialsDrill': [0, 'חומרים מסוכנים'],
             'hostileAircraftIntrusion': [2, 'חדירת כלי טיס עוין'],
             'missilesDrill': [0, 'תרגיל ירי רקטות וטילים'],
             'newsFlash': [14, 'בדקות הקרובות צפויות להתקבל התרעות באזורך'],
             'terroristInfiltration': [10, 'חדירת מחבלים']}
date = today

def redalert2df(date, alarms, alerts, red2alerts, key, to_file=False):
    alarms = alarms[alarms['time'].str.contains(date)]
    alarms = alarms.reset_index(drop=True)
    alerts = alerts[alerts['date'] == '.'.join(date.split('-')[::-1])]
    alerts = alerts.reset_index(drop=True)
    # alerts_time = pd.to_datetime(alerts['date'] + ' ' + alerts['time'])
    # alarms_time = pd.to_datetime(alarms['time'])
    alerts_time = pd.to_datetime(alerts['date'] + ' ' + alerts['time']).dt.tz_localize('Asia/Jerusalem').dt.tz_convert(
        'UTC')
    alarms_time = pd.to_datetime(alarms['time']).dt.tz_localize('Asia/Jerusalem').dt.tz_convert('UTC')
    # TODO - read data to match date in utc time
    url = f"https://redalert.orielhaim.com/api/stats/history?startDate={date}T00:00:00Z&endDate={date}T23:59:59Z&sort=timestamp&order=asc&limit=100"
    headers = {"Authorization": f"Bearer {key}"}
    response = requests.get(url, headers=headers)
    data = response.json()
    if type(data['data']) == list and len(data['data']) == 0:
        print(url)
        raise Exception(f"No data for {date}")
    redalert_time = pd.to_datetime([event['timestamp'] for event in data['data']])
    # TODO: add a while loop until data['pagination']['hasMore'] is false
    dfra = pd.DataFrame(columns=['redalert time','redalert id', 'redalert type', 'rid', 'tzofar id', 'location', 'issues'])
    for event in range(len(data['data'])):
        row = len(dfra)
        dfra.at[row, 'redalert time'] = data['data'][event]['timestamp'].replace('T', ' ').split('.')[0]
        dfra.at[row, 'redalert id'] = data['data'][event]['id']
        current_type = data['data'][event]['type']
        dfra.at[row, 'redalert type'] = current_type
        # find matching rid in alerts
        alerts_candidates = np.where(np.abs(alerts_time - redalert_time[event]) < np.timedelta64(1, 'm'))[0]
        types = [alerts['category'][d] for d in alerts_candidates]
        alerts_candidates = [alerts_candidates[a] for a in range(len(alerts_candidates)) if red2alerts[current_type][0] == types[a]]
        red_locations = [loc['name'] for loc in data['data'][event]['cities']]
        dfra.at[row, 'location'] = '; '.join(red_locations)
        if len(dfra) > 1 and dfra['location'][row] == dfra['location'][row-1] and dfra['issues'][row-1] == '' and dfra['redalert type'][row] == dfra['redalert type'][row-1]:
            dfra.at[row, 'issues'] = 'duplicate'
        elif len(dfra) > 1 and  len([l for l in dfra['location'][row].split('; ') if l not in dfra['location'][row-1]]) == 0 and dfra['redalert type'][row] == dfra['redalert type'][row-1]:
            dfra.at[row, 'issues'] = 'duplicate'
        else:
            alerts_locations = np.array([alerts['data'][d] for d in alerts_candidates])
            issues = ''
            match = ''
            for loc in red_locations:
                iloc = np.where(alerts_locations == loc)[0]
                if len(iloc) == 0:
                    issues += f"{loc}; "
                    match += f"0; "
                elif len(iloc) == 1:
                    match += f"{alerts['rid'][alerts_candidates[iloc[0]]]}; "
            if len(match) > 0:
                match = match[:-2]
            if list(np.unique(match.split('; '))) == ['0']:
                match = ''
            if len(issues) > 0:
                issues = 'no dleshem match for: '+issues[:-2]
            dfra.at[row, 'rid'] = match
            dfra.at[row, 'issues'] = issues
            alarms_candidates = np.where(np.abs(alarms_time - redalert_time[event]) < np.timedelta64(1, 'm'))[0]
            alarms_locations = np.array([alarms['cities'][d].split(',')[0].strip() for d in alarms_candidates])
            # issues = ''
            match = ''
            if red2alerts[current_type][0] < 13:
                for loc in red_locations:
                    iloc = np.where(alarms_locations == loc.split(',')[0].strip())[0]
                    if len(iloc) == 0:
                        issues += f"{loc}; "
                        match += f"0; "
                    elif len(iloc) == 1:
                        match += f"{alarms['id'][alarms_candidates[iloc[0]]]}; "
                if len(match) > 0:
                    match = match[:-2]
                if list(np.unique(match.split('; '))) == ['0']:
                    match = ''
                if len(issues) > 0:
                    issues = 'no tzofar match for: ' + issues[:-2]
            dfra.at[row, 'tzofar id'] = match
            dfra.at[row, 'issues'] = issues
    if to_file:
        dfra.to_excel(f'~/Documents/dfra_{date}.xlsx', index=False)
    tzid_str = dfra['tzofar id'][~dfra['tzofar id'].isnull()].values
    tzid = []
    for ii in range(len(tzid_str)):
        tzid.extend([int(t) for t in tzid_str[ii].split('; ') if len(tzid_str[ii]) > 0])
    tzid = np.unique(tzid)
    alarms_id = alarms['id'].unique()
    missed = [ai for ai in alarms_id if ai not in tzid]
    missed_df = alarms[alarms['id'].isin(missed)]
    if to_file:
        missed_df.to_excel(f'~/Documents/missed_{date}.xlsx', index=False)
    return dfra, missed_df

if __name__ == '__main__':
    debug = False
    if debug:
        redalert2df(today, alarms, alerts, red2alerts, key, to_file=True)
    elif len(sys.argv) == 1:
        print('Example:')
        print('python code/redalert_qa.py 2026-04-04')
        print('look for dfra_<date>.xlsx in ~/Documents')
    else:
        redalert2df(sys.argv[1], alarms, alerts, red2alerts, key, to_file=True)

