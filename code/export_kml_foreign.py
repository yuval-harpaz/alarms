"""Plot alarms from Lebanon according to latitude."""
import pandas as pd
import numpy as np
import simplekml
import geojson
# import kml2geojson

type_colors = {0: "ff0000ff", 1: "ff00ff00"}
df = pd.read_csv('/home/innereye/Documents/maps/foreign.csv')

kml = simplekml.Kml()
for ii in range(len(df)):
    coords = np.asarray(df['event_coordinates'][ii].split(', ')).astype(float)
    # coords = [[coords[0]], [coords[1]]]
    pnt = kml.newpoint(name=df["first name"][ii]+' '+df["last name"][ii], coords=[coords[::-1]])
    if 'kidnapped' in df['Status'][ii]:
        pnt.style.iconstyle.color = "ffff5555"
    else:
        pnt.style.iconstyle.color = "ff0000ff"
    pnt.style.iconstyle.scale = 1  # Set size
    pnt.style.iconstyle.icon.href = 'https://maps.google.com/mapfiles/kml/shapes/dot.png'
# df.apply(lambda X: kml.newpoint(name=X["name"], coords=[( X["longitude"],X["latitude"])]) ,axis=1)
path = '/home/innereye/Documents/maps/test.kml'
kml.save(path=path)

json = kml2geojson.convert(path)
st, js = kml2geojson.convert(path, style_type='leaflet')


## import with
geojson_features = []

# Iterate over the dataframe to create features
for ii in range(len(df)):
    coords = np.asarray(df['event_coordinates'][ii].split(', ')).astype(float)
    # Reverse coordinates to GeoJSON format (longitude, latitude)
    coords = list(coords)[::-1]
    # Define the feature properties
    name = f"{df['first name'][ii]} {df['last name'][ii]}"
    color = "FF0000" if 'kidnapped' in df['Status'][ii].lower() else "0000FF"
    properties = {
        "title": name,
        "description": df['Status'][ii],
        "marker-symbol": "point",
        "marker-color": color,
        # "name": name,
        # "color": color,
    }
    # Create a GeoJSON feature
    feature = geojson.Feature(
        geometry=geojson.Point(coords),
        properties=properties
    )
    geojson_features.append(feature)

# Create the GeoJSON FeatureCollection
geojson_data = geojson.FeatureCollection(geojson_features)

# Define the output path
geojson_path = '/home/innereye/Documents/maps/test.geojson'

# Save to a GeoJSON file
with open(geojson_path, 'w') as f:
    geojson.dump(geojson_data, f)

print(f"GeoJSON file created: {geojson_path}")
