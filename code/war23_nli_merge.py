"""find new btl."""
import pandas as pd
# import requests
import os
import numpy as np
from selenium import webdriver
import time

local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True

db = pd.read_csv('data/oct7database.csv')
nli_prev = pd.read_csv('~/Documents/nli.csv', dtype={'nli_id': str})
nli = pd.read_csv('data/tmp_nli.csv', dtype={'nli_id': str})


for ii in range(len(nli)):
    if nli['nli_id'].isna().values[ii] or nli['nli_id'].values[ii] == 'nan':
        if len(str(nli_prev['nli_id'][ii])) > 3:
            rep = nli_prev['nli_id'][ii]
            rep = rep[:-3]+'171'
            nli.at[ii, 'nli_id'] = rep
        else:
            nli.at[ii, 'nli_id'] = ''
    else:
        nli.at[ii, 'nli_id'] = nli['nli_id'][ii]
    if len(str(nli['harpaz_id'].values[ii])) == 0:
        if len(str(nli_prev['harpaz_id'][ii])) > 0:
            nli.at[ii, 'harpaz_id'] = str(int(nli_prev['harpaz_id'][ii]))
        else:
            nli.at[ii, 'harpaz_id'] = ''
    elif nli['harpaz_id'].isna().values[ii] or nli['harpaz_id'].values[ii] == 'nan':
        nli.at[ii, 'harpaz_id'] = ''
    else:
        nli.at[ii, 'harpaz_id'] = str(int(nli['harpaz_id'].values[ii]))
    if nli['candidates'].isna().values[ii] or len(nli['candidates'].values[ii]) == 0:
        if len(str(nli_prev['candidates'][ii])) > 3:
            nli.at[ii, 'candidates'] = nli_prev['candidates'][ii]
        else:
            nli.at[ii, 'candidates'] = ''
nli.to_csv('data/nli.csv', index=False)
