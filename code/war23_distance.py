import re

import matplotlib.pyplot as plt
from matplotlib import colors
import folium
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import plotly.express as px
from geopy.distance import geodesic

local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True
dfwar = pd.read_csv('data/alarms.csv')
# last_alarm = pd.to_datetime(dfwar['time'][len(dfwar)-1])
# last_alarm = last_alarm.tz_localize('Israel')
dfwar = dfwar[dfwar['threat'] == 0]
dfwar = dfwar[dfwar['time'] >= '2023-10-07 00:00:00']
dfwar = dfwar[dfwar['origin']  == 'Gaza']
dfwar = dfwar.reset_index(drop=True)
date = np.array([d[:10] for d in dfwar['time']])
dateu = np.unique(date)
# now = np.datetime64('now', 'ns')
# nowisr = pd.to_datetime(now, utc=True, unit='s').astimezone(tz='Israel')
# nowstr = str(nowisr)[:16].replace('T', ' ')
# current_date = datetime.now()
# date_list = []
# for idate in range(len(dateu)):
#     date_list.append(current_date.strftime('%Y-%m-%d'))
#     current_date -= timedelta(days=1)
coo = pd.read_csv('data/coord.csv')
# Reverse the list to have the dates in descending order
# date_list.reverse()
# Prin
Gaza = [31.50033, 34.47331]
near = np.zeros(len(dateu))
far = np.zeros(len(dateu))
for day in range(len(dateu)):
    idx = date == dateu[day]
    ids = np.unique(dfwar['id'][idx])
    dist = np.zeros(len(ids))
    for iid in range(len(ids)):
        rows = np.where(dfwar['id'] == ids[iid])[0]
        lat = np.zeros(len(rows))
        long = np.zeros(len(rows))
        for irow, row in enumerate(rows):
            lat[irow] = coo['lat'][coo['loc'] == dfwar['cities'].values[row]].values[0]
            long[irow] = coo['long'][coo['loc'] == dfwar['cities'].values[row]].values[0]
        dist[iid] = geodesic([np.median(lat), np.median(long)], Gaza).km
    near[day] = np.sum(dist <= 20)
    far[day] = np.sum(dist > 20)

plt.figure()
plt.plot(dateu, near, label='less than 20km')
plt.plot(dateu, far, label='more than 20km')
plt.legend()
plt.grid()
plt.xticks(rotation=90)

fig = px.bar(x=dateu, y=n, log_y=True)
# fig = px.bar(prev, y=n, x='date',log_y=True)
html = fig.to_html()
file = open('docs/alarms_last_7_days.html', 'w')
a = file.write(html)
file.close()
##