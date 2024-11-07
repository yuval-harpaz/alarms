import pandas as pd
import os
import numpy as np
import sys
import folium
import requests
import folium


local = '/home/innereye/alarms/'
os.chdir(local)
with open('/home/innereye/alarms/.txt') as f:
    cities_url = f.readlines()[1][:-1]
cities = requests.get(cities_url).json()
fn = '/home/innereye/Documents/shfela.html'
center = [31.916965483870964, 34.8542035967742]
mapsh = folium.Map(location=center, zoom_start=10)
folium.TileLayer('cartodbpositron').add_to(mapsh)
title_html = f'''
         <h3 align="center" style="font-size:20px">
         שפלת יהודה - השפלה
         </h3>
         '''
mapsh.get_root().html.add_child(folium.Element(title_html))
for iarea, area in enumerate(['3', '23']):
    co = ['#ff0000', '#0000ff'][iarea]
    name = cities['areas'][area]['he']
    print(name)
    # fn = f"/home/innereye/Documents/{name.replace(' ', '_')}.html"
    coo = pd.DataFrame(columns=['loc', 'lat', 'lon'])
    for city in cities['cities'].keys():
        if cities['cities'][city]['area'] == int(area):
            row = len(coo)
            coo.at[row, 'loc'] = city
            coo.at[row, 'lat'] = cities['cities'][city]['lat']
            coo.at[row, 'lon'] = cities['cities'][city]['lng']
    for iloc in range(len(coo)):
        lat = coo['lat'].values[iloc]
        long = coo['lon'].values[iloc]
        tip = f"{coo['loc'][iloc]}"
        radius = (1/np.pi)**0.5
        folium.Circle(location=[lat, long],
                      tooltip=tip,
                      radius=float(np.max([radius*750, 1])),
                      fill=True,
                      fill_color=co,
                      color=co,
                      opacity=0,
                      fill_opacity=0.5
                      ).add_to(mapsh)
mapsh.save(fn)

