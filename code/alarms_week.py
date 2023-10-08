import os
import requests
from matplotlib import colors
import folium
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import plotly.express as px
import sys


# from bs4 import BeautifulSoup
# from selenium import webdriver
# dr = webdriver.Chrome()
# # dr.get("https://www.mobile.de/?lang=en")
# dr.get("https://api.tzevaadom.co.il/alerts-history")


local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True
prev = pd.read_csv('data/alarms.csv')
last_alarm = pd.to_datetime(prev['time'][len(prev)-1])
last_alarm = last_alarm.tz_localize('Israel')
# tzeva = requests.get('https://api.tzevaadom.co.il/alerts-history')
# # print(tzeva.text[:100])
# if tzeva.text[:5] == '[{"id':
#     tzeva = tzeva.json()
# else:
#     if ' 522:' in tzeva.text:
#         message = tzeva.text[tzeva.text.index(' 522:'):]
#         message = message[:message.index('<')]
#     else:
#         message = tzeva.text
#     raise Exception(message)
#
# df = pd.DataFrame(tzeva)
# df = df.explode('alerts')
# df1 = pd.DataFrame(list(df['alerts']))
# dt = np.asarray([pd.to_datetime(ds, utc=True, unit='s').astimezone(tz='Israel') for ds in df1['time']])
# id = np.asarray(df['id'])
# new = np.where(dt > last_alarm)[0]
# if len(new) > 0:
#     for n in new[::-1]:
#         citiesc = df1['cities'][n]
#         x = []
#         for cit in citiesc:
#             x.extend(cit.split(', '))
#         citiesc = np.unique(x)
#         idc = id[n]
#         dtc = dt[n].replace(tzinfo=None)
#         threatc = df1['threat'][n]
#         # if df['description'][n] is None:
#         if threatc == 0:
#             desc = 'ירי רקטות וטילים'
#         elif threatc == 2:
#             desc = 'חדירת מחבלים'
#         elif threatc == 5:
#             desc = 'חדירת כלי טיס עוין'
#         else:
#             desc = ''
#         for cit in citiesc:
#             prev.loc[len(prev.index)] = [str(dtc), cit, threatc, idc, desc]
#     with_duplicates = len(prev)
#     prev = prev.drop_duplicates(keep='first', ignore_index=True)
#     if len(prev) < with_duplicates:
#         print(f'{with_duplicates-len(prev)} duplicates')
#     prev = prev.sort_values('time', ignore_index=True)
#     prev.to_csv('data/alarms.csv', index=False, sep=',')
#
#     news = True
# else:
#     news = False
#
# if islocal:
#     sys.path.append(local+'code')
# from alarms_coord import update_coord
# update_coord()


prev = prev[prev['threat'] == 0]
prev = prev.reset_index(drop=True)
# yyyy = np.array([int(str(date)[:4]) for date in prev['time']])
# mm = np.array([int(str(date)[5:7]) for date in prev['time']])
date = np.array([d[:10] for d in prev['time']])
last7dates = np.unique(date)[-7:]
now = np.datetime64('now', 'ns')
nowisr = pd.to_datetime(now, utc=True, unit='s').astimezone(tz='Israel')
nowstr = str(nowisr)[:16].replace('T', ' ')
# dt = pd.to_datetime(prev['time']).to_numpy()
# dif = np.datetime64(nowstr) - dt
# dif_sec = dif.astype('timedelta64[s]').astype(float)
# dif_days = dif_sec / 60 ** 2 / 24
# past_24h = dif_days <= 1
# past_7d = dif_days <= 7

current_date = datetime.now()
date_list = []
for _ in range(7):
    date_list.append(current_date.strftime('%Y-%m-%d'))
    current_date -= timedelta(days=1)

# Reverse the list to have the dates in descending order
date_list.reverse()
# Prin
nid = []
n = []
for day in range(7):
    idx = date == date_list[day]
    nid.append(len(np.unique(prev['id'][idx])))
    n.append(np.sum(idx))


fig = px.bar(x=date_list, y=n, log_y=True)
# fig = px.bar(prev, y=n, x='date',log_y=True)
html = fig.to_html()
file = open('docs/alarms_last_7_days.html', 'w')
a = file.write(html)
file.close()
##
# Make map
title_html = f'''
             <h3 align="center" style="font-size:16px"><b>Rocket alarms in Israel for the last 7 days, data from <a href="https://www.oref.org.il" target="_blank">THE NATIONAL EMERGENCY PORTAL</a>
             via <a href="https://www.tzevaadom.co.il/" target="_blank">צבע אדום</a>. last checked: {nowstr}</b></h3>
             '''
gnames = date_list
co = [[0.25, 0.25, 1.0], [0.25, 0.9, 0.8], [0.25, 1, 0.25], [0.75, 0.75, 0.25], [0.82, 0.5, 0.35],
      [1.0, 0.25, 0.25], [0, 0, 0]]
chex = []
for c in co:
    chex.append(colors.to_hex(c))
lgd_txt = '<span style="color: {col};">{txt}</span>'
grp = []
for ic, gn in enumerate(gnames):
    grp.append(folium.FeatureGroup(name=lgd_txt.format(txt=gn, col=chex[ic])))

coo = pd.read_csv('data/coord.csv')
center = [coo['lat'].mean(), coo['long'].mean()]
##
map = folium.Map(location=center, zoom_start=7.5, tiles='openstreetmap')
tiles = ['cartodbpositron', 'stamenterrain']
for tile in tiles:
    folium.TileLayer(tile).add_to(map)
map.get_root().html.add_child(folium.Element(title_html))

for idate in range(7):
    # idx = (yyyy == year)
    dt = date_list[idate]
    idx = date == date_list[idate]
    print(sum(idx))
    loc = np.asarray(prev['cities'][idx])
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
                                fill_color=chex[idate],
                                color=chex[idate],
                                opacity=0.5,
                                fill_opacity=0.5
                                ).add_to(grp[idate])
        else:
            print('cannot find coord for '+locu[iloc])

for ig in range(len(gnames)):
    grp[ig].add_to(map)
folium.map.LayerControl('topleft', collapsed=False).add_to(map)
map.save("docs/alarms_7_days.html")
print('done')
