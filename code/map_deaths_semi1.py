from __future__ import (absolute_import, division, print_function)
import pandas as pd
import os
import numpy as np
import sys
import folium
# from folium import plugins
import json
from branca.element import Figure, JavascriptLink
from folium.map import Marker
from folium.utilities import validate_location
from jinja2 import Template
sys.path.append('code')
from map_deaths_name_search import name_search_addon
from folium.features import DivIcon

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

coo = pd.read_csv('data/deaths_by_loc.csv')
# names = pd.read_excel('data/deaths_by_loc.xlsx', 'names_by_id')
names = pd.read_csv('data/oct_7_9.csv')
# pairs of search phrase+replacement. When one is given, search for contains(phrase) and replace with phrase
replace = [['בכניסה לעלומים'], ['ביה"ח שיפא'], ['סמוך לצומת גמה', 'צומת גמה'], ['מיגונית בצומת גמה', 'צומת גמה'],
           ['צומת בארי'], ['מיגוניות בצומת רעים', 'צומת רעים'], ['חאן יונס'],['מיגונית חניון רעים', 'פסטיבל נובה'],
           ['רצועת עזה', 'רצועת עזה, לא פורסם מיקום מדוייק'], ['דיר אל בלח']]  #
for uu in replace:
    names.loc[names['location'].str.contains(uu[0]), 'location'] = uu[-1]  # -1 allows for pairs, search term + what to change into
center = [coo['lat'].mean(), coo['long'].mean()]
##
table = 'https://docs.google.com/spreadsheets/d/1bImioxD69gmyYhOsggcgCj1EK8Dxp8n25jwGS80GWSY/edit?usp=sharing'
# Look for missing coordinates
locu = np.unique(names['location'])
missing = []
dupcoo = []
for lc in locu:
    if lc not in coo['name'].values:
        missing.append(lc)
    if np.sum(coo['name'] == lc) > 1 and lc not in dupcoo:
        dupcoo.append(lc)
if len(missing) > 0:
    raise Exception('missing coordinates for :'+str(missing))
if len(dupcoo) > 0:
    raise Exception('duplicate coordinates for :'+str(dupcoo))
# Look for identical names

nameu = np.unique(names['fullName'])
allowed = ['מזרחי אור']
dup_name = []
for nm in nameu:
    if np.sum(names['fullName'] == nm) > 1 and nm not in allowed:
        dup_name.append(nm)
if len(dup_name) > 0:
    raise Exception('duplicate names: '+str(dup_name))
catname = ["אזרחים וכיתות כוננות","חיילים","שוטרים וכוחות הצלה","ירי רקטי"]

cat = []
for icat in range(4):
    cat.append(names['category'].values == catname[icat])


# add text for sig places
idx = list(range(20))

idx = idx + [np.where(coo['name'] == 'בבירור')[0][0]]
opacity = 0.55
row_len = 7
font_size = 2
colors = ["#ff0000", "#808000", '#2255ff', '#FFA500']
isparty = names['comment'] == 'פסטיבל נובה'
isduck = names['comment'] == 'מסיבת פסיידאק'

for lang in ['heb', 'eng']:
    if lang == 'heb':
        cat_lang = ["אזרחים וכיתות כוננות", "חיילים", "שוטרים וכוחות הצלה", "ירי רקטי"]
    else:
        cat_lang = ['Civilians and emergency teams', 'Soldiers', 'Police and rescue teams', 'Rockets']
    for imap in [0, 1]:
        n_loc = []
        # legend
        ydif = 0.018
        xdif = 0.018
        lltext = [31.576, 34.197]
        llcirc = lltext.copy()
        llcirc[1] = lltext[1] - xdif
        llcirc[0] = lltext[0] - 0.007
        map = folium.Map(location=center, zoom_start=11)
        folium.TileLayer('cartodbpositron').add_to(map)
        now = np.datetime64('now', 'ns')
        nowisr = pd.to_datetime(now, utc=True, unit='s').astimezone(tz='Israel')
        nowstr = str(nowisr)[:16].replace('T', ' ')
        if lang == 'heb':
            if imap == 1:
                other = '    <a href="https://yuval-harpaz.github.io/alarms/oct_7_9.html" target="_blank">חזרה</a>'
                change_lang = ''
            else:
                other = '    <a href="https://yuval-harpaz.github.io/alarms/oct_7_9_search.html" target="_blank"> חיפוש שם</a>'
                change_lang = '    <a href="https://yuval-harpaz.github.io/alarms/oct_7_9_eng.html"> Eng</a>'
            title_html = f'''
                         <h3 dir="rtl" align="center" style="font-size:16px"><b>מקום מותם של {len(cat[0])} הנרצחים והנופלים במתקפת חמאס על ישראל בין 7-9.10.2023.</b>{other},{change_lang}</h3>
                         <h4 dir="rtl" align="center" style="font-size:12px">
                         נערך על ידי שגיא אור ו<a href="https://twitter.com/yuvharpaz" target="_blank">יובל הרפז</a> (אנא שלחו תיקונים והערות). 
                         קישור <a href={table} target="_blank"> לנתונים </a> במסמך גוגל 
                          . כללנו אנשים שנפצעו או נחטפו במתקפה, ומתו או נרצחו מאז.  עדכון אחרון: {nowstr}</h4>             
                         '''
        else:
            if imap == 1:
                other = '    <a href="https://yuval-harpaz.github.io/alarms/oct_7_9_eng.html" target="_blank"> back</a>'
                change_lang = ''
            else:
                other = '    <a href="https://yuval-harpaz.github.io/alarms/oct_7_9_eng_search.html" target="_blank"> search name</a>'
                change_lang = '    <a href="https://yuval-harpaz.github.io/alarms/oct_7_9.html"> עברית</a>'
            title_html = f'''
                         <h3 dir="rtl" align="center" style="font-size:16px"><b>Death locations of {len(cat[0])} murdered and fallen during the Hamas attack on Israel between 7-9.10.2023.</b>{other},{change_lang}</h3>
                         <h4 dir="rtl" align="center" style="font-size:12px">
                         Edited by Sagi Or and <a href="https://twitter.com/yuvharpaz" target="_blank">Yuval Harpaz</a>. 
                         <a href={table} target="_blank"> The data </a> in a google sheet 
                         . We included people who were kidnapped or injured in the attack, and died or were murdered later.  Last update: {nowstr}</h4>             
                         '''
        map.get_root().html.add_child(folium.Element(title_html))
        if imap == 1:
            if lang == 'heb':
                name_col = 'fullName'
            else:
                name_col = 'eng'
            map.get_root().html.add_child(folium.Element(name_search_addon(names, coo, map.get_name(), name_col=name_col)))
            fname = f'docs/oct_7_9_{lang}_search.html'
        else:
            fname = f'docs/oct_7_9_{lang}.html'
        fname = fname.replace('_heb', '')
        # parties first
        party_lat = [31.4014870534664, 31.3417157186523]
        party_long = [34.4724927048611, 34.4161349190368]
        party_rad = [np.sum(names['comment'] == 'פסטיבל נובה'), np.sum(names['comment'] == 'מסיבת פסיידאק')]
        # party_rad = (np.array(party_rad) / np.pi) ** 0.5
        if lang == 'heb':
            party_tip = ['נובה ('+str(party_rad[0])+'), כולל נמלטים שנרצחו', 'פסיידאק ('+str(party_rad[1])+'), לא נרצחו באתר המסיבה']
        else:
            party_tip = ['Nova ('+str(party_rad[0])+'), including murdered escapees', 'Psyduck ('+str(party_rad[1])+'), including murdered escapees']
        for iparty in [1]:
            folium.Circle(location=[party_lat[iparty], party_long[iparty]],
                          tooltip=f'<font size="{font_size}">'+party_tip[iparty],
                          radius=float(np.max([(party_rad[iparty] / np.pi) ** 0.5 * 300, 1])),
                          fill=True,
                          fill_color='#AAAAAA',
                          color='#AAAAAA',
                          opacity=0,
                          fill_opacity=opacity
                          ).add_to(map)
        for iloc in range(len(coo)):
            lat = float(coo['lat'][iloc])
            long = float(coo['long'][iloc])
            loc = coo["name"][iloc]
            if lang == 'heb':
                loc_lang = loc
            else:
                loc_lang = coo['eng'][np.where(coo['name'] == loc)[0][0]]
            nall = np.sum(names['location'] == loc)
            n_loc.append(nall)
            if nall == 0:
                if loc != 'מסיבת פסיידאק':
                    raise Exception('no people in '+loc)
            else:
                isloc = names['location'] == loc
                s = np.sum(isloc & cat[1])
                p = np.sum(isloc & cat[2])
                r = np.sum(isloc & cat[3])
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
                        fest = np.sum(iscat & isparty & isloc)
                        pfest = np.sum(iscat & isduck & isloc)
                        if lang == 'heb':
                            nm = names['fullName'][isloc & iscat].values
                            rk = names['rank'][isloc & iscat].values
                        else:
                            nm = names['eng'][isloc & iscat].values
                            rk = np.array(['']*len(nm))
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
                        if ns[icat] > 300:
                            fs = 1
                        else:
                            fs = font_size
                        tip = f'<font size="{fs}">{loc_lang}:  {ns[icat]} {cat_lang[icat]}'
                        if fest > 0 and (loc != 'פסטיבל נובה') and (loc != 'מיגוניות בכניסה לרעים'):
                            if lang == 'heb':
                                tip = tip + f' (כולל {fest} מפסטיבל נובה)'
                            else:
                                tip = tip + f' (including {fest} from Nova festival)'
                        if pfest > 0:
                            if fest and pfest:
                                if lang == 'heb':
                                    tip = tip[:-1] + f' ו- {pfest} ממסיבת פסיידאק)'
                                else:
                                    tip = tip[:-1] + f' and {pfest} from Psyduck party)'
                            else:
                                if lang == 'heb':
                                    tip = tip + f' (כולל {pfest} ממסיבת פסיידאק)'
                                else:
                                    tip = tip + f' (including {pfest} from Psyduck Party)'
                        tip = tip + '<br>' + name_string
                        if loc == 'עמיעוז':
                            tip = tip.replace('<br>', '<br>נחבלה בדרך לממ\"ד - ')
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

        for iloc in idx:
            loc = coo["name"][iloc]
            if lang == 'heb':
                loc_lang = loc
            else:
                loc_lang = coo['eng'][np.where(coo['name'] == loc)[0][0]]
            # if 'מוצב' not in loc:
            tot = np.sum(names['location'] == loc)
            radius = (tot / np.pi) ** 0.5
            latlong = [coo['lat'][iloc] + 0.006, coo['long'][iloc] + radius * 0.0035]

            if loc in ['נחל עוז', 'מוצב נחל עוז' ,'רעים', 'סמוך למפלסים']:
                latlong[0] = latlong[0] - 0.003
                latlong[1] = latlong[1] - 0.003
            elif loc == 'מוצב כיסופים':
                latlong[0] = latlong[0] - 0.006
                latlong[1] = latlong[1] - 0.003
            if loc in ['בארי', 'נחל עוז','כיסופים', 'רעים']:
                if lang == 'heb':
                    loc_lang = 'קיבוץ ' + loc_lang
                if loc == 'כיסופים':
                    latlong[1] = latlong[1] - 0.014
                # else:
                #     loc_lang = 'Kibbutz ' + loc_lang
            elif loc == 'מיגוניות בצומת רעים':
                latlong[0] = latlong[0] + 0.003
                latlong[1] = latlong[1] - 0.006
                if lang == 'heb':
                    loc_lang = 'מיגוניות'
                else:
                    loc_lang = 'Shelters'
            elif loc == 'בבירור':
                if lang == 'heb':
                    loc_lang = 'לא פורסם'
                else:
                    loc_lang = 'Not published'
            elif loc == 'צומת גמה':
                latlong[0] = latlong[0] - 0.006
                # latlong[1] = latlong[1] + 0.006
            html_txt1 = f'<div style="font-size: 10pt; color:gray">{loc_lang} ({tot})</div>'
            if loc == 'פסטיבל נובה':
                if lang == 'heb':
                    html_txt1 += f'<div style="font-size:7pt; color:gray">כולל הנמלטים למיגוניות ולקיבוצים: {np.sum(isparty)}</div>'
                else:
                    html_txt1 += f'<div style="font-size:7pt; color:gray">including escapees to shelters and kibbutzim: {np.sum(isparty)}</div>'
            folium.map.Marker(
                latlong,
                icon=DivIcon(
                    icon_size=(250, 36),
                    icon_anchor=(0, 0),
                    html=html_txt1,
                )
            ).add_to(map)
        # make legend
        for icat in range(4):
            color = colors[icat]
            html_txt = f'<div style="font-size: 10pt">{cat_lang[icat]} ({sum(cat[icat])})</div>'
            folium.map.Marker(
                lltext,
                icon=DivIcon(
                    icon_size=(250, 36),
                    icon_anchor=(0, 0),
                    html=html_txt,
                )
            ).add_to(map)
            folium.Circle(location=llcirc,
                          radius=500.0,
                          fill=True,
                          fill_color=color,
                          color=color,
                          opacity=0,
                          fill_opacity=opacity
                          ).add_to(map)
            lltext[0] = lltext[0] - ydif
            llcirc[0] = llcirc[0] - ydif
        # some fixes
        map.save(fname)
        with open(fname) as f:
            txt = f.read()
        if lang == 'heb':
            txt = txt.replace('<div>', '<div dir="rtl">')
        # txt = txt.replace('http://jieter.github.io', 'https://jieter.github.io')
        txt = txt.replace('בבירור', 'לא פורסם מיקום')
        # txt = txt.replace('אזרחים', 'אזרחים וכיתות כוננות')
        meta = '<head>\n' \
               '    <meta  name="author" content="Yuval Harpaz, Sagi Or">\n' \
               '    <meta  name="Description" content="A map showing where Israeli civillians and soldiers were murdered and fell in battle during the attack by Hamas, from Oct-7 to Oct-9 2023. ">\n' \
               '    <meta  name="keywords" content="map, massacre, Oct-7, 7.10, 7-10, Gaza, Nova Festival, party, Beeri, Oz' \
               'מפה, מפת הטבח, רצח, הרצח, נובה, רעים, עזה, עוטף עזה, כפר עזה, נחל עוז, בארי, שער הנגב, חיילים, אזרחים, כיתות כוננות,יובל הרפז, חמאס">'

        txt = txt.replace('<head>\n    ', meta)
        with open(fname, 'w') as f:
            f.write(txt)
        del map
coo['total'] = n_loc
coo.sort_values('total', inplace=True, ascending=False)
coo.to_csv('data/deaths_by_loc.csv', index=False)
print('done map semi1')