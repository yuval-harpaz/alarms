from __future__ import (absolute_import, division, print_function)
import pandas as pd
import os
import numpy as np
import sys
import folium
from folium import plugins


import json

from branca.element import Figure, JavascriptLink

from folium.map import Marker
from folium.utilities import validate_location

from jinja2 import Template

class SemiCircleColor(Marker):
    """
    Creates a Semicircle plugin to append into a map with
    Map.add_plugin.
    Use (direction and arc) or (startAngle and stopAngle)
    Parameters
    ----------
    location: tuple of length 2, default None
        The latitude and longitude of the marker.
        If None, then the middle of the map is used.
    radius: int, default 0
        Radius of semicircle
    direction: int, default 0
        Heading of direction angle value between 0 and 360 degrees
    arc: int, default 0
        Heading of arc angle value between 0 and 360 degrees.
    startAngle: int, default 0
        Heading of the start angle value between 0 and 360 degrees
    stopAngle: int, default 0
        Heading of the stop angle value between 0 and 360 degrees.
    """
    _template = Template(u"""
            {% macro script(this, kwargs) %}
                if ({{this.direction}} || {{this.arc}}) {
                    var {{this.get_name()}} = L.semiCircle(
                        [{{this.location[0]}},{{this.location[1]}}],
                        {radius:{{this.radius}},
                        fill: {{this.fill}},
                        fillColor:'{{this.fill_color}}',
                        fillOpacity: {{this.fill_opacity}},
                        color: '{{this.color}}',
                        opacity: {{this.opacity}}
                        }).setDirection({{this.direction}},{{this.arc}})
                        .addTo({{this._parent.get_name()}});
                } else if ({{this.startAngle}} || {{this.stopAngle}}) {
                    var {{this.get_name()}} = L.semiCircle(
                        [{{this.location[0]}},{{this.location[1]}}],
                        {radius:{{this.radius}},
                        fill: {{this.fill}},
                        fillColor:'{{this.fill_color}}',
                        fillOpacity: {{this.fill_opacity}},
                        color: '{{this.color}}',
                        opacity: {{this.opacity}},
                        startAngle:{{this.startAngle}}, 
                        stopAngle:{{this.stopAngle}}
                        })
                        .addTo({{this._parent.get_name()}});
                }
            {% endmacro %}
            """)

    def __init__(self,
                location,
                radius=0,
                fill = True,
                fill_color='#3388ff',
                fill_opacity = 0.5,
                color = '#3388ff',
                opacity = 1,
                direction=0,
                arc=0,
                startAngle=0,
                stopAngle=0, **kwargs):

        super(SemiCircleColor, self).__init__( validate_location(location), **kwargs)
        self._name = 'SemiCircle'
        self.radius = radius
        if fill == True:
            self.fill = 'true'
        else: self.fill = 'false'
        self.fill_color = fill_color
        self.fill_opacity = fill_opacity
        self.color = color
        self.opacity = opacity
        self.direction = direction
        self.arc = arc
        self.startAngle = startAngle
        self.stopAngle = stopAngle
        self.fill_color = fill_color
        self.kwargs = json.dumps(kwargs)

    def render(self, **kwargs):
        super(SemiCircleColor, self).render(**kwargs)

        figure = self.get_root()
        assert isinstance(figure, Figure), ('You cannot render this Element '
                                            'if it is not in a Figure.')

        figure.header.add_child(
            JavascriptLink('https://jieter.github.io/Leaflet-semicircle/Semicircle.js'),
name='semicirclejs')



local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True
    sys.path.append(local + 'code')

coo = pd.read_excel('data/deaths_by_loc.xlsx', 'coo')
names = pd.read_excel('data/deaths_by_loc.xlsx', 'names_by_id')
names['location'] = names['location'].str.replace('?', 'בבירור')
# coo = pd.read_csv('data/deaths_by_loc.csv')
center = [coo['lat'].mean(), coo['long'].mean()]
##
table = 'https://docs.google.com/spreadsheets/d/1bImioxD69gmyYhOsggcgCj1EK8Dxp8n25jwGS80GWSY/edit?usp=sharing'
map = folium.Map(location=center, zoom_start=11)
folium.TileLayer('cartodbpositron').add_to(map)
now = np.datetime64('now', 'ns')
nowisr = pd.to_datetime(now, utc=True, unit='s').astimezone(tz='Israel')
nowstr = str(nowisr)[:16].replace('T', ' ')
title_html = f'''
             <h3 dir="rtl" align="center" style="font-size:16px"><b>נרצחים ונופלים במתקפת חמאס על ישראל בין 7-9.10.2023.</b></h3>
             <h4 dir="rtl" align="center" style="font-size:12px">
             נערך על ידי שגיא אור ו<a href="https://twitter.com/yuvharpaz" target="_blank">יובל הרפז</a> (אנא שלחו תיקונית והערות). 
             <a href={table} target="_blank"> הנתונים </a> מ 
             <a href="https://oct7names.co.il/" target="_blank">ואלה שמות</a>
              ומקורות נוספים.  עדכון אחרון: {nowstr}</h4>             
             '''

# title_html = f'''
#              <h3 align="center" style="font-size:16px"><b>Deaths between 7-Oct-23 and 9-Oct-23. data from <a href="https://oct7names.co.il/" target="_blank">ואלה שמות</a> and other sources
#              . last update: {nowstr}</b></h3>
#              '''
map.get_root().html.add_child(folium.Element(title_html))
issoldier = names['citizenGroup'].str.contains('צה"ל')
rescue = ['כבאות והצלה', 'מגן דוד אדום', "משטרה (מיל')", 'שב"כ']
ispolice = names['citizenGroup'] == 'משטרה'
for r in rescue:
    ispolice = ispolice | (names['citizenGroup'] == r)
iscivil = ~(ispolice | issoldier)
isrockets = names['servicePosition'] == "ירי רקטי"

opacity = 0.55
cat = [iscivil, issoldier, ispolice, isrockets]
for icat in range(3):
    cat[icat][isrockets] = False
row_len = 7
font_size = 2
colors = ["#ff0000", "#808000", '#2255ff', '#FFA500']
for iloc in range(len(coo)):
    lat = float(coo['lat'][iloc])
    long = float(coo['long'][iloc])
    loc = coo["name"][iloc]
    # n = coo["deaths"][iloc]
    nall = np.sum(names['location'] == loc)
    # if nall != n:
    #     raise Exception('wrong N for ' + loc)
    isloc = names['location'] == loc
    s = np.sum(isloc & issoldier)
    p = np.sum(isloc & ispolice)
    r = np.sum(isloc & isrockets)
    c = nall - s - p - r
    ns = [c, s, p, r]
    radius = (nall / np.pi) ** 0.5
    start = [0, int(np.round(360*c/nall)), int(np.round(360*(c+s)/nall)), int(np.round(360*(c+s+p)/nall))]
    end = [start[1], start[2], start[3], 360]
    if np.sum(np.array(ns) > 0) == 1:
        onlyone = True
    else:
        onlyone = False
    for icat in range(4):
        color = colors[icat]
        iscat = cat[icat]
        if ns[icat] > 0:
            nm = names['fullName'][isloc & iscat].values
            rk = names['rank'][isloc & iscat].values
            order = np.argsort(nm)
            name_list = nm[order]
            rank = rk[order]
            for irank in range(len(rank)):
                if type(rank[irank]) == str:
                    rank[irank] = rank[irank].strip()
                    if len(rank[irank]) > 2:
                        name_list[irank] = rank[irank] + ' ' + name_list[irank]
                else:
                    rank[irank] = ''

            name_string = ''
            count = 0
            for ii in range(len(name_list)):
                count += 1
                name_string = name_string + name_list[ii] + ', '
                if count == row_len:
                    count = 0
                    name_string = name_string[:-2]+'<br>'
            name_string = name_string.strip()
            if name_string[-1] == ',':
                name_string = name_string[:-1]
            # name_string = '; '.join(names['fullName'][isloc & iscat])
            if ns[icat] > 300:
                fs = 1
            else:
                fs = font_size
            tip = f'<font size="{fs}">{loc}:  {ns[icat]} {["אזרחים","חיילים","שוטרים וכוחות הצלה","ירי רקטי"][icat]}<br>{name_string}'
            if onlyone:
                folium.Circle(location=[lat, long],
                                    tooltip=tip,
                                    radius=float(np.max([radius*300, 1])),
                                    fill=True,
                                    fill_color=color,
                                    color=color,
                                    opacity=0,
                                    fill_opacity=opacity
                                    ).add_to(map)
            else:
                SemiCircleColor(
                    location=[lat, long],
                    tooltip=tip,
                    radius=float(np.max([radius * 300, 1])),
                    fill_color=color,
                    opacity=0,
                    fill_opacity=opacity,
                    startAngle=start[icat],  # Start angle (0 to 360 degrees)
                    stopAngle=end[icat]  # Stop angle (0 to 360 degrees)
                ).add_to(map)
fname = 'docs/oct_7_9.html'
map.save(fname)

with open(fname) as f:
    txt = f.read()

txt = txt.replace('<div>', '<div dir="rtl">')
# txt = txt.replace('http://jieter.github.io', 'https://jieter.github.io')
txt = txt.replace('בבירור', 'לא פורסם מיקום')
txt = txt.replace('אזרחים', 'אזרחים וכיתות כוננות')
with open(fname, 'w') as f:
    f.write(txt)
