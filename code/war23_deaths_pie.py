import pandas as pd
import os
import numpy as np
import sys
from matplotlib import pyplot as plt

local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True
    sys.path.append(local + 'code')

df = pd.read_csv('data/deaths_manual.csv')

status = df['status'].values
rank = df['rank'].values.astype(str)
statusu = np.unique(status)
for ii in range(len(status)):
    if status[ii] == 'חייל':
        if 'מיל' in rank[ii]:
            status[ii] = 'מילואים'
        elif rank[ii] in [ 'אל"ם', 'סא"ל', 'סג"ם', 'סגן', 'סרן', 'רס"ן']:
            status[ii] = 'קצין'
    if ' זר' in status[ii] or status[ii] == 'סטודנט':
        status[ii] = 'זר'
statusu = np.unique(status)

stat = ['אזרח', 'כבאי', 'שוטר', 'מילואים', 'חייל', 'קצין', 'שב"כ', 'זר']
colors = ['b', 'r','cyan','olive','green',(0, 1, 0),'brown','orange']
x = np.zeros(len(stat), int)
for jj in range(len(stat)):
    x[jj] = np.sum(status == stat[jj])

labels = [ll[::-1] for ll in stat]
for il in range(len(labels)):
    labels[il] = str(x[il]) + ' :' + labels[il]
plt.pie(x, labels=labels, colors=colors)

state = ['civilian', 'fire-fighter', 'police', 'reserves', 'soldier', 'officer', 'Shin-Bet', 'foreign']
for il in range(len(labels)):
    labels[il] = state[il]+': '+str(x[il])
plt.pie(x, labels=labels, colors=colors)
