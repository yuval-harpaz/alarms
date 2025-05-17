import re
from matplotlib import colors
import folium
import pandas as pd
import numpy as np
import os
from ellipse_fit import guess_yemen


local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True
coo = pd.read_csv('data/coord.csv')
dfwar = pd.read_csv('data/alarms.csv')
for ii in range(53772, 58070):
    dfwar.at[ii, 'origin'] = np.nan
test = guess_yemen(dfwar, coo)
