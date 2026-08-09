"""Who cannot be placed on the map, and where the missing coordinates are.

Reads the same deployed json the map build reads, so the numbers are current
rather than whatever csv happens to be on disk. Writes the work queue for
code/fix_circles.py: one row per place name that still has no coordinate,
biggest first.

    python code/coverage_report.py
"""
import csv
import json
import os
import re
from collections import defaultdict
from urllib import request


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'data', 'oct7database.csv')
CIRCLES = os.path.join(ROOT, 'data', 'coord_circle.csv')
OUT = os.path.join(ROOT, 'data', 'location_coverage.tsv')

PAIRS = [('מקום האירוע', 'Event location', 'event'),
         ('מקום המוות', 'Death location', 'death')]


def parse_coo(text):
    """Coordinates as (lat, lon). Some cells carry an invisible zero-width space."""
    text = re.sub(r'[^0-9.,\-]', '', str(text or ''))
    try:
        lat, lon = (float(x) for x in text.split(','))
        return lat, lon
    except ValueError:
        return None


def deployed():
    with open(os.path.join(ROOT, '.txt')) as f:
        address = f.read().split('\n')[6]
    with request.urlopen(address) as url:
        data = json.load(url)
    event, death = {}, {}
    for feat in data['features']:
        pid = feat['properties']['pid']
        if feat['geometry']:
            lon, lat = feat['geometry']['coordinates'][:2]
            event[pid] = (lat, lon)
        d = feat['properties'].get('deathcoo')
        if isinstance(d, list) and len(d) == 2:
            death[pid] = (d[1], d[0])
        elif isinstance(d, str) and parse_coo(d):
            death[pid] = parse_coo(d)
    return event, death


def known_circles():
    if not os.path.exists(CIRCLES):
        return {}
    with open(CIRCLES, newline='', encoding='utf-8') as f:
        return {r['name_he']: r for r in csv.DictReader(f)}


def main():
    with open(DB, newline='', encoding='utf-8') as f:
        db = list(csv.DictReader(f))
    event, death = deployed()
    circles = known_circles()

    missing = defaultdict(lambda: {'pids': [], 'en': set(), 'kind': set()})
    placed = {'event': 0, 'death_needed': 0, 'death': 0}
    unplaced_people = set()

    for r in db:
        pid = int(r['pid'])
        for he_col, en_col, kind in PAIRS:
            place = r[he_col].strip()
            if not place:
                continue
            if kind == 'event':
                have = pid in event
                placed['event'] += bool(have)
            else:
                # a death location only needs its own point when it differs
                if place == r['מקום האירוע'].strip():
                    continue
                placed['death_needed'] += 1
                have = pid in death
                placed['death'] += bool(have)
            if have:
                continue
            m = missing[place]
            m['pids'].append(pid)
            m['en'].add(r[en_col].strip())
            m['kind'].add(kind)
            unplaced_people.add(pid)

    rows = []
    for place, m in missing.items():
        rows.append({
            'name_he': place,
            'name_en': ' | '.join(sorted(x for x in m['en'] if x)),
            'n_people': len(m['pids']),
            'kind': ','.join(sorted(m['kind'])),
            'has_circle': 'yes' if place in circles else '',
            'pids': ','.join(str(p) for p in sorted(m['pids'])[:40]),
            '_pids': m['pids'],
        })
    rows.sort(key=lambda r: (-r['n_people'], r['name_he']))

    fields = ['name_he', 'name_en', 'n_people', 'kind', 'has_circle', 'pids']
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, delimiter='\t', fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)

    total = len(db)
    print(f'{total} people in the database')
    print(f'  event coordinate     : {placed["event"]:>5}   missing {total - placed["event"]}')
    print(f'  death coordinate     : {placed["death"]:>5}   '
          f'missing {placed["death_needed"] - placed["death"]} '
          f'(of {placed["death_needed"]} who died away from the event)')
    print(f'  cannot be placed     : {len(unplaced_people):>5} people, '
          f'{len(rows)} distinct place names')
    todo = [r for r in rows if not r['has_circle']]
    print(f'  still needing a circle: {len(todo)} places, '
          f'{len({p for r in todo for p in r["_pids"]})} people\n')
    print(f'top of the queue ({OUT}):')
    for r in rows[:20]:
        mark = ' [has circle]' if r['has_circle'] else ''
        print(f'  {r["n_people"]:>4}  {r["name_he"]:<38} {r["name_en"][:34]:<34}{mark}')


if __name__ == '__main__':
    main()
