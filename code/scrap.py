import re
from matplotlib import colors
import folium
import pandas as pd
import numpy as np
import os
from ellipse_fit import guess_yemen

db = pd.read_csv('data/oct7database.csv')
oct7 = pd.read_json('https://service-f5qeuerhaa-ey.a.run.app/api/individuals')
df = pd.DataFrame(columns=['pid', 'name'])
for ii in range(len(oct7)):
    row = np.where(db['pid'] == oct7['pid'][ii])[0]
    if len(row) == 0:
        print(oct7['pid'][ii], oct7['name'][ii])
        df.loc[len(df)] = [oct7['pid'][ii], oct7['name'][ii]]
df.to_csv('~/Documents/missing.csv', index=False)

df1 = pd.DataFrame(columns=['pid', 'oct7map', 'oct7database'])
for ii in range(len(oct7)):
    row = np.where(db['pid'] == oct7['pid'][ii])[0]
    if len(row) == 1:
        if db['first name'][row[0]] not in oct7['name'][ii]:
            print(oct7['pid'][ii], oct7['name'][ii], db['first name'][row[0]], 
                  db['last name'][row[0]])
            cells = [oct7['pid'][ii], oct7['name'][ii], 
                    db['first name'][row[0]] + ' ' + db['last name'][row[0]]]
            df1.loc[len(df1)] = cells
df1.to_csv('~/Documents/mismatch.csv', index=False)