"""The person table for the iron_swords_locations map, from two sources.

Everything that builds the map goes through load_people(). The columns come
from data/oct7database.csv as published on github; only the coordinates come
from the Apps Script deployment of the google sheet
(~/Documents/iron_swords_export.gs), which is the only place they are kept.

The sheet imports the same csv, so the columns there ought to be identical, but
they are not always: the import can lag a push by up to an hour, and on the way
it rewrites cells it reads as dates (a Death date of '2023' came back as
1905-07-15) and trims trailing spaces. So anything with a csv column is read
from the csv, and the sheet is asked for the geometry alone.

Reading the csv from github rather than from the working copy means a build
would quietly ignore an edit that was never pushed, so load_people() compares
the two first and raises when they differ.

The properties of a person are a verbatim oct7database.csv row -- same 28
column names -- plus two parsed extras:

    event_coo   (lat, lon) or None
    death_coo   (lat, lon) or None, and only when it differs from event_coo

That "only when it differs" is the white-marker rule from the plan: a death
coordinate equal to the event coordinate is not a second place, it is the same
place written twice.
"""
import csv
import io
import json
import os
from urllib import request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# .txt holds the deployed endpoints, one per line. Line 6 is the old
# private_map12 deployment that map_export_loc.py reads; line 7 is the
# iron_swords export, which keeps the rows that have no coordinates.
ENDPOINT_LINE = 7

CSV_PATH = os.path.join(ROOT, 'data', 'oct7database.csv')
CSV_URL = ('https://raw.githubusercontent.com/yuval-harpaz/alarms/'
           'refs/heads/master/data/oct7database.csv')


def endpoint():
    with open(os.path.join(ROOT, '.txt')) as f:
        return f.read().split('\n')[ENDPOINT_LINE].strip()


def fetch():
    """The sheet deployment, as a geojson dict."""
    with request.urlopen(endpoint()) as url:
        return json.load(url)


def fetch_csv():
    """oct7database.csv as github serves it, as text."""
    with request.urlopen(CSV_URL) as url:
        return url.read().decode('utf-8')


def read_csv(text):
    """The csv text as a list of dicts, keyed by the header line.

    Cells are stripped, as the google sheet used to hand them over: 27 cells
    of the csv are typed with a space at one end, and a 'first last' built out
    of one of them reads as a double space on the page.
    """
    rows = []
    for row in csv.DictReader(io.StringIO(text)):
        if None in row:
            raise RuntimeError(f'oct7database.csv row of pid {row["pid"]} has '
                               f'more cells than the header: {row[None]}')
        rows.append({key: (value or '').strip() for key, value in row.items()})
    return rows


def check_pushed(rows):
    """Raise when the working copy of the csv is not what github is serving.

    The build reads github, so an unpushed edit would be invisible rather than
    wrong -- the map would be built from the previous version without a word.
    Compared row by row so that a stray newline at the end of the file, or the
    line endings, are not reported as a difference.
    """
    if not os.path.exists(CSV_PATH):
        print(f'no local {os.path.relpath(CSV_PATH, ROOT)}, nothing to compare')
        return
    with open(CSV_PATH, encoding='utf-8') as f:
        local = read_csv(f.read())
    here = {row['pid']: row for row in local}
    there = {row['pid']: row for row in rows}
    changed = sorted(pid for pid in here.keys() & there.keys()
                     if here[pid] != there[pid])
    only_here = sorted(here.keys() - there.keys())
    only_there = sorted(there.keys() - here.keys())
    if not (changed or only_here or only_there):
        return
    counts = ', '.join(f'{len(what)} {name}' for what, name in
                       ((changed, 'changed'), (only_here, 'only here'),
                        (only_there, 'only on github')) if what)
    pids = ' '.join((changed + only_here + only_there)[:10])
    raise RuntimeError(
        f'{os.path.relpath(CSV_PATH, ROOT)} differs from the copy on github '
        f'({counts}): pid {pids}. Push it and build again -- github serves the '
        f'new file at once, the google sheet can take an hour to catch up.')


def coordinates(data):
    """{pid: (event_coo, death_coo)} out of the sheet deployment.

    Both are (lat, lon) or None, and death_coo is None when it repeats the
    event coordinate.
    """
    coos = {}
    for feature in data['features']:
        properties = feature['properties']
        geometry = feature.get('geometry')
        event = tuple(reversed(geometry['coordinates'][:2])) if geometry else None
        death = properties.get('deathcoo', '')
        death = (death[1], death[0]) \
            if isinstance(death, list) and len(death) == 2 else None
        coos[int(properties['pid'])] = (event, None if death == event else death)
    return coos


def load_people(path=None):
    """List of person dicts.

    Pass path to reuse a saved sheet download instead of calling the
    deployment; the csv is then read from the working copy rather than from
    github, so a cached build needs no network and makes no claim about what
    has been pushed.
    """
    if path:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        with open(CSV_PATH, encoding='utf-8') as f:
            rows = read_csv(f.read())
        print(f'cached build: {os.path.relpath(CSV_PATH, ROOT)} as it is here, '
              f'pushed or not')
    else:
        data = fetch()
        rows = read_csv(fetch_csv())
        check_pushed(rows)

    coos = coordinates(data)
    people = []
    for row in rows:
        person = dict(row)
        # int, as the sheet had it: the pid reaches the page as a number and
        # the reports sort on it.
        person['pid'] = int(row['pid'])
        person['event_coo'], person['death_coo'] = coos.get(person['pid'],
                                                            (None, None))
        people.append(person)

    assert people, 'oct7database.csv has no rows'
    assert 'מקום האירוע' in people[0], 'oct7database.csv has no place columns'
    assert any(event for event, _ in coos.values()), \
        'line %d of .txt is the old deployment: no coordinates' % ENDPOINT_LINE

    # A pid the sheet has not imported yet has no coordinates and lands in the
    # unplaced count; one the sheet still has and the csv does not is dropped.
    # Both mean the sheet is behind, and neither is worth stopping a build for.
    missing = [p['pid'] for p in people if p['pid'] not in coos]
    dropped = sorted(coos.keys() - {p['pid'] for p in people})
    if missing:
        print(f'{len(missing)} in the csv but not in the sheet yet, so without '
              f'coordinates: pid {" ".join(str(x) for x in missing[:10])}')
    if dropped:
        print(f'{len(dropped)} in the sheet but not in the csv, dropped: '
              f'pid {" ".join(str(x) for x in dropped[:10])}')
    return people


def save(data, path):
    """A local copy of the sheet download, for --cache."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


if __name__ == '__main__':
    people = load_people()
    event = sum(p['event_coo'] is not None for p in people)
    death = sum(p['death_coo'] is not None for p in people)
    print(f'{len(people)} people, {event} with an event coordinate, '
          f'{death} with a death coordinate away from the event')
