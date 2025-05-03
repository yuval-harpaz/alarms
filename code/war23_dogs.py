import pandas as pd
import os
import numpy as np
import sys
import folium
# import requests

local = '/home/innereye/alarms/'
os.chdir(local)
# islocal = False
# fn = 'טבלת אקסל סופית מצומצמת של כלבים שנרצחו ב7.10 לדר הרפז נכון ל 6.10.24.xlsx'
fn = 'data/dogs.csv'
df = pd.read_csv(fn)
df['שם יישוב'] = df['שם יישוב'].str.strip()
df.to_csv(fn, index=False)
status = []
for ii in range(len(df)):
    missing = df['נעדר'][ii]
    if str(missing) == 'nan':
        status.append('נרצח')
    elif ' ששב' in missing or ' שחזר' in missing:
        status.append('חטוף ששב')
    else:
        status.append('נעדר')
# df = pd.read_excel('~/Documents/טבלת אקסל סופית של כלבים שנרצחו ב7.10 נכון ל 6.10.24.xlsx')
coo = pd.read_csv('data/coord.csv')
locs = df['שם יישוב'].values
keep = []
for ii in range(len(coo)):
    if coo['loc'][ii] in locs:
        keep.append(True)
    else:
        keep.append(False)
coo = coo[keep]
# df = pd.read_csv('data/deaths.csv')

# locs = [x.replace('קיבוץ ','').replace('מושב ','').replace('קריית','קרית') for x in df['from'] if type(x) == str]
# # locs = [x for x in df['from'].replace('קיבוץ', '').replace('מושב', '').strip() if type(x) == str]
locu = np.unique(locs)
# coo = pd.read_csv('data/coord_deaths.csv')
center = [coo['lat'].mean(), coo['long'].mean()]
##
map = folium.Map(location=center, zoom_start=10)#, tiles='openstreetmap')
# folium.TileLayer('https://tile.openstreetmap.de/{z}/{x}/{y}.png',
#                  attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors').add_to(map)
# folium.TileLayer('openstreetmap').add_to(map)
folium.TileLayer('cartodbpositron').add_to(map)
now = np.datetime64('now', 'ns')
nowisr = pd.to_datetime(now, utc=True, unit='s').astimezone(tz='Israel')
nowstr = str(nowisr)[:16].replace('T', ' ')
status = np.array(status)
missing = np.sum(status == 'נעדר')
killed = np.sum(status == 'נרצח')
returned = np.sum(status == 'חטוף ששב')
title_html = f'''
             <h3 align="center" style="font-size:20px">
             כלבים שנרצחו בשבעה באוק' או שנעדרים מאז.
             
               <a href="https://docs.google.com/spreadsheets/d/1jOXg2FVlNapTrSAbRdUyqwaEik-sjz1PU8pGeSR-wMQ/edit?usp=sharing" target="_blank">            
             טבלת נתונים
             </a>
            <h3 align="center" style="font-size:12px">
            בטבח נרצחו {killed} כלבים, {returned} נחטפו ושבו, ויש {missing} נעדרים
            <br>
            כל היודע מידע נוסף על כלבים שנרצחו או נעדרים בשל אירועי ה-7/10, מתבקש לפנות לתמי בר-יוסף 
            <a href="mailto:tammybj@gmail.com" target="_blank">במייל</a> או באתר <a href="https://www.humandogreaserch.org/">המרכז לחקר יחסי אדם וכלב בישראל ובשואה</c>
             </a></h3>
             '''
map.get_root().html.add_child(folium.Element(title_html))
# locs = np.array(locs)
size = np.zeros(len(locu), int)

for iloc in range(len(locu)):
    row_coo = coo['loc'] == locu[iloc]
    if np.sum(row_coo) == 1:
        size[iloc] = np.sum(locs == locu[iloc])
        lat = float(coo['lat'].values[row_coo][0])
        long = float(coo['long'].values[row_coo][0])
        tip = f'{locu[iloc]}  {size[iloc]}<br>'
        rows_dogs = np.where(locs == locu[iloc])[0]
        for row_dog in rows_dogs:
            tip += f"{df['שם הכלב'][row_dog]}, {df['גיל'][row_dog]}, {status[row_dog]}, ({df['שם משפחה'][row_dog]})<br>"
        tip = tip[:-4]
        radius = (size[iloc]/np.pi)**0.5
        folium.Circle(location=[lat, long],
                            tooltip=tip,
                            radius=float(np.max([radius*750, 1])),
                            fill=True,
                            fill_color='#ff0000',
                            color='#ff0000',
                            opacity=0,
                            fill_opacity=0.5
                            ).add_to(map)
    else:
        print('cannot find coord for '+locu[iloc])
fname = "docs/dogs.html"
map.save(fname)
with open(fname) as f:
    txt = f.read()
txt = txt.replace('<div>', '<div dir="rtl">')
with open(fname, 'w') as f:
    f.write(txt)
print('done dogs')
json = map.to_json()
fname = '/home/innereye/Documents/test.json'
with open(fname, 'w') as f:
    f.write(json)
