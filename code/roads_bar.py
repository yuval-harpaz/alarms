# from matplotlib import colors
import folium
import pandas as pd
import numpy as np

df = pd.read_csv('data/tmp_bar.csv')
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
# map.get_root().html.add_child(folium.Element(title_html))
for ii in range(len(df)):
    # sz = df['Md'][ii]
    loc = df['location'][ii]
    lat = float(coo['lat'][coo['name'] == loc])
    lon = float(coo['long'][coo['name'] == loc])
    rad = np.nansum(df.loc[ii].values[1:])
    tip = loc + ': ' + str(int(rad))
    # dt = df['DateTime'][ii]
    # d = np.round(df['Depth(Km)'][ii], 1)
    # if d > 0:
    #     depth = ', depth: '+str(d)+'Km'
    # tip = df['DateTime(UTC)'][ii][:-4].replace('T', ' ')
    # tip = tip+'<br> '+M[ii]+': '+str(mag[ii])+depth
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
map.save("docs/tmp_bar.html")
# df.to_csv('data/earthquakes.csv', index=False)
