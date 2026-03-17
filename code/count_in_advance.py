import pandas as pd
import numpy as np
import io
import requests

url = 'https://raw.githubusercontent.com/dleshem/israel-alerts-data/main/israel-alerts.csv'
# response = requests.get(url)
# response.raise_for_status()  # Raise an exception for HTTP errors
# csv_content = response.content.decode('utf-8')
df = pd.read_csv(url)
# Filter for category 14 events
df14 = df[df['category'] == 14].copy()
# Convert 'alertDate' to datetime objects
df14['date_orig'] = df14['date']
df14['time_orig'] = df14['time']
df14['datetime'] = pd.to_datetime(df14['date'] + ' ' + df14['time'], dayfirst=True)
df14['date'] = pd.to_datetime(df14['date'], dayfirst=True)
# Filter for dates from Feb 28 2026 onwards
start_date = pd.to_datetime('2026-02-28')
df14 = df14[df14['date'] >= start_date]
df14 = df14[df14['category_desc'].str.contains('בדקות הקרובות')]
df14 = df14.reset_index(drop=True)
datetimes = np.unique(df14['datetime'])
#find differences larger than 60sec in datetimes
difs = [0] + [int(i)+1 for i in np.where(np.diff(datetimes) > np.timedelta64(60, 's'))[0]]
dfc = pd.DataFrame(columns=['date', 'from_time', 'to_time', 'n locations'])
for idt in range(len(difs)):
    start_idx = difs[idt]
    if idt == len(difs)-1:
        end_idx = len(datetimes)
    else:
        end_idx = difs[idt + 1]
    locations = []
    for jdt in range(start_idx, end_idx):
        locations.extend(list(df14['data'][df14['datetime'] == datetimes[jdt]]))
    row = len(dfc)
    dt = datetimes[start_idx]
    dfc.at[row, 'date'] = str(np.datetime_as_string(dt, unit='D'))
    dfc.at[row, 'from_time'] = str(np.datetime_as_string(dt)).split('T')[1].split('.')[0]
    dfc.at[row, 'to_time'] = str(np.datetime_as_string(datetimes[end_idx-1])).split('T')[1].split('.')[0]
    dfc.at[row, 'n locations'] = len(np.unique(locations))
    # if len(locations) != len(np.unique(locations)):
    #     print(dt)
print(dfc)
dfc.to_csv('~/Documents/iac.csv', index=False)

