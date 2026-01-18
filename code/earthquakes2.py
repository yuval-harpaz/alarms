import pandas as pd
import numpy as np
import os
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
update = pd.read_csv('https://eq.gsi.gov.il/en/earthquake/files/last30_event.csv')
columns = np.array(update.columns)
idate = np.where(columns == 'DateTime')[0]
if len(idate) == 1:
    columns[idate[0]] = 'DateTime(UTC)'
update.columns = columns
local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
df = pd.read_csv('data/earthquakes.csv')
df = df.merge(update, how='outer')
df = df.drop_duplicates(subset=['epiid'], keep='last')
df = df.sort_values('DateTime(UTC)', ignore_index=True)

# Calculate preferred magnitude
mag4 = np.asarray([df['Md'], df['Mb'], df['Mw'], df['Mag']]).T
mag = np.zeros(len(mag4))
M_type = np.zeros(len(mag4), dtype=object)
mags = ['Md','Mb', 'Mw', 'Mag']
mag4[np.isnan(mag4)] = 0

for ii in range(len(mag4)):
    if mag4[ii, 3] > 0:  # prefer Mag
        mag[ii] = mag4[ii, 3]
        M_type[ii] = mags[3]
    elif mag4[ii, 2] > 0:  # Mw
        mag[ii] = mag4[ii, 2]
        M_type[ii] = mags[2]
    else:
        imax = np.argmax(mag4[ii, :2])
        mag[ii] = mag4[ii, imax]
        M_type[ii] = mags[imax]

# Store back to dataframe
df['Mag'] = mag
df['MagType'] = M_type

df.to_csv('data/earthquakes.csv', index=False)
