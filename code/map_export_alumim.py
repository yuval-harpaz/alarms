"""Export data to html map."""
import pandas as pd
import numpy as np
import geojson

mapname = 'Alumim'
dba = pd.read_excel(f'/home/innereye/Documents/Map/{mapname}.xlsx')
events = np.array([x.split(';')[0] for x in dba['Status'].values])
geojson_features = []
coos = []
for event in ['killed', 'kidnapped']:
    df = dba[events == event]
    df = df.reset_index(drop=True)
    # Iterate over the dataframe to create features
    coo_string = df['event_coordinates'].values
    coo = np.array([x.split(', ')[::-1] for x in coo_string]).astype(float)
    coou_string = np.unique(coo_string)
    coou = np.array([x.split(', ')[::-1] for x in coou_string]).astype(float)
    coos.extend(coou)
    for ii in range(len(coou)):
        # coords = np.asarray(df['event_coordinates'][ii].split(', ')).astype(float)
        # Reverse coordinates to GeoJSON format (longitude, latitude)
        # coords = list(coords)[::-1]
        # Define the feature properties
        rows = np.where(coo_string == coou_string[ii])[0]
        name = ''
        for row in rows:
            name = name + f"{df['שם פרטי'][row]} {df['שם משפחה'][row]}" + "<br>"
        name = name[:-4]
        # color = "FF0000" if 'kidnapped' in df['Status'][ii].lower() else "0000FF"
        properties = {
            "name": name,
            "event": event,
        }
        # Create a GeoJSON feature
        feature = geojson.Feature(
            properties=properties,
            geometry=geojson.Point(list(coou[ii]))
        )
        geojson_features.append(feature)
center = np.mean(coos, 0)
# Create the GeoJSON FeatureCollection
geojson_data = geojson.FeatureCollection(geojson_features)

# Define the output path
geojson_path = f'/home/innereye/Documents/Map/{mapname}.geojson'

# Save to a GeoJSON file
with open(geojson_path, 'w') as f:
    geojson.dump(geojson_data, f)
print(f"GeoJSON file created: {geojson_path}")

with open(geojson_path, 'r') as f:
    data = f.read()

with open('/home/innereye/Documents/Map/tmp2.html', 'r') as f:
    html = f.read()
before = html[:html.index("var geojsonData = {")]
after = html[html.index("var Killed = L.layerGroup()"):]
optxt = before + "var geojsonData = " + data + "\n" + after
optxt = optxt.replace("center: [31.425145, 34.48899],", f"center: [{center[1]}, {center[0]}],")
optxt = optxt.replace("Foreign", mapname)
mapfile = f'/home/innereye/Documents/Map/{mapname}.html'
with open(mapfile, 'w') as f:
    f.write(optxt)

print(f"map created: {mapfile}")
