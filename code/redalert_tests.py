import pandas as pd
import numpy as np   
import os
import requests
import time
from datetime import datetime, timedelta
from matplotlib import pyplot as plt

key = os.environ['RedAlert']
start = datetime.strptime('2026-02-28', '%Y-%m-%d')
end = datetime.now()
dates = [(start + timedelta(days=x)).strftime("%Y-%m-%d") for x in range((end-start).days + 1)]
sp = 0
plt.figure()
for typ in ['missiles', 'newsFlash']:
    stats = pd.DataFrame(columns=['date','min diff', 'n events'])
    for date in dates:
        url = f"https://redalert.orielhaim.com/api/stats/history?category={typ}&startDate={date}T00:00:00Z&endDate={date}T23:59:59Z&sort=timestamp&order=asc&limit=100"
        headers = {"Authorization": f"Bearer {key}"}
        response = requests.get(url, headers=headers)
        data = response.json()
        dfr = pd.DataFrame(data['data'])
        row = len(stats)
        stats.at[row, 'date'] = date
        if len(dfr) == 0:
            stats.at[row, 'min diff'] = 0
            stats.at[row, 'n events'] = 0
        else:
            dfr['datetime'] = pd.to_datetime(dfr['timestamp'])
            np.sort(dfr['datetime'].diff())
            diffs = dfr['datetime'].diff().values[1:]
            seconds = np.sort(diffs).astype('timedelta64[s]').astype(int)
            stats.at[row, 'min diff'] = seconds[0]
            stats.at[row, 'n events'] = len(dfr)
    for measure in ['min diff', 'n events']:
        sp += 1
        plt.subplot(2, 2, sp)
        plt.bar(range(len(stats)), stats[measure])
        plt.xticks(range(len(stats)), stats['date'], rotation=30, ha='right')
        plt.xlim(-0.5, len(dates))
        plt.gca().yaxis.grid()
        plt.title(f"{typ} {measure}")
        for jj in range(len(stats)):
            plt.text(jj, stats[measure][jj], str(stats[measure][jj]), ha='center')

##  matchin redalert to alarms.csv. did not finish because moed on to take ground truth from telegram
dfa = pd.read_csv('https://github.com/yuval-harpaz/alarms/raw/refs/heads/master/data/alarms.csv')
dfa = dfa[dfa['time'] > '2026-02-28']
dfa = dfa[dfa['threat'] == 0]
dfa.reset_index(drop=True, inplace=True)
# timec = pd.to_datetime(dfc['date'] + ' ' + dfc['from_time'])
timea = pd.to_datetime(dfa['time'])
typ = 'missiles'
for date in dates:
    url = f"https://redalert.orielhaim.com/api/stats/history?category={typ}&startDate={date}T00:00:00Z&endDate={date}T23:59:59Z&sort=timestamp&order=asc&limit=100"
    headers = {"Authorization": f"Bearer {key}"}
    response = requests.get(url, headers=headers)
    data = response.json()
    dfr = pd.DataFrame(data['data'])
    row = len(stats)
    # stats.at[row, 'date'] = date
    if len(dfr) == 0:
        dfr['datetime'] = pd.to_datetime(dfr['timestamp'])
        for ievent in range(len(dfr)):
            event_time = dfr['datetime'][ievent]
            for loc in dfr['cities'][ievent]:
                name = loc['name']
                rowa = np.where((dfa['cities'].values == name) and (np.abs(timea - event_time) < np.timedelta64(2, 'm')))[0]

# key = os.environ['RedAlert']
# command = f'curl "https://redalert.orielhaim.com/api/stats/history?category=missiles&startDate=2026-03-14T00:00:00Z&endDate=2026-03-14T23:59:59Z&sort=timestamp&order=asc&limit=100"   -H "Authorization: Bearer {key}" -o ~/Documents/today.json'
# os.system(command)