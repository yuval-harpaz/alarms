"""City and town names for the region, from OpenStreetMap.

Writes data/coord_place.csv: one row per populated place inside the map's own
box, with the Hebrew and the English name where OSM holds them.

    python code/fetch_places.py            # refresh from Overpass
    python code/fetch_places.py --dry      # report, write nothing

Why the map carries its own names instead of a labelled tile layer: the page is
built twice, Hebrew and English, and no keyless label overlay switches language.
Esri's own World_Boundaries_and_Places is English and the local script; CARTO's
label-only tiles render OSM's `name`, which is Hebrew inside Israel and Arabic
in Gaza; the services that do take a language parameter want an api key, and a
key in a self-contained public html is a key given away. OSM's place nodes hold
`name:he` and `name:en` themselves, so the build picks the language the same way
it picks it for everything else.

Cities and towns only. Villages are 4140 points of which barely half carry a
Hebrew name, and they would bury the map at any zoom that showed them.

Source is OpenStreetMap under ODbL: usable with attribution, which the map gives
alongside the Esri and GovMap credits.
"""
import csv
import json
import os
import sys
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'coord_place.csv')

MIRRORS = ('https://overpass-api.de/api/interpreter',
           'https://overpass.kumi.systems/api/interpreter')

# The box the map frames itself on -- REGION in iron_swords_map.py. Kept here as
# numbers rather than imported, because this script is run by hand and years
# apart from that one, and a silent change of framing should not silently change
# which names were fetched.
BOX = (29.0, 33.0, 34.5, 36.6)      # south, west, north, east

QUERY = """
[out:json][timeout:180];
node["place"~"^(city|town)$"](%s,%s,%s,%s);
out tags center;
"""


def overpass(query):
    """The first mirror that answers."""
    last = None
    for url in MIRRORS:
        try:
            request = urllib.request.Request(
                url, data=urllib.parse.urlencode({'data': query}).encode(),
                headers={'User-Agent': 'iron-swords-map/1.0'})
            with urllib.request.urlopen(request, timeout=240) as answer:
                return json.load(answer)
        except Exception as error:          # noqa: BLE001 -- try the next one
            print(f'  {url}: {error}')
            last = error
    raise SystemExit(f'no overpass mirror answered: {last}')


def rows(elements):
    """One row per place, sorted so a refresh makes a readable diff."""
    out = []
    for element in elements:
        tags = element.get('tags', {})
        name = tags.get('name', '').strip()
        he = tags.get('name:he', '').strip()
        en = tags.get('name:en', '').strip()
        if not (name or he or en):
            continue
        out.append({
            'osm_id': element['id'],
            'place': tags.get('place', ''),
            'lat': round(element['lat'], 6),
            'lon': round(element['lon'], 6),
            # The local name is the fallback both languages share: in Israel it
            # is the Hebrew, in Gaza and Lebanon the Arabic, and a name in the
            # wrong alphabet still says where you are.
            'name': name,
            'name_he': he,
            'name_en': en,
        })
    out.sort(key=lambda row: (row['place'], row['name_en'] or row['name']))
    return out


def main():
    print(f'asking overpass for cities and towns in {BOX}')
    data = overpass(QUERY % BOX)
    places = rows(data['elements'])
    kinds = {}
    for place in places:
        kinds.setdefault(place['place'], []).append(place)
    for kind, group in sorted(kinds.items()):
        he = sum(1 for p in group if p['name_he'])
        en = sum(1 for p in group if p['name_en'])
        print(f'  {kind:6} {len(group):5}   name:he {he:5}   name:en {en:5}')

    if '--dry' in sys.argv:
        print('--dry: nothing written')
        return
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(places[0].keys()))
        writer.writeheader()
        writer.writerows(places)
    print(f'{os.path.relpath(OUT, ROOT)}  {len(places)} places')


if __name__ == '__main__':
    main()
