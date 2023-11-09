import pandas as pd
import os
import numpy as np
import sys
import datetime
from matplotlib import pyplot as plt
# import folium

local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True
    sys.path.append(local + 'code')

dfwar = pd.read_csv('data/alarms.csv')
dfwar = dfwar[dfwar['time'] >= '2023-10-07 00:00:00']
dfwar = dfwar[dfwar['threat'] == 0]
dfwar = dfwar[dfwar['origin'] == 'Gaza']
dfwar['HM'] = [x[11:16] for x in dfwar['time'].values]
dfwar = dfwar.reset_index(drop=True)
date = np.array([x[:10] for x in dfwar['time']])
##
dateu = np.unique(date)[-15:]
yy = np.zeros((24, 14))
for idate in range(len(dateu)):
    df = dfwar[date == dateu[idate]]
    xs = pd.to_datetime(df['HM'], format='%H:%M')
    xs = xs - datetime.datetime.strptime('00:00:00', '%H:%M:%S')
    # xs = xs.dt.seconds / (24 * 3600)
    xs = np.round(xs.dt.seconds / 3600) / 24
    xs = xs * 2 * np.pi
    xu = np.arange(0, 24) / 24
    xu = xu * 2 * np.pi
    y = [np.sum(xs == x) for x in xu]
    if idate == 14:
        y = np.mean(yy, 1)
        tit = 'Avg'
    else:
        yy[:, idate] = y
        tit = dateu[idate][8:10] + '/' + dateu[idate][5:7]
    # id = df['id'].to_numpy()
    # y = [len(np.unique(id[xs == x])) for x in xu]
    # fig = plt.figure(figsize=(7,7))
    ax = plt.subplot(3, 5, idate+1, projection='polar')
    ax.bar(xu+(2 * np.pi /24 / 2), y, width=1/4, alpha=0.3, color='red', label=dateu[idate])
    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.pi/2)
    ax.set_xticks(np.linspace(0, 2*np.pi, 24, endpoint=False))
    ticks = ['12 AM', '1 AM', '2 AM', '3 AM', '4 AM', '5 AM', '6 AM', '7 AM','8 AM','9 AM','10 AM','11 AM','12 PM', '1 PM', '2 PM', '3 PM', '4 PM',  '5 PM', '6 PM', '7 PM', '8 PM', '9 PM', '10 PM', '11 PM' ]
    ax.set_xticklabels(ticks, fontsize=7)
    # plt.setp(ax.get_yticklabels(), visible=False)
    #Bars to the wall
    # plt.ylim(0,2)
    # plt.legend(bbox_to_anchor=(1, 0), fancybox=True, shadow=True)
    plt.title(tit, ha='left', x=-0.15, y=0.83, color='b')
    # plt.text(0, 0.9, dateu[idate][5:])
    plt.show()

##
plt.figure()
ax = plt.subplot(121, projection='polar')
ax.bar(xu[:12]*2+(2 * np.pi /12 / 2), y[12:], width=2*np.pi/12, alpha=0.3, color='blue', label='PM')
ax.bar(xu[:12]*2+(2 * np.pi /12 / 2), y[:12], width=2*np.pi/12, alpha=0.7, color='red', label='AM')
ax.set_theta_direction(-1)
ax.set_theta_offset(np.pi/2)
ax.set_xticks(np.linspace(0, 2*np.pi, 12, endpoint=False))
ticks = ['12', '1', '2', '3', '4', '5', '6', '7','8','9','10','11']
ax.set_xticklabels(ticks, fontsize=7)
plt.legend(loc=[-0.15, 0.83], reverse=True)
plt.title('hour')
plt.show()

#
dfm = dfwar[(dfwar['time'] > dateu[0]) & (dfwar['time'] < dateu[-1])]
minute = [int(x[14:16]) for x in dfm['time']]
xum = np.arange(0, 60) / 60
xum = xum * 2 * np.pi
ym = [np.sum(minute == x) for x in np.arange(60).astype(int)]
ym = np.array(ym)/14
# plt.figure()
ax = plt.subplot(122, projection='polar')
ax.bar(xum+(2 * np.pi /60 / 2), ym, width=2*np.pi/60, alpha=0.3, color='red', label='minute')
# ax.bar(xu[:12]*2+(2 * np.pi /12 / 2), y[:12], width=2*np.pi/12, alpha=0.7, color='red', label='AM')
ax.set_theta_direction(-1)
ax.set_theta_offset(np.pi/2)
ax.set_xticks(np.linspace(0, 2*np.pi, 60, endpoint=False))
ticks = np.arange(60)
ax.set_xticklabels(ticks, fontsize=7)
# plt.legend(loc=[-0.15, 0.83], reverse=True)
plt.title('minute')
plt.show()

