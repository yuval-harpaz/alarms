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

df = pd.read_csv(path2data+'alarms.csv')
loc = pd.read_csv(path2data+'coord.csv')
ifirst = np.where(df['origin'].isnull() & (df['threat'].values == 0))[0][0]
ids = np.unique(df['id'][ifirst:])
sp = 0
plt.figure()
for jj in range(len(ids)):
    # for jj in [46]:
    id0 = ids[jj]
    df0 = df[df['id'] == id0]
    if len(df0) > 10:
        sp += 1
        df0 = df0.reset_index(drop=True)
        points = np.zeros((len(df0), 2))
        for ii in range(len(df0)):
            row = np.where(loc['loc'] == df0['cities'][ii])[0][0]
            lat = loc['lat'][row]
            long = loc['long'][row]
            points[ii, :] = [long, lat]
        plt.subplot(5, 5, sp)
        ellipse = fit_ellipse(points)
        if ellipse[1][0]*94.6 > 30 and ellipse[1][1]*111.2 > 60 and np.abs(ellipse[2]-37) < 10:
            color = [0.5, 1, 0.5]
        else:
            color = [0, 0, 0]
        plt.title(f"{id0} {np.round(ellipse[1][0]*94.6, 1)}x{np.round(ellipse[1][1]*111.2, 1)} {int(np.round(ellipse[2]))}", color=color)
        plt.axis('off')
print('done')


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
            edge='g'
        else:
            edge='k'
        plt.plot(points[:, 0], points[:, 1], '.r')
        ellipse_patch = Ellipse(xy=ellipse[0], width=ellipse[1][0], height=ellipse[1][1], angle=ellipse[2], edgecolor=edge, fc='None', lw=2)
        plt.gca().add_patch(ellipse_patch)
            
plt.axis('equal')
plt.show()



