"""Export data to html map."""
import pandas as pd
import numpy as np
loc = pd.read_csv('data/deaths_by_loc.csv')

db = pd.read_csv('~/Documents/oct7database - Data2.csv')
loc1 = loc[loc['total'] == 1]
loc1 = loc1.reset_index(drop=True)
for ii in range(len(loc1)):
    dbrow = np.where(db['מקום האירוע'].values == loc1['name'][ii])[0]
    if len(dbrow) == 1:
        coo = db['event_coordinates'][dbrow[0]]
        if type(coo) == str:
            if coo[:2] != '31':
                print(f"bad coo for {loc1['name'][ii]}")
        else:
            print(f"no coo for {loc1['name'][ii]}")

##
db = pd.read_csv('~/Documents/oct7database - Data3.csv')
migu = np.unique(db['מקום האירוע'].values[db['מקום האירוע'].str.contains('מיגוני') == True])
migu = pd.DataFrame(migu, columns=['name'])
migu.to_csv('~/Documents/migu.csv', index=False)
##
migu = pd.read_csv('~/Documents/migu.csv', sep=',')
db = pd.read_csv('~/Documents/oct7database - Data4.csv')
migu = migu[~migu['lat'].isnull()]
migu = migu.reset_index(drop=True)
for ii in range(len(migu)):
    rows = np.where(db['מקום האירוע'].values == migu['name'][ii])[0]
    expected = np.array([migu['lat'][ii], migu['lon'][ii]])
    print(migu['name'][ii])
    for row in rows:
        current = str(db['event_coordinates'][row])
        if current == 'nan':
            print(f"nan for pid {db['pid'][row]}")
        else:
            current = np.array(current.split(', ')).astype(float)
            if np.max(np.abs(expected-current)) > 0.0000000001:
                print(f"unexpected for pid {db['pid'][row]}")



