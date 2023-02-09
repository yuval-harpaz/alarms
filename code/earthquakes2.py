
from matplotlib import colors
import folium
import pandas as pd
import numpy as np
import os

update = pd.read_csv('https://eq.gsi.gov.il/en/earthquake/files/last30_event.csv')

local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
df = pd.read_csv('data/earthquakes.csv')
df = df.merge(update, how='outer')
dt = pd.to_datetime(df['DateTime']).to_numpy()
mag = np.max(np.asarray([df['Md'], df['Mb'], df['Mw']]), axis=0)
now = np.datetime64('now', 'ns')
dif = now-dt
dif = dif.astype('timedelta64[D]')
lin = dif.copy().astype(int)
group_index = np.ones(len(lin), int)*4
four = np.zeros((len(lin), 4))
four[:, 2] = 1
four[:, 3] = 0.2
ccc = [365, 30, 7, 1]
co = [[0, 1, 0.5, 1], [1, 0.75, 0.5, 1], [1, 0, 0, 1], [0, 0, 0, 1]]
for ii, cc in enumerate(ccc):
    for ll in range(4):
        four[lin <= ccc[ii], ll] = co[ii][ll]
        group_index[lin <= ccc[ii]] = 3-ii

title_html = '''
             <h3 align="center" style="font-size:16px"><b>Earthquakes measured in Israel since 2000</b></h3>
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
map = folium.Map(location=center, zoom_start=7.5)
map.get_root().html.add_child(folium.Element(title_html))
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
                        ).add_to(grp[group_index[ii]])
for ig in range(5):
    grp[ig].add_to(map)
folium.map.LayerControl('topleft', collapsed=False).add_to(map)
map.save("docs/tmp.html")
# df.to_csv('data/tmp.csv', index=False)