import folium
from folium.plugins import GroupedLayerControl
from folium.features import DivIcon
import pandas as pd
import numpy as np
import os


local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True
prev = pd.read_csv('data/alarms.csv')

prev = prev.reset_index(drop=True)
last_alarm = pd.to_datetime(prev['time'][len(prev)-1])
last_alarm = last_alarm.tz_localize('Israel')

date = np.array([d[:10] for d in prev['time']])
month = np.array([d[:7] for d in prev['time']])
monthu = np.unique(month)
monthu = monthu[monthu >= ['2023-10']]
now = np.datetime64('now', 'ns')
nowisr = pd.to_datetime(now, utc=True, unit='s').astimezone(tz='Israel')
nowstr = str(nowisr)[:16].replace('T', ' ')
##
# Make map
title_html = f'''
             <h3 align="center" style="font-size:16px"><b>Alarms in Israel per month, data from <a href="https://www.oref.org.il" target="_blank">THE NATIONAL EMERGENCY PORTAL</a>
             via <a href="https://www.tzevaadom.co.il/" target="_blank">צבע אדום</a>. last checked: {nowstr}</b></h3>
             '''
color = '#000000'
lgd_txt = '<span style="color: {col};">{txt}</span>'
grp = []
for ic, gn in enumerate(monthu):
    gn = '/'.join(gn.split('-')[::-1])
    show = False
    if ic == 0:
        show = True
    grp.append(folium.FeatureGroup(name=lgd_txt.format(txt=gn, col=color), show=show))

coo = pd.read_csv('data/coord.csv')
center = [coo['lat'].mean(), coo['long'].mean()]
##
map = folium.Map(location=center, zoom_start=7.5, tiles='cartodbpositron')
map.get_root().html.add_child(folium.Element(title_html))
coo = coo.sort_values('lat', ignore_index=True, ascending=False)
cities = prev['cities'].values
keep = [x in cities[date > '2023-10-07'] for x in coo['loc']]
if coo['loc'][0] == 'אל מסק':
    keep[0] = False  # where dehel is el masq?
coo = coo[keep]
coo = coo.reset_index(drop=True)
monthly = coo.copy()
for igroup in range(len(monthu)):
    dt = monthu[igroup]
    idx = month == dt
    loc = np.asarray(prev['cities'][idx])
    for iloc in range(len(monthly)):
        lc = monthly['loc'][iloc]
        sz = np.sum(loc == lc)
        monthly.at[iloc, dt] = sz
        if sz > 0:
            lat = float(monthly['lat'][iloc])
            long = float(monthly['long'][iloc])
            tip = lc+':  ' + str(sz)  # + str(mag[ii]) + depth  + '<br> '
            alpha = 0.5
            folium.CircleMarker(location=[lat, long],
                                tooltip=tip,
                                radius=float(np.max([sz**0.5*2, 1])),
                                fill=True,
                                fill_color=color,
                                color=color,
                                opacity=0,
                                fill_opacity=alpha
                                ).add_to(grp[igroup])
monthly.to_csv('data/war23_alarms_monthly.csv', index=False)

for ig in range(len(monthu)):
    grp[ig].add_to(map)
select = [['קריית שמונה'], ['נהריה'], ['קצרין'], ['חיפה - נווה שאנן ורמות כרמל', 'חיפה'], ['תל אביב - מרכז העיר', 'תל אביב'],
          ['אופקים'], ['שדרות'], ['אשקלון - צפון', 'אשקלון'], ['באר שבע - מערב', 'באר שבע']]
for cit in select:
    iloc = np.where(monthly['loc'] == cit[0])[0]
    if len(iloc) != 1:
        raise Exception('issues with '+cit[0])
    iloc = iloc[0]
    lat = float(monthly['lat'][iloc])
    long = float(monthly['long'][iloc])
    html_txt1 = f'<div dir="rtl" align="left" style="font-size: 14pt; color:gray">{cit[-1]}</div>'
    folium.map.Marker(
                    [lat, long],
                    icon=DivIcon(
                        icon_size=(250, 36),
                        icon_anchor=(0, 0),
                        html=html_txt1,
                    )
                ).add_to(map)
# folium.map.LayerControl('topright', collapsed=False, hideSingleBase=True).add_to(map)
GroupedLayerControl(
    groups={'חודש': grp},
    collapsed=False,
    position='topleft'
).add_to(map)
html_name = "docs/war_alarms_monthly.html"
map.save(html_name)
print('done monthly alarms')
