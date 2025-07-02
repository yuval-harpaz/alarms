"""Set NLI for DB based on excel downloaded from https://docs.google.com/spreadsheets/d/1iEnnPpaDH9_Br_I2_8pjtPJcoFJf4ByP4xcdjdyc-Kc/edit?usp=sharing."""
import pandas as pd
import os
import numpy as np

local = '/home/innereye/alarms/'
# islocal = False
if os.path.isdir(local):
    os.chdir(local)
    local = True
db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})
nli = pd.read_excel('~/Documents/NLI.xlsx', sheet_name='manual', dtype={'nli_id': str, 'harpaz_id': str})

last_pid = 119
last_row = np.where(db['pid'] == last_pid)[0][0]
for ii in range(last_row):
    if nli['pid'][ii] != db['pid'][ii]:
        raise ValueError(f"PID mismatch at index {ii}: {nli['pid'][ii]} != {db['pid'][ii]}")
    nli_id = nli['nli_id'][ii]
    if str(nli_id) != 'nan' and db['הספריה הלאומית'][ii] != nli_id:
        print(f"Setting NLI for PID {db['pid'][ii]} from {db['הספריה הלאומית'][ii]} to {nli_id}")
        db.loc[ii, 'הספריה הלאומית'] = nli_id
db.to_csv('data/oct7database.csv', index=False)