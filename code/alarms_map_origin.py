import re
from matplotlib import colors
import folium
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import plotly.express as px


local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True
coo = pd.read_csv('data/coord.csv')
def guess_origin(df_toguess):
    toguess = pd.isnull(df_toguess['origin']).values
    row_lat = np.array([coo['lat'][coo['loc'] == x].values[0] for x in df_toguess['cities'].values])
    row_long = np.array([coo['long'][coo['loc'] == x].values[0] for x in df_toguess['cities'].values])
    syria = toguess & (row_long > 35.63) & (row_lat < 33.1)
    lebanon = toguess & (row_lat > 32.69)
    yemen = toguess & (row_lat < 30)
    origin = df_toguess['origin'].values
    origin[toguess] = 'Gaza'
    origin[lebanon] = 'Lebanon'
    origin[syria] = 'Syria'
    origin[yemen] = 'Yemen'
    df_toguess['origin'] = origin
    return df_toguess


dfwar = pd.read_csv('data/alarms.csv')
dfwar = guess_origin(dfwar)
dfwar.to_csv('data/alarms.csv', index=False, sep=',')
last_alarm = pd.to_datetime(dfwar['time'][len(dfwar)-1])
last_alarm = last_alarm.tz_localize('Israel')
dfwar = dfwar[dfwar['threat'] == 0]
dfwar = dfwar[dfwar['time'] >= '2023-10-07 00:00:00']
dfwar = dfwar.reset_index(drop=True)
now = np.datetime64('now', 'ns')
nowisr = pd.to_datetime(now, utc=True, unit='s').astimezone(tz='Israel')
nowstr = str(nowisr)[:16].replace('T', ' ')
origin = np.array([str(x) for x in dfwar['origin']])
origu = np.unique(origin)

##
# Make map
title_html = f'''
             <h3 align="center" style="font-size:16px"><b>Rocket alarms in Israel by origin, data from <a href="https://www.oref.org.il" target="_blank">THE NATIONAL EMERGENCY PORTAL</a>
             via <a href="https://www.tzevaadom.co.il/" target="_blank">צבע אדום</a>. last checked: {nowstr}</b></h3>
             '''
gnames = origu
co = [[0.8, 0.2, 0.2], [0.2, 0.8, 0.2], [0.2, 0.2, 0.8], [0, 0, 0], [0.75, 0.75, 0.25], [0.82, 0.5, 0.35],
      [1.0, 0.25, 0.25]]
chex = []
for c in co:
    chex.append(colors.to_hex(c))
lgd_txt = '<span style="color: {col};">{txt}</span>'
grp = []
for ic, gn in enumerate(gnames):
    grp.append(folium.FeatureGroup(name=lgd_txt.format(txt=gn, col=chex[ic])))

center = [coo['lat'].mean(), coo['long'].mean()]
##
map = folium.Map(location=center, zoom_start=7.5)
folium.TileLayer('cartodbpositron').add_to(map)
folium.TileLayer('openstreetmap').add_to(map)
folium.TileLayer('https://tile.openstreetmap.de/{z}/{x}/{y}.png',
                 attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors').add_to(map)
# for tile in tiles:
#     folium.TileLayer(tile).add_to(map)
map.get_root().html.add_child(folium.Element(title_html))

for igroup in range(len(origu)):
    # idx = (yyyy == year)
    dt = gnames[igroup]
    idx = origin == origu[igroup]
    loc = np.asarray(dfwar['cities'][idx])
    locu = np.unique(loc)
    size = np.zeros(len(locu), int)
    for iloc in range(len(locu)):
        row_coo = coo['loc'] == locu[iloc]
        if np.sum(row_coo) == 1:
            size[iloc] = np.sum(loc == locu[iloc])
            lat = float(coo['lat'][row_coo])
            long = float(coo['long'][coo['loc'] == locu[iloc]])
            tip = locu[iloc]+'('+dt + '):  ' + str(size[iloc])  # + str(mag[ii]) + depth  + '<br> '
            folium.CircleMarker(location=[lat, long],
                                tooltip=tip,
                                radius=float(np.max([size[iloc]**0.5*2, 1])),
                                fill=True,
                                fill_color=chex[igroup],
                                color=chex[igroup],
                                opacity=0,
                                fill_opacity=0.5
                                ).add_to(grp[igroup])
        else:
            print('cannot find coord for '+locu[iloc])

for ig in range(len(gnames)):
    grp[ig].add_to(map)
folium.map.LayerControl('topleft', collapsed=False).add_to(map)
html_name = "docs/alarms_origin.html"
map.save(html_name)
with open(html_name, 'r') as fid:
    html = fid.read()
osmde = 'https://tile.openstreetmap.de/{z}/{x}/{y}.png'  # 'openstreetmap.de'
idx = [m.start() for m in re.finditer(osmde, html)]
html = html[:idx[1]] + html[idx[1]:].replace(osmde, 'openstreetmap.de')
with open(html_name, 'w') as fid:
    fid.write(html)
print('done')
