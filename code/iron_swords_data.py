"""The person table for the iron_swords_locations map, from one place only.

Everything that builds the map goes through load_people(). Today that is the
Apps Script deployment of the google sheet (~/Documents/iron_swords_export.gs);
when the data moves to Wix, this function is the single edit.

The properties of a feature are a verbatim oct7database.csv row -- same 28
column names -- plus 'deathcoo'. So a person here is a dict keyed by the csv
headers, with two parsed extras:

    event_coo   (lat, lon) or None
    death_coo   (lat, lon) or None, and only when it differs from event_coo

That "only when it differs" is the white-marker rule from the plan: a death
coordinate equal to the event coordinate is not a second place, it is the same
place written twice.
"""
import datetime
import json
import os
from urllib import request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# .txt holds the deployed endpoints, one per line. Line 6 is the old
# private_map12 deployment that map_export_loc.py reads; line 7 is the
# iron_swords export, which keeps the rows that have no coordinates.
ENDPOINT_LINE = 7


def endpoint():
    with open(os.path.join(ROOT, '.txt')) as f:
        return f.read().split('\n')[ENDPOINT_LINE].strip()


def fetch():
    with request.urlopen(endpoint()) as url:
        return json.load(url)


SHEET_EPOCH = datetime.date(1899, 12, 30)
DATE_COLUMNS = ('Event date', 'Death date')


def as_date(value):
    """yyyy-mm-dd, converting a spreadsheet serial when one turns up.

    Some cells reach the export as numbers rather than dates -- 45436 instead
    of 2024-05-24 -- because the sheet typed them numerically and Apps Script
    hands back a Number, which the export stringifies. Converting here rather
    than in the .gs keeps the fix live without a redeploy; the csv these come
    from has the right value, so a serial always means the sheet, never the data.
    """
    text = (value or '').strip()
    if not text.isdigit() or not 20000 < int(text) < 60000:
        return text
    return str(SHEET_EPOCH + datetime.timedelta(days=int(text)))


def load_people(path=None):
    """List of person dicts. Pass path to read a saved json instead of the web."""
    if path:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = fetch()

    people, converted = [], []
    for feature in data['features']:
        person = dict(feature['properties'])

        for column in DATE_COLUMNS:
            fixed = as_date(person.get(column))
            if fixed != (person.get(column) or '').strip():
                converted.append((person['pid'], column, person[column], fixed))
            person[column] = fixed

        geometry = feature.get('geometry')
        person['event_coo'] = tuple(reversed(geometry['coordinates'][:2])) \
            if geometry else None

        death = person.pop('deathcoo', '')
        person['death_coo'] = (death[1], death[0]) \
            if isinstance(death, list) and len(death) == 2 else None
        if person['death_coo'] == person['event_coo']:
            person['death_coo'] = None

        people.append(person)

    if converted:
        print(f'{len(converted)} spreadsheet serials read as dates '
              f'(fix the cell format in the sheet):')
        for pid, column, was, now in converted:
            print(f'    pid {pid:<6} {column}: {was!r} -> {now}')

    assert people, 'the deployment returned no features'
    assert 'מקום האירוע' in people[0], \
        'line %d of .txt is the old deployment: no place-name columns' % ENDPOINT_LINE
    return people


def save(people, path):
    """A local copy, so a build can be re-run without hitting the network."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(people, f, ensure_ascii=False)


if __name__ == '__main__':
    people = load_people()
    event = sum(p['event_coo'] is not None for p in people)
    death = sum(p['death_coo'] is not None for p in people)
    print(f'{len(people)} people, {event} with an event coordinate, '
          f'{death} with a death coordinate away from the event')