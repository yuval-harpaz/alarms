import pandas as pd
import os
import Levenshtein
import numpy as np


local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True

db = pd.read_csv('data/oct7database.csv')
# haa = pd.read_csv('data/deaths_haaretz.csv')
ynet = pd.read_csv('data/ynetlist.csv')
ynet['מקום מגורים'] = ynet['מקום מגורים'].str.replace('\xa0', ' ')
# idf = pd.read_csv('data/deaths_idf.csv')
##
found = -np.ones(len(db), int)
goodness = -np.ones(len(db), int)
age = ynet['גיל'].values
first = ynet['שם פרטי'].values
last = ynet['שם משפחה'].values
fro = ynet['מקום מגורים'].values
for ii in range(len(db)):
    fit_1st = first == db['שם פרטי'][ii]
    fit_last = last == db['שם משפחה'][ii]
    fit_loc = (fro == db['Residence'][ii]) | (fro == db['Country'][ii])
    fit_age = age == db['Age'][ii]
    fit = np.sum([fit_1st, fit_last, fit_loc, fit_age], 0)
    ifit = np.argmax(fit)
    goodness[ii] = fit[ifit]
    if goodness[ii] > 1 and np.sum(fit == goodness[ii]) == 1:  # one best match
        if ifit in found:
            prev = np.where(found == ifit)[0]
            if goodness[ii] > np.max(goodness[prev]):
                found[ii] = ifit
            else:
                print(f"{ii} {ifit} already")
            found[prev] = -1
        found[ii] = ifit
df = pd.DataFrame(columns=['pid', 'ynet_row', 'db_first', 'db_last','db_residence', 'db_country', 'ynet_first', 'ynet_last', 'ynet_from'])        
df['pid'] = db['pid']
df['ynet_row'] = found
df['db_first'] = db['שם פרטי']
df['db_last'] = db['שם משפחה']
df['db_residence'] = db['Residence']
df['db_country'] = db['Country']
for ii in range(len(db)):
    row = found[ii]
    if row > -1:
        df.at[ii, 'ynet_first'] = first[row]
        df.at[ii, 'ynet_last'] = last[row]
        df.at[ii, 'ynet_from'] = fro[row]
df.to_csv('~/Documents/ynet_pid.csv', index=False)


