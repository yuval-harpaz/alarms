import pandas as pd
import os
import numpy as np
import sys
import datetime
from matplotlib import pyplot as plt


local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True
    sys.path.append(local + 'code')

dfwar = pd.read_csv('data/alarms.csv')
dfwar = dfwar[dfwar['time'] >= '2023-10-07 00:00:00']
dfwar = dfwar[dfwar['threat'] == 0]
dfwar['time_round'] = [x[:14]+'00' for x in dfwar['time'].values]
dfwar = dfwar.reset_index(drop=True)


date = np.array([x[:10] for x in dfwar['time']])
dateu = np.unique(date)
timeu = []
for day in dateu:
    for hour in range(24):
        timeu.append(day + ' ' + str(hour).zfill(2) + ':00')
dt = pd.to_datetime(timeu)

alarms_per_hour = np.zeros(len(timeu), int)
for itime in range(len(timeu)):
    alarms_per_hour[itime] = np.sum(dfwar['time_round'] == timeu[itime])
##
plt.plot(dt, alarms_per_hour)
plt.grid()
plt.title('Alarms per hour over all regions in Israel since 7-Oct-23')
plt.ylabel('Alarms per hour')
plt.xlabel('Time')
plt.yticks(range(0,801,100))
##

df = pd.DataFrame(timeu, columns=['time'])
df['alarms'] = alarms_per_hour
df.to_csv('alarms_per_hour.csv', index=False, sep=',')

    #
    #
    #
    # xs = pd.to_datetime(df['HM'], format='%H:%M')
    # xs = xs - datetime.datetime.strptime('00:00:00', '%H:%M:%S')
    # # xs = xs.dt.seconds / (24 * 3600)
    # xs = np.round(xs.dt.seconds / 3600) / 24
    # xs = xs * 2 * np.pi
    # xu = np.arange(0, 24) / 24
    # xu = xu * 2 * np.pi
    # y = [np.sum(xs == x) for x in xu]
    # # id = df['id'].to_numpy()
    # # y = [len(np.unique(id[xs == x])) for x in xu]
    # # fig = plt.figure(figsize=(7,7))
    # ax = plt.subplot(3, 5, idate+1, projection='polar')
    # ax.bar(xu+(2 * np.pi /24 / 2), y, width=1/4, alpha=0.3, color='red', label=dateu[idate])
    # ax.set_theta_direction(-1)
    # ax.set_theta_offset(np.pi/2)
    # ax.set_xticks(np.linspace(0, 2*np.pi, 24, endpoint=False))
    # ticks = ['12 AM', '1 AM', '2 AM', '3 AM', '4 AM', '5 AM', '6 AM', '7 AM','8 AM','9 AM','10 AM','11 AM','12 PM', '1 PM', '2 PM', '3 PM', '4 PM',  '5 PM', '6 PM', '7 PM', '8 PM', '9 PM', '10 PM', '11 PM' ]
    # ax.set_xticklabels(ticks, fontsize=7)
    # # plt.setp(ax.get_yticklabels(), visible=False)
    # #Bars to the wall
    # # plt.ylim(0,2)
    # # plt.legend(bbox_to_anchor=(1, 0), fancybox=True, shadow=True)
    # plt.title(dateu[idate])
    # plt.show()
    #
