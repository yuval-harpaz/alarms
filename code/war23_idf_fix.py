import pandas as pd
import os
import numpy as np

local = '/home/innereye/alarms/'
os.chdir(local)
##
csv = 'data/deaths_idf.csv'
idf = pd.read_csv('data/deaths_idf.csv')
db = pd.read_csv('data/oct7database.csv')
pid = db['pid'].values
for ii in range(len(idf)):
    row = np.where(pid == idf['pid'][ii])[0]
    if len(row) == 1:
        row = row[0]
        first = db['שם פרטי'][row]
        name = idf['name'][ii]
        if first not in name:
            print(f'ii={ii}, pid={idf["pid"][ii]}, {first} not in {name}')

pid = df['pid'].values
pidu = np.unique(pid)
dbpid = db['pid'].values
for ii in range(len(df)):
    row = np.where(dbpid == df['pid'][ii])[0][0]
    db.at[row, 'הנצחה'] = df['url'][ii]

null = np.where(db['הנצחה'].isnull())[0]
for dbr in null:
    pid = db['pid'][dbr]
    crr = np.where(cref['oct7map_pid'] == pid)[0]
    if len(crr) == 1:
        btl_id = cref['btl_id'].values[crr[0]]
        if ~np.isnan(btl_id):
            laad = 'https://laad.btl.gov.il/Web/He/TerrorVictims/Page/Default.aspx?ID='+str(int(btl_id))
            db.at[dbr, 'הנצחה'] = laad

db.to_csv('tmp.csv', index=False)