import pandas as pd
import os
import numpy as np
import sys
import folium
import requests

local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True
    sys.path.append(local + 'code')
from alarms_coord import update_coord

min_deaths = {'בארי': 85, 'ניר עוז': 35, 'יכיני':4, 'נתיב העשרה': 21, 'כפר עזה': 72, 'עלומים': 20, 'כיסופים': 16,
              'רעים': 5, 'נירים': 5, 'אופקים':30, 'נחל עוז': 35, 'חולית': 13, 'ניר יצחק': 3, 'עין השלושה': 3,
              'מגן': 1, 'סופה': 3, 'כרם שלום': 2, 'שלומית': 2}  # from: https://www.ynet.co.il/news/article/yokra13627562


def map_deaths():
    df = pd.read_csv('data/deaths.csv')
    # coo = pd.read_csv('data/coord.csv')
    locs = [x.replace('קיבוץ ','').replace('מושב ','').replace('קריית','קרית') for x in df['from'] if type(x) == str]
    # locs = [x for x in df['from'].replace('קיבוץ', '').replace('מושב', '').strip() if type(x) == str]
    locu = np.unique(locs)
    for md in list(min_deaths.keys()):
        if md not in locu:
            locu = np.array(list(locu)+[md])
    update_coord(latest=locu, coord_file='data/coord_deaths.csv')
    coo = pd.read_csv('data/coord_deaths.csv')
    center = [coo['lat'].mean(), coo['long'].mean()]
    ##
    map = folium.Map(location=center, zoom_start=7.5)#, tiles='openstreetmap')
    # folium.TileLayer('https://tile.openstreetmap.de/{z}/{x}/{y}.png',
    #                  attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors').add_to(map)
    # folium.TileLayer('openstreetmap').add_to(map)
    folium.TileLayer('cartodbpositron').add_to(map)
    now = np.datetime64('now', 'ns')
    nowisr = pd.to_datetime(now, utc=True, unit='s').astimezone(tz='Israel')
    nowstr = str(nowisr)[:16].replace('T', ' ')
    title_html = f'''
                 <h3 align="center" style="font-size:16px"><b>War deaths in Israel since 7-Oct-23, by residence. data from <a href="https://ynet-projects.webflow.io/news/attackingaza" target="_blank">ynet</a>
                 . last checked: {nowstr}</b></h3>
                 '''
    map.get_root().html.add_child(folium.Element(title_html))
    locs = np.array(locs)
    size = np.zeros(len(locu), int)
    folium.Circle(location=[31.4025912, 34.4724382],
                  tooltip='המסיבה ברעים, 357',
                  radius=float((260 / np.pi) ** 0.5 * 750),
                  fill=True,
                  fill_color='#555555',
                  color='#555555',
                  opacity=0,
                  fill_opacity=0.5
                  ).add_to(map)
    for iloc in range(len(locu)):
        row_coo = coo['loc'] == locu[iloc]
        if np.sum(row_coo) == 1:
            size[iloc] = np.sum(locs == locu[iloc])
            if locu[iloc] in min_deaths.keys():
                size[iloc] = np.max([min_deaths[locu[iloc]], size[iloc]])
            lat = float(coo['lat'][row_coo])
            long = float(coo['long'][coo['loc'] == locu[iloc]])
            tip = f'{locu[iloc]}  {size[iloc]}'
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
            # folium.CircleMarker(location=[lat, long],
            #                     tooltip=tip,
            #                     radius=float(np.max([radius, 1])),
            #                     fill=True,
            #                     fill_color='#ff0000',
            #                     color='#ff0000',
            #                     opacity=0,
            #                     fill_opacity=0.5
            #                     ).add_to(map)
        else:
            print('cannot find coord for '+locu[iloc])
    map.save("docs/war_deaths23.html")
    print('done, one more thing')
    # רםצ https://www.mako.co.il/news-israel/2023_q2/Article-3abcb0281ca0b81026.htm
    n12 = requests.get('https://makoironcdn.cdn-il.com/website%2Fdata.json')
    n12 = n12.json
    n12 = requests.get('https://makoironcdn.cdn-il.com/website%2Fdata.json')
    n12 = n12.json()
    dfn12 = pd.DataFrame(n12['rows'])
    dfn12.to_excel('data/mako.xlsx')
    # ##  complete ynet with mako
    # # df.reset_index(drop=True, inplace=True)
    # already = np.zeros(len(dfn12))
    # for rown12 in range(len(dfn12)):
    #     match = []
    #     for rowynet in range(len(df)):
    #         if (dfn12['b'][rown12] in df['name'][rowynet]) and (dfn12['c'][rown12] in df['name'][rowynet]):
    #             match.append(rowynet)
    #     if len(match) > 1:
    #         pass
    #         # print(dfn12['b']+' '+dfn12['c']+' has more than one match '+str(match))
    #     elif len(match) == 0:
    #         pass
    #         # print(dfn12['b']+' '+dfn12['c']+' has no match')
    #     else:
    #         match = match[0]
    #         if already[rown12]:
    #             print(f'ynet {match} conflicts with ynet {already[rown12]}')
    #         else:
    #             already[rown12] = match
    #             if pd.isnull(df['first'][match]):
    #                 df.at[match, 'first'] = dfn12['b'][rown12]
    #                 midlast = dfn12['c'][rown12].split(' ')
    #                 df.at[match, 'last'] = midlast[-1]
    #                 if len(midlast) == 2:
    #                     df.at[match, 'middle'] = midlast[0]
    #                 elif len(midlast) > 2:
    #                     df.at[match, 'middle'] = ' '.join(midlast[:-1])
    #                 df.at[match, 'mako_story'] = dfn12['l'][rown12]
    #                 df.at[match, 'status'] = dfn12['g'][rown12]
    #                 df.at[match, 'rank'] = dfn12['a'][rown12]
    #                 if pd.isnull(df['gender'][match]):
    #                     df.at[match, 'gender'] = dfn12['e'][rown12].replace('גבר', 'M').replace('אישה', 'F')
    #                 if df['age'][match] == 0 and len(dfn12['d'][rown12]) > 0:
    #                     df.at[match, 'age'] = int(dfn12['d'][rown12])
    # df.to_csv('data/deaths.csv', index=False)
    # df.to_excel('data/deaths.xlsx', index=False)

# https://ynet-pic1.yit.co.il/picserver5/wcm_upload_files/2023/11/12/S1sFis07p/ynetlist1211.xlsx
# https://www.kavlaoved.org.il/%D7%A9%D7%9E%D7%95%D7%AA%D7%99%D7%94%D7%9D-%D7%A9%D7%9C-%D7%9E%D7%94%D7%92%D7%A8%D7%99-%D7%94%D7%A2%D7%91%D7%95%D7%93%D7%94-%D7%A9%D7%A0%D7%94%D7%A8%D7%92%D7%95-%D7%91%D7%9E%D7%9C%D7%97%D7%9E%D7%AA/













if __name__ == '__main__':
    map_deaths()

