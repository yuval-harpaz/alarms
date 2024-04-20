# from matplotlib import colors
import folium
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from glob import glob
##


start_time = datetime.strptime('2024-04-14 01:42:20', '%Y-%m-%d %H:%M:%S')
end_time = datetime.strptime('2024-04-14 01:57:07', '%Y-%m-%d %H:%M:%S')

current_time = start_time
times = [current_time.strftime('%Y-%m-%d %H:%M:%S')]
while current_time < end_time:
    current_time += timedelta(seconds=1)
    times.append(current_time.strftime('%Y-%m-%d %H:%M:%S'))

##
local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True
#
df = pd.read_csv('data/alarms.csv')
df = df[df['time'] >= '2024-04-14 01:42:20']
df = df[df['time'] <= '2024-04-14 01:57:07']

coo = pd.read_csv('data/coord.csv')
center = [coo['lat'].mean(), coo['long'].mean()]
##

timeu = np.unique(df['time'].values)
for itime in range(len(timeu)):
    map = folium.Map(location=center, zoom_start=8)
    folium.TileLayer('cartodbpositron').add_to(map)
    dft = df[df['time'] <= timeu[itime]]
    current_loc = dft['cities'][dft['time'] == timeu[itime]]
    current_loc = current_loc.values
    locu = np.unique(dft['cities'])
    # map.get_root().html.add_child(folium.Element(title_html))
    for ii in range(len(locu)):
        # sz = df['Md'][ii]
        loc = locu[ii]
        lat = float(coo['lat'][coo['loc'] == loc].values)
        lon = float(coo['long'][coo['loc'] == loc].values)
        rad = np.nansum(dft['cities'] == loc)
        tip = loc + ': ' + str(int(rad))
        if loc in current_loc:
            color = '#ff0000'
        else:
            color = '#000000'
        folium.Circle(location=[lat, lon],
                      tooltip=tip,
                      radius=float(np.max([(rad / np.pi) ** 0.5 * 300 * 4, 1])),
                      fill=True,
                      fill_color=color,
                      color=color,
                      opacity=0.5,
                      fill_opacity=0.5
                      ).add_to(map)
    map.save(f"/home/innereye/Documents/iran/map_{timeu[itime]}.html")

##
import cv2

font                   = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (10, 50)
fontScale              = 0.5
fontColor              = (0, 0, 0)
thickness              = 2
lineType               = 2


os.chdir('/home/innereye/Documents/iran/')
maps = sorted(glob('Scree*'))
hmaps = sorted(glob('map_*html'))
ihtml = -1
for iframe in range(len(times)):
    op = f'frame{str(iframe).zfill(3)}.png'
    newl = [x for x in hmaps if times[iframe] in x]
    if len(newl) == 0:
        new = False
    elif len(newl) == 1:
        new = True
        timelast = newl[0][15:23]
    else:
        raise Exception(str(newl))
    if new:
        ihtml += 1
        shot = maps[ihtml]
        img = cv2.imread(shot)
        cv2.putText(img, timelast,
                    bottomLeftCornerOfText,
                    font,
                    fontScale,
                    fontColor,
                    thickness,
                    lineType)
        cv2.imwrite('T'+shot, img)



ihtml = -1
for iframe in range(len(times)):
    op = f'frame{str(iframe).zfill(3)}.png'
    newl = [x for x in hmaps if times[iframe] in x]
    if len(newl) == 0:
        new = False
    elif len(newl) == 1:
        new = True
    else:
        raise Exception(str(newl))
    if new:
        ihtml += 1
    shot = 'T'+maps[ihtml]
    err = os.system(f'ln -s "{shot}" "{op}"')

ff = 'ffmpeg -framerate 10 -pattern_type glob -i "frame*.png" -vcodec libx264 -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" iran10T.mp4'
os.system(ff)