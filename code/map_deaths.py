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
from alarms_coord import update_coord


def map_deaths():
    df = pd.read_csv('data/deaths.csv')
    coo = pd.read_csv('data/coord.csv')
    locs = [x for x in df['from'] if type(x) == str]
    locu = np.unique(locs)
    # found = np.zeros(len(df), bool)
    # c = 0
    # for loc in locu:
    #     if np.any(coo['loc'] == loc):
    #         found[c] = True
    #     else:
    #         print(f'{loc} not found')

    update_coord(latest=locu, coord_file='data/coord_deaths.csv')


    coo = pd.read_csv('data/coord_deaths.csv')
    center = [coo['lat'].mean(), coo['long'].mean()]
    ##
    map = folium.Map(location=center, zoom_start=7.5)#, tiles='openstreetmap')
    # tiles = ['cartodbpositron', 'stamenterrain']
    # folium.TileLayer('cartodbpositron').add_to(map)
    folium.TileLayer('https://tile.openstreetmap.de/{z}/{x}/{y}.png',
                     attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors').add_to(map)
    # for tile in tiles:
    #     folium.TileLayer(tile).add_to(map)
    now = np.datetime64('now', 'ns')
    nowisr = pd.to_datetime(now, utc=True, unit='s').astimezone(tz='Israel')
    nowstr = str(nowisr)[:16].replace('T', ' ')
    title_html = f'''
                 <h3 align="center" style="font-size:16px"><b>War deaths in Israel since 7-Oct-23, by residence. data from <a href="https://ynet-projects.webflow.io/news/attackingaza" target="_blank">ynet</a>
                 . last checked: {nowstr}</b></h3>
                 '''

    map.get_root().html.add_child(folium.Element(title_html))


    # idx = (yyyy == year)
    # dt = date_list[idate]
    # idx = date == date_list[idate]
    # print(sum(idx))
    # locs = np.asarray(prev['cities'][idx])
    # locu = np.unique(loc)
    locs = np.array(locs)
    size = np.zeros(len(locu), int)
    for iloc in range(len(locu)):
        row_coo = coo['loc'] == locu[iloc]
        if np.sum(row_coo) == 1:
            size[iloc] = np.sum(locs == locu[iloc])
            lat = float(coo['lat'][row_coo])
            long = float(coo['long'][coo['loc'] == locu[iloc]])
            tip = f'{locu[iloc]}  {size[iloc]}'  # + str(mag[ii]) + depth  + '<br> '
            folium.CircleMarker(location=[lat, long],
                                tooltip=tip,
                                radius=1.5*float(np.max([size[iloc]**0.5*2, 1])),
                                fill=True,
                                fill_color='#ff0000',
                                color='#ff0000',
                                opacity=0,
                                fill_opacity=0.5
                                ).add_to(map)
        else:
            print('cannot find coord for '+locu[iloc])

    # folium.map.LayerControl('topleft', collapsed=False).add_to(map)
    map.save("docs/war_deaths23.html")
    # with open('docs/war_deaths23.html', 'r') as fid:
    #     html = fid.read()
    # # reploc = html.index('https://tile.openstreetmap.de/{z}/{x}/{y}.png')
    # html.replace('https://tile.openstreetmap.de/{z}/{x}/{y}.png', 'openstreetmap.de')
    # with open('docs/war_deaths23.html', 'w') as fid:
    #     fid.write(html)
    print('done')


if __name__ == '__main__':
    map_deaths()