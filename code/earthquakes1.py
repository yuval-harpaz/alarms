
from matplotlib import colors
import folium
import pandas as pd
import numpy as np
import os

update = pd.read_csv('https://eq.gsi.gov.il/en/earthquake/files/last30_event.csv')

local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
df = pd.read_csv('data/rslt_8320.csv')
df = df.merge(update, how='outer')

# id = np.asarray(update['epiid'])
# id = [x[1:-1] for x in id]
# c = 0
# for ii in range(len(df)):
#     if df['epiid'][ii][1:-1] in id:
#         c+=1
# print(c)

dt = pd.to_datetime(df['DateTime']).to_numpy()
mag = np.max(np.asarray([df['Md'], df['Mb'], df['Mw']]), axis=0)
now = np.datetime64('now', 'ns')
dif = now-dt
dif = dif.astype('timedelta64[D]')
lin = dif.copy().astype(int)
four = np.zeros((len(lin), 4))
four[:, 2] = 1
four[:, 3] = 0.2
ccc = [365, 30, 7, 1]
co = [[0, 1, 0.5, 1], [1, 0.75, 0.5, 1], [1, 0, 0, 1], [0, 0, 0, 1]]
for ii, cc in enumerate(ccc):
    for ll in range(4):
        four[lin <= ccc[ii], ll] = co[ii][ll]

center = [df['Lat'].mean(), df['Long'].mean()]
map = folium.Map(location=center, zoom_start=7.5)
for ii in range(len(df)):
    # sz = df['Md'][ii]
    lat = df['Lat'][ii]
    lon = df['Long'][ii]
    # dt = df['DateTime'][ii]
    c = colors.to_hex(four[ii,:3])
    folium.CircleMarker(location=[lat, lon],
                        radius=mag[ii]**2/2,
                        fill=True,
                        fill_color=c,
                        color=c,
                        opacity=four[ii, 3],
                        fill_opacity=four[ii, 3]
                        ).add_to(map)
map.save("docs/earthquakes_by_time.html")
