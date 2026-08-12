"""Gaza Strip neighbourhood centres from OCHA oPt, via HDX.

Writes data/coord_neighbourhood.csv: name, municipality, lat, lon.

    python code/fetch_neighbourhoods.py          # refresh
    python code/fetch_neighbourhoods.py --dry    # report, write nothing

Points, not polygons. OSM has neighbourhood *polygons* for Gaza City only --
nothing for Rafah or Khan Yunis, where it holds two point features in total.
This dataset covers the whole Strip, which is why both exist side by side:
data/coord_locality.geojson draws the shapes where shapes are known, and this
names the neighbourhoods where they are not.

Source: OCHA occupied Palestinian territory, "State of Palestine - Gaza Strip
Neighbourhoods", CC BY. WGS84, so the coordinates go straight in.

The shapefile is read here by hand -- geopandas and fiona are not installed and
a point shapefile is a simple format: a 100 byte header then fixed records, and
a dbf of fixed-width fields beside it.
"""
import csv
import json
import os
import struct
import sys
import urllib.request
import zipfile

from shapely.geometry import Point, shape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'coord_neighbourhood.csv')
LOCALITIES = os.path.join(ROOT, 'data', 'coord_locality.geojson')

DATASET = 'gaza-strip-neighbourhoods'
HDX = 'https://data.humdata.org/api/3/action/package_show?id=' + DATASET
AGENT = {'User-Agent': 'alarms-iron-swords-map/1.0'}

FIELDS = ['name', 'name_ar', 'municipality', 'lat', 'lon', 'pcode']


def resource_url():
    with urllib.request.urlopen(
            urllib.request.Request(HDX, headers=AGENT), timeout=60) as response:
        result = json.load(response)['result']
    for res in result['resources']:
        if res['format'].upper() == 'SHP':
            print(f"{result['title']}  ({result['license_title']})")
            return res['url']
    raise SystemExit('no SHP resource in the HDX dataset')


def read_dbf(data):
    """Rows of a dbf as dicts. Fixed-width fields, no memo, no deleted rows."""
    count, header_len, rec_len = struct.unpack('<IHH', data[4:12])
    fields, pos = [], 32
    while data[pos] != 0x0D:
        fields.append((data[pos:pos + 11].split(b'\0')[0].decode('latin-1'),
                       data[pos + 16]))
        pos += 32
    rows = []
    for i in range(count):
        record = data[header_len + i * rec_len:header_len + (i + 1) * rec_len]
        offset, row = 1, {}
        for name, length in fields:
            row[name] = record[offset:offset + length].decode('utf-8', 'replace').strip()
            offset += length
        rows.append(row)
    return rows


def read_points(data):
    """(lat, lon) per record of a point shapefile."""
    points, pos = [], 100
    while pos < len(data):
        length = struct.unpack('>I', data[pos + 4:pos + 8])[0] * 2
        lon, lat = struct.unpack('<dd', data[pos + 12:pos + 28])
        points.append((round(lat, 6), round(lon, 6)))
        pos += 8 + length
    return points


def municipalities():
    """Name -> shape, for the level 8 areas already fetched from OSM.

    The dataset's own DISTRICT column is blank on 111 of the 149 rows, so the
    municipality is derived geometrically instead of trusted from the file.
    """
    if not os.path.exists(LOCALITIES):
        print('  no coord_locality.geojson; municipality column left empty')
        return []
    with open(LOCALITIES, encoding='utf-8') as f:
        return [(feature['properties']['name_en'], shape(feature['geometry']))
                for feature in json.load(f)['features']
                if feature['properties']['admin_level'] == '8']


def main():
    url = resource_url()
    path = os.path.join(ROOT, 'data', '.neighbourhoods.zip')
    urllib.request.urlretrieve(url, path)

    with zipfile.ZipFile(path) as archive:
        shp = next(n for n in archive.namelist() if n.lower().endswith('.shp'))
        dbf = next(n for n in archive.namelist() if n.lower().endswith('.dbf'))
        rows = read_dbf(archive.read(dbf))
        points = read_points(archive.read(shp))
    os.remove(path)

    if len(rows) != len(points):
        raise SystemExit(f'{len(rows)} attribute rows but {len(points)} points')

    areas = municipalities()
    out, counts = [], {}
    for row, (lat, lon) in zip(rows, points):
        point = Point(lon, lat)
        where = next((name for name, geom in areas if geom.contains(point)), '')
        counts[where or '(outside every municipality)'] = \
            counts.get(where or '(outside every municipality)', 0) + 1
        out.append({'name': row.get('Neighbourh', ''),
                    'name_ar': row.get('NameARB', ''),
                    'municipality': where,
                    'lat': lat, 'lon': lon,
                    'pcode': row.get('PCODE', '')})

    out.sort(key=lambda r: (r['municipality'], r['name']))
    print(f'\n{len(out)} neighbourhood points:')
    for name, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f'  {n:>4}  {name}')

    if '--dry' in sys.argv:
        print('\ndry run, nothing written')
        return
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(out)
    print(f'\n{OUT}  {os.path.getsize(OUT) / 1e3:.0f} kB')


if __name__ == '__main__':
    main()
