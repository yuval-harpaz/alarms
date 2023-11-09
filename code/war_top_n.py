import numpy as np
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime

# https://he.wikipedia.org/wiki/%D7%94%D7%9C%D7%97%D7%99%D7%9E%D7%94_%D7%91%D7%A8%D7%A6%D7%95%D7%A2%D7%AA_%D7%A2%D7%96%D7%94_%D7%9C%D7%90%D7%97%D7%A8_%D7%9E%D7%91%D7%A6%D7%A2_%D7%A9%D7%95%D7%9E%D7%A8_%D7%94%D7%97%D7%95%D7%9E%D7%95%D7%AA

os.chdir('/home/innereye/alarms/data/')
dfwar = pd.read_csv('alarms.csv')
# last_alarm = pd.to_datetime(dfwar['time'][len(dfwar)-1])
# last_alarm = last_alarm.tz_localize('Israel')
dfwar = dfwar[dfwar['threat'] == 0]
dfwar = dfwar[dfwar['time'] >= '2023-10-07 00:00:00']
dfwar = dfwar[dfwar['origin']  == 'Gaza']
dfwar = dfwar.reset_index(drop=True)
loc = np.unique(dfwar['cities'])
n = np.zeros(len(loc), int)
for ii in range(len(loc)):
    n[ii] = np.sum(dfwar['cities'] == loc[ii])

nn = 30
tick = np.array([x[::-1] for x in loc])
order = np.argsort(-n)
##
plt.figure()
plt.bar(range(1, nn+1), n[order[:nn]])
for ii in range(nn):
    plt.text(ii+1-0.1, 5, tick[order[ii]], rotation=90, color='w')
    plt.text(ii+1-0.2, n[order[ii]] + 3, n[order[ii]], color = 'k')
ax = plt.gca()
ax.yaxis.grid()
plt.xticks([])
plt.title('rocket alarms from 2023-10-7 until ' + dfwar['time'][len(dfwar)-1])


