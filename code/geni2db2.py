import pandas as pd
import numpy as np
import os
from urllib.parse import unquote

# geni = pd.read_excel('~/Documents/geni_pid.xlsx')
db = pd.read_csv('~/Documents/db_geni.csv')
private = pd.read_excel('~/Documents/private2.xlsx')
not_empty = np.where([len(p) > 3 for p in private['פרופיל Geni'].astype(str).values])[0]
for ii in not_empty:
    url = private['פרופיל Geni'][ii]
    name = private['Name'][ii]
    db_row = np.where(db['שם פרטי'].str.contains(name.split(' ')[0]) & db['שם משפחה'].str.contains(name.split(' ')[-1]))[0]
    if len(db_row) == 1:
        db_row = db_row[0]
        if str(db.at[db_row, 'geni']) == str(private['פרופיל Geni'][ii]):
            pass
        elif len(str(db.at[db_row, 'geni'])) > 3:
            print(db.at[db_row, 'geni'])
        else:
            db.at[db_row, 'geni'] = private['פרופיל Geni'][ii]
    elif len(db_row) > 1:
        print(str(ii)+' many for ' + name)
    elif len(db_row) == 0:
        print(str(ii)+' none for ' + name)
db[['pid', 'first name', 'last name', 'geni']].to_csv('data/geni.csv', index=False)

##
df = pd.read_csv('data/oct7database.csv')
df = df[['pid', 'first name', 'last name']]
for ii in np.where(~db['geni'].isnull())[0]:
    row = np.where(df['pid'] == db['pid'][ii])[0][0]
    df.at[row, 'geni'] = db['geni'][ii]
df.to_csv('data/geni.csv', index=False)