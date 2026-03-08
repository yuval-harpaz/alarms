import pandas as pd
import numpy as np
dfl = pd.read_csv('~/RedAlert/israel-alerts.csv')
dfy = pd.read_csv('~/alarms/data/alarms.csv')
#sanity check
test_case = ['2026-03-07T23:21:00', 'מעיין ברוך']
row_l = dfl[(dfl['alertDate'] == test_case[0]) & (dfl['data'] == test_case[1])]
print(row_l)
row_y = dfy[(dfy['time'] == test_case[0].replace('T', ' ')) & (dfy['cities'] == test_case[1])]
print(row_y)