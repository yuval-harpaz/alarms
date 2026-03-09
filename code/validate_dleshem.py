import pandas as pd
import numpy as np
import os
dfl = pd.read_csv('https://github.com/dleshem/israel-alerts-data/raw/refs/heads/main/israel-alerts.csv')
dfy = pd.read_csv('https://github.com/yuval-harpaz/alarms/raw/refs/heads/master/data/alarms.csv')
llen = len(dfl)
dfl = dfl[dfl['alertDate'] > dfy['time'][0][:10]]
dfl.reset_index(drop=True, inplace=True)
# skipped = llen - len(dfl)
commas = ', '.join(dfl['data'][dfl['data'].str.contains(",")].unique())
#take the first 10 characters from alertDate + time to create datetime
dfl['datetime'] = pd.to_datetime(dfl['alertDate'] + ' ' + dfl['time'])
dfy['datetime'] = pd.to_datetime(dfy['time'])
leshemrow = -np.ones(len(dfy), int)
iorigin = -np.ones(len(dfl), int)
start = 0
for ii in range(start, len(dfy)):
    # find a dfy row with cities containd in dfl['data'] and time delta smaller than 30 seconds
    idx_close = np.where(abs(dfy['datetime'][ii] - dfl['datetime']) < pd.Timedelta(seconds=30))[0]
    for jj in idx_close:
        if (dfy['cities'][ii] in commas and dfy['cities'][ii] in dfl['data'][jj]) or dfy['cities'][ii] == dfl['data'][jj]:
            leshemrow[ii] = jj
            if iorigin[jj] == -1:
                iorigin[jj] = ii
            elif dfy['origin'][iorigin[jj]] != dfy['origin'][ii]:
                os.system(f'echo {jj} {dfy["cities"][ii]} {dfy["origin"][ii]} {dfy["origin"][iorigin[jj]]} >> ~/RedAlert/missing_origin.log')
            break
    print(f'{ii}/{len(dfy)}')
for jj in range(len(dfl)):
    if iorigin[jj] > -1:
        dfl.at[jj, 'origin'] = dfy['origin'][iorigin[jj]]
dfl.to_csv('~/RedAlert/leshem_origin.csv', index=False)
dfy['dleshem_row'] = leshemrow # + skipped
dfy.to_csv('~/RedAlert/alarms2leshem.csv', index=False)
## fill by neighbours
# skipped = 4332
dfy = pd.read_csv('~/RedAlert/alarms2leshem.csv')
dfl = pd.read_csv('~/RedAlert/leshem_origin.csv')
# null = dfl.origin.isnull()
# empty = np.unique([dfl['data'][e] for e in range(len(dfl)) if null[e] and dfl['category'][e] == 1])
no_leshem = np.where(dfy['dleshem_row'] < 0)[0]
for ii in range(len(no_leshem)):
    bad = no_leshem[ii]
    if dfy['dleshem_row'][bad+1] - dfy['dleshem_row'][bad-1] == 2:
        new_dlr =  dfy['dleshem_row'][bad-1] + 1
        if new_dlr not in dfy['dleshem_row'].values and dfl['data'][new_dlr] in dfy['cities'][bad]:
            dfy.at[bad, 'dleshem_row'] = new_dlr
            dfl.at[new_dlr, 'origin'] = dfy['origin'][bad]
empty = np.where(dfl['origin'].isnull())[0]
null = dfl['origin'].isnull()
for jj in empty:
    if dfl['time'][jj] == dfl['time'][jj-1] and not null[jj-1]:
        dfl.at[jj, 'origin'] = dfl['origin'][jj-1]
        null[jj] = False
dfl.to_csv('~/RedAlert/leshem_origin.csv', index=False)

 ## fill by coordinates
# dfy = pd.read_csv('~/RedAlert/alarms2leshem.csv')
dfl = pd.read_csv('~/RedAlert/leshem_origin.csv')
coord = pd.read_csv('~/alarms/data/coord.csv')
empty = np.where(dfl['origin'].isnull() & (dfl['alertDate'] < '2023-10-07').values)[0]

lat = coord['lat'].values
long = coord['long'].values
for jj in empty:
    icoord = np.where(coord['loc'] == dfl['data'][jj].split(', ')[0])[0]
    if len(icoord) == 1:
        icoord = icoord[0]
        if lat[icoord] < 31.87 and lat[icoord] > 31.07 and long[icoord] < 34.73:
            dfl.at[jj, 'origin'] = 'Gaza'
        elif lat[icoord] > 32.66:
            dfl.at[jj, 'origin'] = 'Lebanon'
dfl.to_csv('~/RedAlert/leshem_origin.csv', index=False)
print(empty, len(np.where(dfl['origin'].isnull() & (dfl['alertDate'] < '2023-10-07').values)[0]))

##
dfy = pd.read_csv('~/RedAlert/alarms2leshem.csv')
neg = np.where(dfy['dleshem_row'] < 0)[0]
suspect = []
for ii in neg:
    if dfy['dleshem_row'][ii+1] - dfy['dleshem_row'][ii-1] == 1:
        suspect.append(ii)
dfsus = dfy.iloc[np.array(suspect)]
dfsus.to_csv('~/RedAlert/suspect.csv', index=True)
    