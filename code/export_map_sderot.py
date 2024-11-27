"""Plot alarms from Lebanon according to latitude."""
import pandas as pd
import numpy as np
import simplekml
import geojson



# import kml2geojson
df = pd.read_csv('/home/innereye/Documents/sderot.csv')
df['latitude'] = [x.split(',')[0].strip() for x in df['event_coordinates']]

nums = df['latitude'].values
for inum in range(len(nums)):
    num = nums[inum]
    if len(num) < 9:
        num = '{:.6f}'.format(float(num))
    else:
        num = num[:9]
    nums[inum] = num
df['latitude'] = nums
df['longitude'] = [x.split(',')[1].strip() for x in df['event_coordinates']]
nums = df['longitude'].values
for inum in range(len(nums)):
    num = nums[inum]
    if len(num) < 9:
        num = '{:.6f}'.format(float(num))
    else:
        num = num[:9]
    nums[inum] = num
df['longitude'] = nums
df.to_csv('/home/innereye/Documents/sderot.csv', index=False)

not_empty = np.array(~df['event_coordinates'].isnull())

killed = np.array([x[:6] == 'killed' for x in df['Status']])
kml = simplekml.Kml()
for iskilled in [1, 0]:
    if iskilled:
        iscat = not_empty & killed
    else:
        iscat = not_empty & ~killed
    coou = np.unique(df['event_coordinates'][iscat])
    # type_colors = {0: "ff0000ff", 1: "ff00ff00"}

    for ii in range(len(coou)):
        coo_str = coou[ii]
        rows = np.where((df['event_coordinates'] == coo_str) & iscat)[0]
        coords = np.asarray([x.strip() for x in coo_str.split(',')]).astype(float)
        # desc = ''
        # for row in rows:
        #     desc = desc + df["שם פרטי"][row] + ' ' + df["שם משפחה"][row] + '\n'
        # desc = desc[:-1]
        # if len(rows) == 1:
        #     name = desc
        # else:
        #     name = None
        # coords = [[coords[0]], [coords[1]]]
        name = df["שם פרטי"][rows[0]] + ' ' + df["שם משפחה"][rows[0]]
        if len(rows) > 1:
            name = name + f" + {len(rows)-1}"
        pnt = kml.newpoint(name=name, coords=[coords[::-1]])
        # pnt.style.iconstyle.color = ["ffff5555", "ff0000ff"][iskilled]
        scale = len(rows)/10
        if scale < 1:
            scale = 1
        scale = scale + 0.01 * iskilled
        pnt.style.iconstyle.scale = scale  # Set size
        color = ['0000FF', 'FF0000'][iskilled]
        pnt.style.iconstyle.icon.href = f"https://caltopo.com/icon.png?cfg=c%3Aring%2C{color}%231.0"
# df.apply(lambda X: kml.newpoint(name=X["name"], coords=[( X["longitude"],X["latitude"])]) ,axis=1)
path = '/home/innereye/Documents/maps/test1.kml'
kml.save(path=path)

# json = kml2geojson.convert(path)
# st, js = kml2geojson.convert(path, style_type='leaflet')


# ## import with
# geojson_features = []

# # Iterate over the dataframe to create features
# for ii in range(len(df)):
#     coords = np.asarray(df['event_coordinates'][ii].split(', ')).astype(float)
#     # Reverse coordinates to GeoJSON format (longitude, latitude)
#     coords = list(coords)[::-1]
#     # Define the feature properties
#     name = f"{df['first name'][ii]} {df['last name'][ii]}"
#     color = "FF0000" if 'kidnapped' in df['Status'][ii].lower() else "0000FF"
#     properties = {
#         "title": name,
#         "description": df['Status'][ii],
#         "marker-symbol": "point",
#         "marker-color": color,
#         # "name": name,
#         # "color": color,
#     }
#     # Create a GeoJSON feature
#     feature = geojson.Feature(
#         geometry=geojson.Point(coords),
#         properties=properties
#     )
#     geojson_features.append(feature)

# # Create the GeoJSON FeatureCollection
# geojson_data = geojson.FeatureCollection(geojson_features)

# # Define the output path
# geojson_path = '/home/innereye/Documents/maps/test.geojson'

# # Save to a GeoJSON file
# with open(geojson_path, 'w') as f:
#     geojson.dump(geojson_data, f)

# print(f"GeoJSON file created: {geojson_path}")
