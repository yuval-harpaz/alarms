"""Export data to html map."""
import pandas as pd
import numpy as np
import geojson

df = pd.read_csv('/home/innereye/Documents/maps/foreign.csv')
geojson_features = []

# Iterate over the dataframe to create features
for ii in range(len(df)):
    coords = np.asarray(df['event_coordinates'][ii].split(', ')).astype(float)
    # Reverse coordinates to GeoJSON format (longitude, latitude)
    coords = list(coords)[::-1]
    # Define the feature properties
    name = f"{df['first name'][ii]} {df['last name'][ii]}"
    color = "FF0000" if 'kidnapped' in df['Status'][ii].lower() else "0000FF"
    event = df['Status'][ii]
    properties = {
        "name": name,
        "event": df['Status'][ii].split(';')[0],
    }
    # Create a GeoJSON feature
    feature = geojson.Feature(
        properties=properties,
        geometry=geojson.Point(coords)
    )
    geojson_features.append(feature)

# Create the GeoJSON FeatureCollection
geojson_data = geojson.FeatureCollection(geojson_features)

# Define the output path
geojson_path = '/home/innereye/Documents/Map/foreign.geojson'

# Save to a GeoJSON file
with open(geojson_path, 'w') as f:
    geojson.dump(geojson_data, f)


with open(geojson_path, 'r') as f:
    data = f.read()

with open('/home/innereye/Documents/Map/tmp2.html', 'r') as f:
    html = f.read()
before = html[:html.index("var geojsonData = {")]
after = html[html.index("var Killed = L.layerGroup()"):]
optxt = before + "var geojsonData = " + data + "\n" + after
with open('/home/innereye/Documents/Map/foreign2.html', 'w') as f:
    f.write(optxt)
print(f"GeoJSON file created: {geojson_path}")
