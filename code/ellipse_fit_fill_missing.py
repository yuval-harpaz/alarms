#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fit an elipse to alarm clusters, see if from yemen.
"""
from ellipse_fit import fit_ellipse
import pandas as pd
import numpy as np
import os
from matplotlib import pyplot as plt
from matplotlib.patches import Ellipse
path2data = os.environ['HOME']+'/alarms/data/'
coast = pd.read_csv(path2data+'israel_mediterranean_coast_0.5km.csv').values[:, ::-1]
df = pd.read_csv(path2data+'alarms.csv')
loc = pd.read_csv(path2data+'coord.csv')
ifirst = np.where(df['origin'].isnull() & (df['threat'].values == 0))[0][0]
ids = np.unique(df['id'][ifirst:])


islarge = np.zeros(len(ids), bool)
for jj in range(len(ids)):
    # for jj in [46]:
    islarge[jj] = sum(df['id'] == ids[jj]) > 10
ids = ids[islarge]

plt.figure()
for jj in range(len(ids)):
    # for jj in [46]:
    id0 = ids[jj]
    df0 = df[df['id'] == id0]
    if len(df0) > 10:
        df0 = df0.reset_index(drop=True)
        points = np.zeros((len(df0), 2))
        for ii in range(len(df0)):
            row = np.where(loc['loc'] == df0['cities'][ii])[0][0]
            lat = loc['lat'][row]
            long = loc['long'][row]
            points[ii, :] = [long, lat]
        ellipse = fit_ellipse(points, plot=False)
        if ellipse[1][0]*94.6 > 30 and ellipse[1][1]*111.2 > 60 and np.abs(ellipse[2]-37) < 10:
            edge = 'g'
        else:
            edge = 'k'
        plt.subplot(5, 5, jj+1)
        plt.plot(points[:, 0], points[:, 1], '.r')
        ellipse_patch = Ellipse(xy=ellipse[0], width=ellipse[1][0], height=ellipse[1][1], angle=ellipse[2], edgecolor=edge, fc='None', lw=2)
        plt.gca().add_patch(ellipse_patch)
        plt.text(35, 33, f"{id0} {np.round(ellipse[1][0]*94.6, 1)}x{np.round(ellipse[1][1]*111.2, 1)} {int(np.round(ellipse[2]))}", ha='center')
        plt.plot(coast[:, 0], coast[:, 1])
        plt.axis('equal')
        plt.xlim(34.5, 36)
        # plt.ylim(29.5, 33)

bad = [5308, 5330]
yemen = [i for i in ids if i not in bad]
for jj in range(len(yemen)):
    # for jj in [46]:
    id0 = yemen[jj]
    rows = np.where(df['id'] == id0)[0]
    for row in rows:
        df.at[row, 'origin'] = 'Yemen'

df.to_csv(path2data+'alarms.csv', index=False)

