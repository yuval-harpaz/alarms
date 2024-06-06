import pandas as pd
from datetime import date, timedelta, datetime
import os
import numpy as np
from matplotlib import pyplot as plt
local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True
##
df = pd.read_csv('data/idf_dashboard.csv')
def movmean(data, win):
    #  smooth data with a moving average. win should be an odd number of samples.
    #  data is np.ndarray with samples by channels shape
    #  to get smoothing of 3 samples back and 3 samples forward use win=7
    if len(data.shape) == 1:
        data = data[:, np.newaxis]
        nChannels = 1
    else:
        nChannels = data.shape[1]
    smooth = data.copy()
    for iChannel in range(nChannels):
        if len(data.shape) == 1:
            vec = data
        else:
            vec = data[:, iChannel]
        padded = np.concatenate(
            (np.ones((win,)) * vec[0], vec, np.ones((win,)) * vec[-1]))
        sm = np.convolve(padded, np.ones((win,)) / win, mode='valid')
        sm = sm[int(win / 2):]
        sm = sm[0:vec.shape[0]]
        if len(data.shape) == 1:
            smooth[:] = sm
        else:
            smooth[:, iChannel] = sm
    return smooth
##
start_dt = date(2023, 12, 10)
end_dt = date.today()
delta = timedelta(days=1)
dates = []
while start_dt <= end_dt:
    dates.append(start_dt.isoformat())
    start_dt += delta
res = np.diff(df['מתחילת המלחמה'])
gaz = np.diff(df['מתחילת התמרון'])
dates = np.array(dates[1:])
rest = np.zeros(len(dates), int)
gaza = np.zeros(len(dates), int)
for ii in range(1, len(df)):
    row = np.where(dates == df['תאריך'][ii])[0][0]
    rest[row] = res[ii-1]
    gaza[row] = gaz[ii-1]



t = pd.to_datetime(dates)
plt.figure()
plt.plot(t, movmean(rest, 7))
plt.plot(t, movmean(gaza, 7))


