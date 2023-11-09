
from matplotlib import colors
import folium
import pandas as pd
import numpy as np
import os
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
update = pd.read_csv('https://eq.gsi.gov.il/en/earthquake/files/last30_event.csv')

local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
df = pd.read_csv('data/earthquakes.csv')
df = df.merge(update, how='outer')
dt = pd.to_datetime(df['DateTime']).to_numpy()
mag3 = np.asarray([df['Md'], df['Mb'], df['Mw']]).T
mag = np.max(mag3, axis=1)
imax = np.argmax(mag3, axis=1)
mag[mag3[:, 2] > 0] = mag3[mag3[:, 2] > 0, 2]
M = []  # take Mw when possible
for ii in range(len(dt)):
    if mag3[ii, 2] == 0:
        M.append(df.columns[2+imax[ii]])
    else:
        M.append('Mw')
now = np.datetime64('now', 'ns')
nowisr = pd.to_datetime(now, utc=True, unit='s').astimezone(tz='Israel')
# dtc = dt[n].replace(tzinfo=None)
# dt = np.asarray([pd.to_datetime(ds, utc=True, unit='s').astimezone(tz='Israel') for ds in df1['time']])
nowstr = str(nowisr)[:16].replace('T', ' ')
dif = now-dt
dif_sec = dif.astype('timedelta64[s]').astype(float)
dif_days = dif_sec/60**2/24
# lin = dif.copy().astype(int)
group_index = np.ones(len(dif_days), int)*4
four = np.zeros((len(dif_days), 4))
four[:, 2] = 1
four[:, 3] = 0.2
ccc = [365, 30, 7, 1]
co = [[0, 1, 0.5, 1], [1, 0.75, 0.5, 1], [1, 0, 0, 1], [0, 0, 0, 1]]
for ii, cc in enumerate(ccc):
    for ll in range(4):
        four[dif_days <= ccc[ii], ll] = co[ii][ll]
        group_index[dif_days <= ccc[ii]] = 3-ii

title_html = f'''
             <h3 align="center" style="font-size:16px"><b>Earthquakes measured in Israel since 2000, data from <a href="https://eq.gsi.gov.il/heb/earthquake/lastEarthquakes.php" target="_blank">THE GEOLOGICAL SURVEY OF ISRAEL</a>. last checked: {nowstr}</b></h3>
             '''

lgd_txt = '<span style="color: {col};">{txt}</span>'
gnames = ['one day', 'one week', 'one month', 'one year', 'more than a year']
chex = [colors.to_hex([0, 0, 1])]
for c in co:
    chex.append(colors.to_hex(c))
lgd_txt = '<span style="color: {col};">{txt}</span>'
grp = []
for ic, gn in enumerate(gnames):
    grp.append(folium.FeatureGroup(name=lgd_txt.format(txt=gn, col=chex[4-ic])))
center = [df['Lat'].mean(), df['Long'].mean()]
map = folium.Map(location=center, zoom_start=7.5, tiles='openstreetmap')
tiles = ['cartodbpositron', 'stamenterrain']
for tile in tiles:
    folium.TileLayer(tile).add_to(map)
map.get_root().html.add_child(folium.Element(title_html))
for ii in range(len(df)):
    # sz = df['Md'][ii]
    lat = df['Lat'][ii]
    lon = df['Long'][ii]
    # dt = df['DateTime'][ii]
    c = colors.to_hex(four[ii, :3])
    depth = ''
    d = df['Depth(Km)'][ii]
    if d > 0:
        depth = ', depth: '+str(d)+'Km'
    tip = df['DateTime'][ii][:-4].replace('T', ' ')
    tip = tip+'<br> '+M[ii]+': '+str(mag[ii])+depth
    folium.CircleMarker(location=[lat, lon],
                        tooltip=tip,
                        radius=mag[ii]**2/2,
                        fill=True,
                        fill_color=c,
                        color=c,
                        opacity=four[ii, 3],
                        fill_opacity=four[ii, 3]
                        ).add_to(grp[group_index[ii]])
for ig in range(5):
    grp[4-ig].add_to(map)
folium.map.LayerControl('topleft', collapsed=False).add_to(map)
map.save("docs/earthquakes_by_time.html")
df.to_csv('data/earthquakes.csv', index=False)
