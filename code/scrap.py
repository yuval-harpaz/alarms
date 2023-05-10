import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
import matplotlib
# Drag coefficient, projectile radius (m), area (m2) and mass (kg).
import pandas as pd
import os
from datetime import datetime

# https://he.wikipedia.org/wiki/%D7%94%D7%9C%D7%97%D7%99%D7%9E%D7%94_%D7%91%D7%A8%D7%A6%D7%95%D7%A2%D7%AA_%D7%A2%D7%96%D7%94_%D7%9C%D7%90%D7%97%D7%A8_%D7%9E%D7%91%D7%A6%D7%A2_%D7%A9%D7%95%D7%9E%D7%A8_%D7%94%D7%97%D7%95%D7%9E%D7%95%D7%AA

os.chdir('/home/innereye/alarms/data/')
alarms = pd.read_csv('alarms.csv')
strikes = pd.read_csv('strikes_in_gazza.csv')
dates = pd.date_range(start='2019-06-13', end=datetime.today())
# datelist = pd.date_range(datetime.today(), periods=100).tolist()
datesa = [x[:10] for x in alarms['time']]
datess = [x[:10] for x in strikes['date']]
data = np.zeros((len(dates), 2))
for ii in range(len(dates)):
    d = str(dates[ii])[:10]
    if d in datesa:
        data[ii, 0] = 1
    if d in datess:
        data[ii, 1] = 1

plt.figure()
idx = np.where(data[:, 0])[0]
plt.plot(dates[idx], np.ones(len(idx)), 'or', label='alarms')
idx = np.where(data[:, 1])[0]
plt.plot(dates[idx], np.ones(len(idx)), 'xb', label='strikes')

datasm = data.copy()
for ii in range(3, data.shape[0]-3):
    datasm[ii, 0] = np.mean(data[ii-3:ii+4, 0])
    datasm[ii, 1] = np.mean(data[ii-3:ii+4, 1])
datasm[:4,:] = np.nan
##
plt.figure()
plt.plot(dates, datasm[:, 0]+0.05, 'r', label='alarms')
plt.plot(dates, datasm[:, 1], 'b', label='strikes')
plt.text(dates[154], 0.8, 'חגורה שחורה'[::-1], ha='center')
plt.text(dates[430], 0.8, 'בלונים'[::-1], ha='center')
plt.text(dates[703], 0.8, 'שומר חומות'[::-1], ha='center')
plt.xticks(rotation=90)
plt.legend()
