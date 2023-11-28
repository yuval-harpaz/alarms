import requests
import pandas as pd
# import numpy as np
import os

local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True

df = pd.read_csv('data/casualties_by_severity.csv')
time = pd.to_datetime(df['time'])
plt.bar(