import requests
from matplotlib import colors
import folium
import pandas as pd
import numpy as np
import os
from datetime import datetime

now_date = datetime.now().strftime("%d.%m.%Y")
start = True
halfs = [[[1,1],[30,6]],[[1,7], [31,12]]]
mont = [0,1,2,3,4,5,6,7,8,9,10,11,12,1]
for year in range(2019, 2024):
    for month in range(1,13):
        alerts_url = f'https://www.oref.org.il//Shared/Ajax/GetAlarmsHistory.aspx?lang=he&fromDate=02.{str(month)}.{str(year)}&toDate=02.{str(mont[month+1])}.{str(year)}&mode=0'
        alerts_json = requests.get(alerts_url).json()
        # Break multi-region alerts into separate records
        df = pd.DataFrame.from_records(alerts_json)
        if len(df) > 0:
            df['data'] = df['data'].str.split(',')
            df = df.explode('data')
            # Remove sub-regions such as א, ב, ג, ד
            df = df[df['data'].str.len() > 2]
            # Change Hatzor to detailed name as the google geocoder fail to detect the correct city
            df['data'] = df['data'].replace('חצור', 'חצור אשדוד')
            if start:
                df['data'] = df['data'].str.replace(r'\s+\d+$', '')
                prev = df.copy()
                start = False
            else:
                prev = prev.merge(df, how='outer')
            print(str(year)+' '+str(month)+' '+str(len(df)))

# prevv = prev.copy()
year = 2021
month = 5
start = True
ds = []
for day in range(1, 32):
    alerts_url = f'https://www.oref.org.il//Shared/Ajax/GetAlarmsHistory.aspx?lang=he&fromDate={day}.05.2021&toDate={day}.05.2021&mode=0'
    alerts_json = requests.get(alerts_url).json()
    df = pd.DataFrame.from_records(alerts_json)
    if len(df) > 0:
        df['data'] = df['data'].str.split(',')
        df = df.explode('data')
        df = df[df['data'].str.len() > 2]
        df['data'] = df['data'].replace('חצור', 'חצור אשדוד')
        if start:
            prevv = df
            start = False
        else:
            prevv = prevv.merge(df, how='outer')
        print(str(day) + ' ' + str(len(df)))
        ds.append(len(df))
prev = prev.merge(prevv, how='outer')
prev.sort_values('rid', inplace=True)
prev.to_csv('/home/innereye/alarms/data/alarms_from_2019.csv', index=False, sep=',')
## after deleting old format rows manually
prev = pd.read_csv('/home/innereye/alarms/data/alarms_from_2019.csv')

with open('/home/innereye/alarms/oath.txt') as f:
    oath = f.readlines()[0][:-1]
def get_coordinates(city_name):
    city_name = city_name + ', ישראל'
    geocoder_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={city_name}&key={oath}&language=iw'
    geocoding_result = requests.get(geocoder_url).json()
    lat = geocoding_result['results'][0]['geometry']['location']['lat']
    long = geocoding_result['results'][0]['geometry']['location']['lng']
    return(lat, long)

coo.sort_values('loc', inplace=True)
coo = pd.read_csv('/home/innereye/alarms/data/coord.csv')


# failed = ['מגן','שובה','אזור תעשייה צמח','זוהר']

city_to_coords = {}
for city in prev['data'].unique():
    if city not in coo['loc'].values:
        try:
            city_to_coords[city] = get_coordinates(city)
            print(city, '\t -', city_to_coords[city], end='\r')
        except Exception as e:
            city_to_coords[city] = (None, None)
            print(city, '\t', '- failed finding coordinates')
# lat, long = get_coordinates('רחובות')
# coo = pd.DataFrame(city_to_coords, columns=['loc','coord'])
for new in list(city_to_coords.keys()):
    if new in coo['loc'].values:
        print(new+' '+'exists')
coo1 = pd.DataFrame(list(city_to_coords.keys()), columns=['loc'])
coo1['lat'] = 0.0
coo1['long'] = 0.0
for icity, city in enumerate(coo1['loc']):
    try:
        coo1['lat'][icity] = city_to_coords[city][0]
        coo1['long'][icity] = city_to_coords[city][1]
    except:
        print('failed '+city)

coo = coo.merge(coo1, how='outer')
coo.sort_values('loc', inplace=True)
coo.to_csv('/home/innereye/alarms/data/coord.csv', index=False, sep=',')


# alerts_url = f'https://www.oref.org.il//Shared/Ajax/GetAlarmsHistory.aspx?lang=he&fromDate=01.01.2014&toDate={now_date}&mode=0'
# googlemaps = pd.read_json('https://maps.googleapis.com/maps/api/geocode/json?address='+location[0]+'&key='+oath+'&language=iw')
# getakeythere = 'https://www.npmjs.com/package/googleapis'
# oref_python = 'https://github.com/SgtTepper/RedAlert/blob/main/OrefAlerts.ipynb'
#
# update = pd.read_csv('https://eq.gsi.gov.il/en/earthquake/files/last30_event.csv')
#
# local = '/home/innereye/alarms/'
# if os.path.isdir(local):
#     os.chdir(local)
# df = pd.read_csv('data/earthquakes.csv')
# df = df.merge(update, how='outer')
# dt = pd.to_datetime(df['DateTime']).to_numpy()
# mag3 = np.asarray([df['Md'], df['Mb'], df['Mw']]).T
# mag = np.max(mag3, axis=1)
# imax = np.argmax(mag3, axis=1)
# mag[mag3[:, 2] > 0] = mag3[mag3[:, 2] > 0, 2]
# M = []  # take Mw when possible
# for ii in range(len(dt)):
#     if mag3[ii, 2] == 0:
#         M.append(df.columns[2+imax[ii]])
#     else:
#         M.append('Mw')
# now = np.datetime64('now', 'ns')
# dif = now-dt
# dif_sec = dif.astype('timedelta64[s]').astype(float)
# dif_days = dif_sec/60**2/24
# # lin = dif.copy().astype(int)
# group_index = np.ones(len(dif_days), int)*4
# four = np.zeros((len(dif_days), 4))
# four[:, 2] = 1
# four[:, 3] = 0.2
# ccc = [365, 30, 7, 1]
# co = [[0, 1, 0.5, 1], [1, 0.75, 0.5, 1], [1, 0, 0, 1], [0, 0, 0, 1]]
# for ii, cc in enumerate(ccc):
#     for ll in range(4):
#         four[dif_days <= ccc[ii], ll] = co[ii][ll]
#         group_index[dif_days <= ccc[ii]] = 3-ii
#
# title_html = '''
#              <h3 align="center" style="font-size:16px"><b>Earthquakes measured in Israel since 2000, data from <a href="https://eq.gsi.gov.il/heb/earthquake/lastEarthquakes.php" target="_blank">THE GEOLOGICAL SURVEY OF ISRAEL</a></b></h3>
#              '''
#
# lgd_txt = '<span style="color: {col};">{txt}</span>'
# gnames = ['one day', 'one week', 'one month', 'one year', 'more than a year']
# chex = [colors.to_hex([0, 0, 1])]
# for c in co:
#     chex.append(colors.to_hex(c))
# lgd_txt = '<span style="color: {col};">{txt}</span>'
# grp = []
# for ic, gn in enumerate(gnames):
#     grp.append(folium.FeatureGroup(name=lgd_txt.format(txt=gn, col=chex[4-ic])))
# center = [df['Lat'].mean(), df['Long'].mean()]
# map = folium.Map(location=center, zoom_start=7.5, tiles='openstreetmap')
# tiles = ['cartodbpositron', 'stamenterrain']
# for tile in tiles:
#     folium.TileLayer(tile).add_to(map)
# map.get_root().html.add_child(folium.Element(title_html))
# for ii in range(len(df)):
#     # sz = df['Md'][ii]
#     lat = df['Lat'][ii]
#     lon = df['Long'][ii]
#     # dt = df['DateTime'][ii]
#     c = colors.to_hex(four[ii, :3])
#     depth = ''
#     d = df['Depth(Km)'][ii]
#     if d > 0:
#         depth = ', depth: '+str(d)+'Km'
#     tip = df['DateTime'][ii][:-4].replace('T', ' ')
#     tip = tip+'<br> '+M[ii]+': '+str(mag[ii])+depth
#     folium.CircleMarker(location=[lat, lon],
#                         tooltip=tip,
#                         radius=mag[ii]**2/2,
#                         fill=True,
#                         fill_color=c,
#                         color=c,
#                         opacity=four[ii, 3],
#                         fill_opacity=four[ii, 3]
#                         ).add_to(grp[group_index[ii]])
# for ig in range(5):
#     grp[4-ig].add_to(map)
# folium.map.LayerControl('topleft', collapsed=False).add_to(map)
# map.save("docs/earthquakes_by_time.html")
# df.to_csv('data/earthquakes.csv', index=False)
