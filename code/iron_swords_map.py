"""Build the iron_swords_locations map, public and private.

    python code/iron_swords_map.py            # writes to $WEBSITE (misc/docs)
    python code/iron_swords_map.py --cache x.json   # reuse a saved download

Four files, from one template:

    iron_swords_locations.html            public,  Hebrew
    iron_swords_locations_en.html         public,  English
    iron_swords_locations_private.html    private, Hebrew   (gitignored)
    iron_swords_locations_private_en.html private, English  (gitignored)

The private pair carries every exact coordinate we hold and no polygons. The
public pair replaces the coordinates of anyone inside an area whose addresses
were never published with that area's ring. Both pairs are one self-contained
file: the private coordinates are never written to a geojson beside the html,
because a file next to a page is not protected by a login on that page.

Marker colours follow war_victims_map_plan.md. The order of the parts of
Status carries the meaning:

    killed before kidnapped  -> died at the event; the place the body was
                                retrieved from is not a death location
    kidnapped before killed  -> red at the kidnapping site, white where he died
    released / rescued       -> blue, the person was not killed

An unknown Status stops the build only when those rules cannot decide it. A
new combination that the rules do handle is reported and built, so the daily
job does not fail on a wording the sheet has just started using.
"""
import csv
import json
import os
import sys
from collections import Counter

from shapely.geometry import shape

from iron_swords_data import load_people
from iron_swords_places import place_people, report
from polygons import load_polygons, area_for

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, 'code', 'iron_swords_template.html')
WEBSITE = os.environ.get('WEBSITE', os.path.expanduser('~/misc/docs/'))
BASENAME = 'iron_swords_locations'

# Where the map opens. Not the centre of mass of the markers: that sat inside
# Gaza, and the opening view should hold the whole picture.
CENTER = [32.236036, 35.137024]

# The eight values the plan tabulated. Anything else is reported.
KNOWN_STATUS = {
    'killed',
    'kidnapped; released',
    'kidnapped; killed; retrieved',
    'killed; kidnapped; retrieved',
    'killed; kidnapped; returned',
    'kidnapped; killed; returned',
    'kidnapped; rescued',
    'kidnapped; released; died',
}

CAMPAIGNS = [
    {'name': 'הכל', 'name_en': 'All', 'start': None, 'end': None},
    {'name': '7 באוקטובר', 'name_en': 'Oct 7', 'start': '2023-10-07', 'end': '2023-10-07'},
    {'name': 'חרבות ברזל', 'name_en': 'Iron Swords', 'start': '2023-10-07', 'end': None},
    {'name': 'מגן ברזל', 'name_en': 'Iron Shield', 'start': '2024-04-13', 'end': '2024-04-14'},
    {'name': 'חיצי הצפון', 'name_en': 'Northern Arrows', 'start': '2024-09-19', 'end': '2024-11-27'},
    {'name': 'עם כלביא', 'name_en': 'Twelve-Day War', 'start': '2025-06-13', 'end': '2025-06-24'},
    {'name': 'שאגת הארי', 'name_en': 'Epic Fury', 'start': '2026-02-28', 'end': None},
]

LABELS = {
    'he': {
        'title': 'מפת מיקומים – חרבות ברזל',
        'search': 'חיפוש לפי שם או מקום...',
        'killed': 'מקום האירוע',
        'kidnapped': 'מקום החטיפה',
        'died_elsewhere': 'מקום המוות',
        'approximate': 'מיקום מקורב',
        'areas': 'שכונה',
        'legend': 'מקרא',
        'halo': 'הילה',
        'localities': 'גבולות שכונות ויישובים (OSM)',
        'neighbourhoods': 'מרכזי שכונות (OCHA)',
        'front': 'זירה',
        'role': 'תפקיד',
        'status': 'סטטוס',
        'unspecified': 'לא צוין',
        'showing': 'מוצגים',
        'unplaced': 'ללא מיקום:',
        'filters': 'סינון',
        'by_event_date': 'תאריך האירוע',
        'by_death_date': 'תאריך המוות',
        'private': 'מפה פרטית – כוללת כתובות מדויקות שלא פורסמו. לא לשיתוף.',
    },
    'en': {
        'title': 'Iron Swords locations',
        'search': 'Search by name or place...',
        'killed': 'Event location',
        'kidnapped': 'Kidnapping location',
        'died_elsewhere': 'Death location',
        'approximate': 'Approximate location',
        'areas': 'Neighbourhood',
        'legend': 'Legend',
        'halo': 'Halo',
        'localities': 'Locality boundaries (OSM)',
        'neighbourhoods': 'Neighbourhood centres (OCHA)',
        'front': 'Front',
        'role': 'Role',
        'status': 'Status',
        'unspecified': 'Unspecified',
        'showing': 'Showing',
        'unplaced': 'not placed:',
        'filters': 'Filters',
        'by_event_date': 'Event date',
        'by_death_date': 'Death date',
        'private': 'Private map – holds exact unpublished addresses. Do not share.',
    },
}


def markers(person, unknown):
    """(red, blue, white) coordinates for one person, any of them None."""
    status = person['Status'].strip()
    parts = [p.strip() for p in status.split(';') if p.strip()]
    event, death = person['event_coo'], person['death_coo']

    if status not in KNOWN_STATUS:
        unknown[status] += 1

    if 'killed' in parts:
        if 'kidnapped' in parts and parts.index('killed') < parts.index('kidnapped'):
            # Killed at the scene, the body taken and later retrieved. Where it
            # was retrieved from is not where he died.
            return event, None, None
        return event, None, death
    if 'released' in parts or 'rescued' in parts:
        return None, event, None
    raise ValueError(
        f'pid {person["pid"]}: Status {status!r} has neither killed nor '
        f'released/rescued, so no colour rule applies. Add it to '
        f'war_victims_map_plan.md and to markers() in this file.')


def survivor_note(person):
    """(Hebrew, English) note for someone who came back from captivity, else None.

    Read off Status, not off the blue marker: someone with no coordinate has no
    marker at all, and it is exactly there that the note is needed. On a circle
    there is no colour to say it -- a released hostage sits in the same orange
    dot as the people murdered at that place, which is how pid 964 read as one
    of the Nova dead. Gendered, Hebrew having no neutral form here.
    """
    parts = [p.strip() for p in person['Status'].split(';') if p.strip()]
    if 'kidnapped' not in parts or 'killed' in parts or 'died' in parts:
        return None
    if 'released' not in parts and 'rescued' not in parts:
        return None
    return ('שורדת שבי' if person['Gender'] == 'F' else 'שורד שבי',
            'captivity survivor')


def person_record(person, red, blue, white):
    """The compact dict the page filters on. Absent keys keep the file small."""
    record = {
        'p': person['pid'],
        'n': f'{person["שם פרטי"]} {person["שם משפחה"]}'.strip(),
        'd': person['Event date'],
        's': person['Status'],
    }
    name_en = f'{person["first name"]} {person["last name"]}'.strip()
    if name_en:
        record['ne'] = name_en
    # Family name kept apart from the display name: the popups sort on it, and
    # a surname of two words cannot be recovered from 'first last'.
    for key, column in (('ln', 'שם משפחה'), ('lne', 'last name')):
        if person[column].strip():
            record[key] = person[column].strip()
    note = survivor_note(person)
    if note:
        record['note'], record['note_en'] = note
    for key, column in (('dd', 'Death date'), ('r', 'Role'), ('f', 'front'),
                        ('loc', 'מקום האירוע'), ('loce', 'Event location')):
        if person[column]:
            record[key] = person[column]
    if white:
        # The white marker stands somewhere else entirely -- a hospital, a spot
        # in Gaza -- so it has to be labelled with the death place. Labelling it
        # with the event place is what made pid 2416's x at Afula read as Jenin.
        for key, column in (('dloc', 'מקום המוות'), ('dloce', 'Death location')):
            if person[column]:
                record[key] = person[column]
    for key, coo in (('red', red), ('blue', blue), ('white', white)):
        if coo:
            record[key] = [round(coo[0], 6), round(coo[1], 6)]
    return record


def build(people, private, areas):
    """(records, polygons_used, hidden) for one visibility level."""
    records, rings, hidden = [], {}, []
    unknown = Counter()

    for person in people:
        red, blue, white = markers(person, unknown)
        record = person_record(person, red, blue, white)

        if not private:
            # A coordinate inside an area whose addresses were never published
            # is replaced by the ring. Applied to the death point too: it is a
            # coordinate in the same file, and it can fall in the same area.
            for key in ('red', 'blue', 'white'):
                coo = record.get(key)
                if not coo:
                    continue
                props = area_for(person['מקום האירוע'], coo, areas)
                if props is None or props['public_exact']:
                    continue
                record.pop(key)
                ring = next((g for p, g in areas if p['name_he'] == props['name_he']
                             and g is not None), None)
                if ring is None:
                    # Recorded as private but never drawn: nothing to show, and
                    # publishing the point is exactly what must not happen.
                    hidden.append((person['pid'], props['name_he']))
                    continue
                record['poly'] = props['name_he']
                rings[props['name_he']] = (props, ring)

        if person['circle']:
            record['circ'] = person['circle']['name_he']
        if not any(k in record for k in ('red', 'blue', 'white', 'circ', 'poly')):
            continue
        records.append(record)

    if unknown:
        print('\nStatus values not in the plan\'s table -- the colour rules '
              'handled them, check the table is still right:')
        for status, n in unknown.most_common():
            print(f'  {n:>4}  {status!r}')

    polygons = [{'name_he': props['name_he'],
                 'name_en': props.get('name_en') or props['name_he'],
                 'ring': [list(c) for c in ring.exterior.coords]}
                for props, ring in rings.values()]
    return records, polygons, hidden


def translation_gaps(people):
    """Hebrew that reaches the English map untranslated.

    Nothing breaks: every label falls back to the Hebrew. But the English map
    then shows a Hebrew name, so this is the queue for data/dictionaries.json.
    """
    gaps = {'מקום האירוע': Counter(), 'מקום המוות': Counter(), 'name': []}
    for person in people:
        for he_col, en_col in (('מקום האירוע', 'Event location'),
                               ('מקום המוות', 'Death location')):
            if person[he_col].strip() and not person[en_col].strip():
                gaps[he_col][person[he_col].strip()] += 1
        if not f'{person["first name"]}{person["last name"]}'.strip():
            gaps['name'].append(person['pid'])

    if not any(gaps[k] for k in gaps):
        return
    print('\nmissing English, shown in Hebrew on the English map:')
    for he_col in ('מקום האירוע', 'מקום המוות'):
        for place, n in gaps[he_col].most_common():
            print(f'  {n:>4}  {he_col}  {place}')
    if gaps['name']:
        print(f'  {len(gaps["name"]):>4}  people with no English name: '
              f'{", ".join(str(p) for p in gaps["name"][:20])}')


def localities_payload():
    """Gaza boundaries for the reference overlay, or [] if never fetched.

    Deliberately not merged into the polygon layer: these carry no privacy
    meaning, they only say which neighbourhood an orange dot stands in.
    """
    path = os.path.join(ROOT, 'data', 'coord_locality.geojson')
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as f:
        collection = json.load(f)

    areas = [{'name': p['name_en'] or p['name'],
              'name_he': p['name_he'] or p['name_en'] or p['name'],
              'level': p['admin_level'],
              'size': shape(feature['geometry']).area,
              'geometry': feature['geometry']}
             for feature in collection['features']
             for p in [feature['properties']]]

    # Biggest first, so the smallest area a point falls in is drawn last and is
    # the one that answers the hover. Sorting on admin_level would not do it:
    # as text '10' sorts before '8', which put the Gaza municipality on top of
    # every neighbourhood inside it and made all of them read עזה.
    areas.sort(key=lambda a: -a['size'])
    for area in areas:
        del area['size']
    return areas


def neighbourhoods_payload():
    """OCHA neighbourhood centres, or [] if never fetched. Names only, no shape:
    OSM has neighbourhood polygons for Gaza City alone, and these cover the
    Strip -- Rafah and Khan Yunis included, which have no polygons anywhere."""
    path = os.path.join(ROOT, 'data', 'coord_neighbourhood.csv')
    if not os.path.exists(path):
        return []
    with open(path, newline='', encoding='utf-8') as f:
        return [{'name': row['name'], 'municipality': row['municipality'],
                 'lat': float(row['lat']), 'lon': float(row['lon'])}
                for row in csv.DictReader(f) if row['name']]


def circles_payload(circles, records):
    used = {r['circ'] for r in records if 'circ' in r}
    return [{'name_he': c['name_he'], 'name_en': c['name_en'],
             'lat': c['lat'], 'lon': c['lon']}
            for name, c in sorted(circles.items()) if name in used]


def render(records, circles, polygons, localities, neighbourhoods, lang,
           private, unplaced):
    with open(TEMPLATE, encoding='utf-8') as f:
        html = f.read()

    dates = sorted(r['d'] for r in records if r['d'])
    labels = LABELS[lang]

    config = {
        'lang': lang,
        'labels': labels,
        'campaigns': [dict(c, start=c['start'] or dates[0],
                           end=c['end'] or None) for c in CAMPAIGNS],
        'center': CENTER,
        'zoom': 9,
        'date_min': dates[0],
        'date_max': dates[-1],
        'unplaced': unplaced,
    }
    banner = (f'<div id="private-banner">{labels["private"]}</div>'
              if private else '')

    for token, value in (
            ('__TITLE__', labels['title'] + (' (private)' if private else '')),
            ('__SEARCH_PLACEHOLDER__', labels['search']),
            ('__FILTERS__', labels['filters']),
            ('__LEGEND__', labels['legend']),
            ('__DIR__', 'rtl' if lang == 'he' else 'ltr'),
            ('__BY_EVENT_DATE__', labels['by_event_date']),
            ('__BY_DEATH_DATE__', labels['by_death_date']),
            ('__BANNER__', banner),
            ('__CONFIG__', json.dumps(config, ensure_ascii=False)),
            ('__PEOPLE__', json.dumps(records, ensure_ascii=False)),
            ('__CIRCLES__', json.dumps(circles, ensure_ascii=False)),
            ('__POLYGONS__', json.dumps(polygons, ensure_ascii=False)),
            ('__LOCALITIES__', json.dumps(localities, ensure_ascii=False)),
            ('__NEIGHBOURHOODS__', json.dumps(neighbourhoods, ensure_ascii=False)),
            ('__COMMENT__', f'{len(records)} people, built by '
                            f'code/iron_swords_map.py')):
        html = html.replace(token, value)
    return html


def main():
    cache = None
    if '--cache' in sys.argv:
        cache = sys.argv[sys.argv.index('--cache') + 1]
        cache = cache if os.path.exists(cache) else None

    people = load_people(cache)
    circles, cases = place_people(people)
    report(cases)
    translation_gaps(people)

    areas = load_polygons()
    localities = localities_payload()
    neighbourhoods = neighbourhoods_payload()
    unplaced = sum(len(e['pids']) for kind in ('region', 'missing')
                   for e in cases[kind].values())

    for private in (False, True):
        records, polygons, hidden = build(people, private, areas)
        payload = circles_payload(circles, records)
        for lang in ('he', 'en'):
            name = BASENAME + ('_private' if private else '') + \
                ('_en' if lang == 'en' else '') + '.html'
            path = os.path.join(WEBSITE, name)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(render(records, payload, polygons, localities,
                               neighbourhoods, lang, private, unplaced))
            print(f'{path}  {os.path.getsize(path) / 1e6:.1f} MB')

        kind = 'private' if private else 'public'
        print(f'  {kind}: {len(records)} people drawn, '
              f'{len(polygons)} rings, {len(payload)} circles')
        if hidden:
            places = Counter(name for _, name in hidden)
            print(f'  {len(hidden)} people are in an area with no ring and no '
                  f'publication, so the public map cannot show them at all:')
            for name, n in places.most_common():
                print(f'      {n:>4}  {name}')


if __name__ == '__main__':
    main()
