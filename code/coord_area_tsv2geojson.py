"""One-off: convert data/coord_area.tsv to data/coord_area.geojson.

English names are taken from the database, by matching the Hebrew area name
against "מקום האירוע" / "מקום המוות" and reading the paired English column.
Names that do not match are reported and left empty for task 1 to resolve.
"""
import csv
import json
from collections import defaultdict

TSV = 'data/coord_area.tsv'
DB = 'data/oct7database.csv'
OUT = 'data/coord_area.geojson'

# Areas whose Hebrew name does not appear in the database, so no English name
# can be read off it. Supplied by Yuval.
MANUAL_EN = {
    'נתיבות; קריית משה': 'Netivot; Kiryat Moshe',
    'כפר עזה; דור צעיר': 'Kfar Aza; Young Generation',
    'ניר יצחק; השכונה המזרחית': 'Nir Yitzhak; eastern neighborhood',
}


def english_names():
    pairs = defaultdict(set)
    with open(DB, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            for he, en in (('מקום האירוע', 'Event location'),
                           ('מקום המוות', 'Death location')):
                if row[he].strip():
                    pairs[row[he].strip()].add(row[en].strip())
    return pairs


def ring(cells):
    pts = []
    for cell in cells:
        cell = cell.strip()
        if len(cell) > 5:
            lat, lon = (float(x) for x in cell.split(','))
            pts.append((lon, lat))
    if not pts:
        return None
    if pts[0] != pts[-1]:
        pts.append(pts[0])
    if signed_area(pts) < 0:                 # RFC 7946 wants CCW exteriors
        pts.reverse()
    return pts


def signed_area(pts):
    return sum((pts[i][0] * pts[i + 1][1] - pts[i + 1][0] * pts[i][1])
               for i in range(len(pts) - 1)) / 2


en = english_names()
features, unmatched, ambiguous = [], [], []

with open(TSV, newline='', encoding='utf-8') as f:
    for row in csv.reader(f, delimiter='\t'):
        name_he = row[0].strip()
        if not name_he:
            continue
        source_text = row[1].strip() if len(row) > 1 else ''
        source_url = row[2].strip() if len(row) > 2 else ''
        candidates = sorted(en.get(name_he, []))
        if not candidates:
            name_en = MANUAL_EN.get(name_he, '')
            if not name_en:
                unmatched.append(name_he)
        else:
            if len(candidates) > 1:
                ambiguous.append((name_he, candidates))
            name_en = candidates[0]
        pts = ring(row[3:])
        features.append({
            'type': 'Feature',
            'properties': {
                'name_he': name_he,
                'name_en': name_en,
                'source_text': source_text,
                'source_url': source_url,
                'public_exact': bool(source_url),
            },
            'geometry': {'type': 'Polygon', 'coordinates': [pts]} if pts else None,
        })

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump({'type': 'FeatureCollection', 'features': features}, f,
              ensure_ascii=False, indent=1)
    f.write('\n')

rings = sum(1 for x in features if x['geometry'])
public = sum(1 for x in features if x['properties']['public_exact'])
print(f'{OUT}: {len(features)} areas, {rings} with a ring, {public} already public')
if unmatched:
    print(f'\nno English name found for {len(unmatched)} (left empty, for task 1):')
    for n in unmatched:
        print(f'  {n}')
if ambiguous:
    print(f'\nmore than one English name in the database:')
    for n, c in ambiguous:
        print(f'  {n} -> {c}')