import pandas as pd
import os
import numpy as np
import sys
import folium

local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True
    sys.path.append(local + 'code')

coo = pd.read_excel('data/deaths_by_loc.xlsx', 'data')

# coo = pd.read_csv('data/deaths_by_loc.csv')
center = [coo['lat'].mean(), coo['long'].mean()]
##
map = folium.Map(location=center, zoom_start=10)
folium.TileLayer('cartodbpositron').add_to(map)
now = np.datetime64('now', 'ns')
nowisr = pd.to_datetime(now, utc=True, unit='s').astimezone(tz='Israel')
nowstr = str(nowisr)[:16].replace('T', ' ')
title_html = f'''
             <h3 align="center" style="font-size:16px"><b>Deaths between 7-Oct-23 and 9-Oct-23. data from <a href="https://oct7names.co.il/" target="_blank">ואלה שמות</a> and other sources
             . last update: {nowstr}</b></h3>
             '''
map.get_root().html.add_child(folium.Element(title_html))
for iloc in range(len(coo)):
    lat = float(coo['lat'][iloc])
    long = float(coo['long'][iloc])
    tip = f'{coo["name"][iloc]}  {coo["deaths"][iloc]}'
    radius = (coo["deaths"][iloc]/np.pi)**0.5
    if coo['army'][iloc]:
        color = "#808000"
    else:
        color = "#ff0000"
    folium.Circle(location=[lat, long],
                        tooltip=tip,
                        radius=float(np.max([radius*300, 1])),
                        fill=True,
                        fill_color=color,
                        color=color,
                        opacity=0,
                        fill_opacity=0.35
                        ).add_to(map)

map.save("docs/oct_7_9.html")

