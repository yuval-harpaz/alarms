# from matplotlib import colors
import folium
import pandas as pd
import numpy as np
import os
##
local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True
#
df = pd.read_csv('data/oct_7_9.csv')
# replace = [['בכניסה לעלומים'], ['סמוך לצומת גמה', 'צומת גמה'], ['מיגונית בצומת גמה', 'צומת גמה'],
#            ['צומת בארי'], ['מיגוניות בצומת רעים', 'צומת רעים']]  #
# for uu in replace:
#     df.loc[df['location'].str.contains(uu[0]), 'location'] = uu[-1]  # -1 allows for pairs, search term + what to change into

locuu = np.unique([x for x in df['location'].values if 'ירי בשוגג' not in x])
locuu = locuu[locuu != 'עזה']
cat = ['']*len(locuu)
cat[np.where(locuu =='פרי גן')[0][0]] = 'residential'
cat[np.where(locuu =='כוחלה')[0][0]] = 'residential'
cat = np.array(cat, str)
for ii in range(len(cat)):
    if 'מוצב' in locuu[ii] or 'מחנה' in locuu[ii]:
        cat[ii] = 'army'
    elif locuu[ii] in df['residence'].values:
        cat[ii] = 'residential'
    elif locuu[ii] in ['חוף זיקים','מסיבת פסיידאק','פסטיבל נובה']:
        cat[ii] = 'camping'
    else:
        cat[ii] = 'road'
cat[np.where(locuu =='כוחלה')[0][0]] = 'residential'
cat[np.where(locuu =='פרי גן')[0][0]] = 'residential'
cat[np.where(locuu =='סמוך למחנה רעים')[0][0]] = 'road'
cat = np.array(cat, str)
for army in ['עמדה 91', 'מעבר ארז', 'מש"א ארז', 'מו"פ דרום']:
    cat[np.where(locuu == army)[0][0]] = 'army'

dfc = pd.DataFrame(columns=['loc', 'cat'])
dfc['loc'] = locuu
dfc['cat'] = cat
dfc = dfc.sort_values(['cat', 'loc'], ignore_index=True)

##
road = dfc['loc'][dfc['cat'] == 'road'].values
include = np.empty(len(df), bool)
for ii in range(len(df)):
    jj = np.where(dfc['loc'].values == df['location'][ii])[0]
    if len(jj) == 0:
       print(df['location'][ii])
    else:
        include[ii] = dfc['cat'].values[jj[0]] == 'road'
miguniot = np.where(df['location'].str.contains('מיגוניות'))[0]
# include[miguniot] = False
df_road = df[include].copy()
df_road = df_road[df_road['date'] == '07.10.2023']
df_road.sort_values(['location', 'fullName'], inplace=True)

df_road.to_excel('../Documents/road.xlsx', index=False)
##
df = pd.read_excel('../Documents/road.xlsx')
# df = pd.read_csv('data/tmp_bar.csv')
replace = [['בכניסה לעלומים'], ['סמוך לצומת גמה', 'צומת גמה'], ['מיגונית בצומת גמה', 'צומת גמה'],
           ['צומת בארי'], ['מיגוניות בצומת רעים', 'צומת רעים']]  #

for uu in replace:
    df.loc[df['location'].str.contains(uu[0]), 'location'] = uu[-1]  # -1 allows for pairs, search term + what to change into
coo = pd.read_csv('data/deaths_by_loc.csv')
center = [coo['lat'].mean(), coo['long'].mean()]
map = folium.Map(location=center, zoom_start=7.5, tiles='openstreetmap')
tiles = ['cartodbpositron', 'stamenterrain']
for tile in tiles:
    folium.TileLayer(tile).add_to(map)
locu = np.unique(df['location'])
# map.get_root().html.add_child(folium.Element(title_html))
for ii in range(len(locu)):
    # sz = df['Md'][ii]
    loc = locu[ii]
    lat = float(coo['lat'][coo['name'] == loc])
    lon = float(coo['long'][coo['name'] == loc])
    rad = np.nansum(df['location'] == loc)
    tip = loc + ': ' + str(int(rad))
    name_list = df['fullName'][df['location'] == loc].values
    name_string = ''
    count = 0
    for ii in range(len(name_list)):
        count += 1
        name_string = name_string + name_list[ii] + ', '
        if count == 7:
            count = 0
            name_string = name_string[:-2] + '<br>'
    name_string = name_string.strip()
    if name_string[-1] == ',':
        name_string = name_string[:-1]
    # dt = df['DateTime'][ii]
    # d = np.round(df['Depth(Km)'][ii], 1)
    # if d > 0:
    #     depth = ', depth: '+str(d)+'Km'
    # tip = df['DateTime(UTC)'][ii][:-4].replace('T', ' ')
    tip = tip+'<br> '+name_string
    folium.Circle(location=[lat, lon],
                  tooltip=tip,
                  radius=float(np.max([(rad / np.pi) ** 0.5 *300, 1])),
                  fill=True,
                  fill_color='#ff0000',
                  color='#ff0000',
                  opacity=0.5,
                  fill_opacity=0.5
                  ).add_to(map)

folium.map.LayerControl('topleft', collapsed=False).add_to(map)
map.save("docs/tmp_bar1.html")
# df.to_csv('data/earthquakes.csv', index=False)
##
# prev = pd.read_csv('data/tmp_bar.csv')
# df = pd.read_excel('../Documents/road.xlsx')
