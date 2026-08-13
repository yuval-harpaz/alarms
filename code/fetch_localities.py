"""Gaza Strip locality and neighbourhood boundaries from OpenStreetMap.

Writes data/coord_locality.geojson: one Feature per administrative area inside
the Strip, levels 8 (municipality), 9 (locality) and 10 (neighbourhood).

    python code/fetch_localities.py            # refresh from Overpass
    python code/fetch_localities.py --dry      # report, write nothing

This is a reference layer, not victim data. It answers "which neighbourhood is
this" behind an orange dot, and it carries no privacy meaning -- which is why
it is a separate file from data/coord_area.geojson, whose rings exist to hide
addresses the media never published.

Source is OpenStreetMap under ODbL: usable with attribution, which the map
gives alongside the Esri and GovMap credits. Bing's neighbourhood polygons,
which show the same thing, are proprietary and cannot be reused.
"""
import json
import os
import sys
import urllib.parse
import urllib.request

from shapely.geometry import Polygon, MultiPolygon, mapping
from shapely.ops import unary_union

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'coord_locality.geojson')

MIRRORS = ('https://overpass.kumi.systems/api/interpreter',
           'https://overpass-api.de/api/interpreter')

# Everything administrative inside the Gaza Strip relation. Going through the
# area rather than a bounding box keeps Sderot, Netivot and the Israeli
# regional councils out -- a box around the Strip catches all of them.
QUERY = """
[out:json][timeout:180];
rel["boundary"="administrative"]["name:en"="Gaza Strip"];
map_to_area -> .gs;
relation["boundary"="administrative"]["admin_level"~"^(8|9|10)$"](area.gs);
out geom;
"""

# Metres, in degrees. Enough to drop surveyor-grade vertices, not enough to
# move a boundary anywhere it matters.
SIMPLIFY = 0.00002


def overpass(query):
    last = None
    for host in MIRRORS:
        try:
            request = urllib.request.Request(
                host, data=urllib.parse.urlencode({'data': query}).encode(),
                headers={'User-Agent': 'alarms-iron-swords-map/1.0'})
            with urllib.request.urlopen(request, timeout=200) as response:
                return json.load(response)['elements']
        except Exception as error:          # noqa: BLE001 - report and try next
            print(f'  {host} failed: {error}')
            last = error
    raise SystemExit(f'every overpass mirror failed: {last}')


def rings(element):
    """Closed outer rings of a boundary relation, stitched from its ways.

    Overpass returns the members as separate open line segments in no useful
    order, so they are joined end to end until each ring closes.
    """
    segments = [[(p['lon'], p['lat']) for p in member['geometry']]
                for member in element.get('members', [])
                if member.get('type') == 'way' and member.get('geometry')
                and member.get('role') in ('outer', '')]

    closed = []
    while segments:
        ring = segments.pop(0)
        joined = True
        while joined and ring[0] != ring[-1]:
            joined = False
            for i, candidate in enumerate(segments):
                if candidate[0] == ring[-1]:
                    ring += candidate[1:]
                elif candidate[-1] == ring[-1]:
                    ring += candidate[::-1][1:]
                elif candidate[-1] == ring[0]:
                    ring = candidate[:-1] + ring
                elif candidate[0] == ring[0]:
                    ring = candidate[::-1][:-1] + ring
                else:
                    continue
                segments.pop(i)
                joined = True
                break
        if len(ring) > 3 and ring[0] == ring[-1]:
            closed.append(ring)
    return closed


def shape_of(element):
    parts = []
    for ring in rings(element):
        polygon = Polygon(ring)
        if not polygon.is_valid:
            polygon = polygon.buffer(0)
        if not polygon.is_empty and polygon.area > 0:
            parts.append(polygon)
    if not parts:
        return None
    merged = parts[0] if len(parts) == 1 else unary_union(parts)
    merged = merged.simplify(SIMPLIFY, preserve_topology=True)
    return merged if isinstance(merged, (Polygon, MultiPolygon)) else None


def main():
    print('fetching from overpass...')
    elements = overpass(QUERY)
    print(f'{len(elements)} administrative relations inside the Gaza Strip')

    features, skipped = [], []
    for element in elements:
        tags = element.get('tags', {})
        geometry = shape_of(element)
        name_en = tags.get('name:en') or tags.get('int_name')
        if geometry is None or not (name_en or tags.get('name')):
            skipped.append(tags.get('name:en') or tags.get('name') or element['id'])
            continue
        features.append({
            'type': 'Feature',
            'properties': {
                'name': tags.get('name', ''),
                'name_en': name_en or tags.get('name', ''),
                'name_he': tags.get('name:he', ''),
                'admin_level': tags.get('admin_level', ''),
                'osm_id': element['id'],
            },
            'geometry': mapping(geometry),
        })

    features.sort(key=lambda f: (int(f['properties']['admin_level'] or 0),
                                 f['properties']['name_en']))
    for level in ('8', '9', '10'):
        names = [f['properties']['name_en'] for f in features
                 if f['properties']['admin_level'] == level]
        print(f'  admin {level}: {len(names)}  {", ".join(names)}')
    if skipped:
        print(f'  no usable ring, skipped: {skipped}')

    if '--dry' in sys.argv:
        print('\ndry run, nothing written')
        return
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump({'type': 'FeatureCollection',
                   'attribution': '© OpenStreetMap contributors, ODbL',
                   'features': features}, f, ensure_ascii=False)
    print(f'\n{OUT}  {os.path.getsize(OUT) / 1e3:.0f} kB, {len(features)} areas')


if __name__ == '__main__':
    main()