"""Build the iron_swords_locations map, public and private.

    python code/iron_swords_map.py            # writes to $WEBSITE (misc/docs)
    python code/iron_swords_map.py --cache x.json   # reuse a saved download

The columns come from data/oct7database.csv on github and the coordinates from
the google sheet -- see iron_swords_data.py, which also stops a build whose csv
was never pushed.

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

Marker colours follow war_victims_map_plan.md. The first part of Status decides
the colour of the point, and the rest decides whether there is a second one:

    Status begins with kidnapped -> blue, the person was taken alive
    anything else                -> red, killed where the event happened
    killed before kidnapped      -> red only; the place the body was retrieved
                                    from is not a death location
    a death coordinate elsewhere -> an additional white marker

Blue therefore means taken alive, not survived. What became of a hostage is
told by the white marker and by the survivor note, not by the colour of the
point they were taken from.

An unknown Status stops the build only when those rules cannot decide it. A
new combination that the rules do handle is reported and built, so the daily
job does not fail on a wording the csv has just started using.
"""
import csv
import json
import os
import sys
from collections import Counter

from shapely.geometry import shape

from iron_swords_data import load_people
from iron_swords_places import load_circles, place_people, report, resolve
from normalize_semicolons import normalize
from polygons import load_polygons, area_for

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, 'code', 'iron_swords_template.html')
WEBSITE = os.environ.get('WEBSITE', os.path.expanduser('~/misc/docs/'))
BASENAME = 'iron_swords_locations'

# Used only if a build somehow draws nothing; the opening centre is computed
# per build from the marks inside REGION.
CENTER_FALLBACK = [32.236036, 35.137024]

# What the map is about. Marks outside it -- the UAE, Egypt -- are drawn and
# clickable, but get no say in where the map opens or how a filtered url frames
# itself: a midrange takes the extremes literally, so one point in the Gulf
# would put the centre in Saudi Arabia. Passed to the page, so the framing there
# uses the same box rather than a second copy of these numbers.
REGION = {'south': 29.0, 'north': 34.5, 'west': 33.0, 'east': 36.6}

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
    {'name': '7 באוקטובר', 'name_en': 'Oct 7', 'start': '2023-10-07', 'end': '2023-10-07'},
    {'name': 'חרבות ברזל (הכל)', 'name_en': 'Iron Swords (all)',
     'start': '2023-10-07', 'end': None},
    {'name': 'תמרון בעזה', 'name_en': 'Gaza ground manoeuvre',
     'start': '2023-10-27', 'end': '2025-10-10'},
    {'name': 'עם כלביא', 'name_en': 'Twelve-Day War', 'start': '2025-06-13', 'end': '2025-06-24'},
    {'name': 'שאגת הארי', 'name_en': 'Epic Fury', 'start': '2026-02-28', 'end': None},
]

# The site page the question mark beside the search box points at.
HELP_URL = ('https://www.oct7database.com/maps-and-data/'
            '%D7%9E%D7%AA%D7%A7%D7%A4%D7%AA-%D7%97%D7%9E%D7%90%D7%A1-'
            '%D7%A0%D7%92%D7%93-%D7%99%D7%A9%D7%A8%D7%90%D7%9C-(7-9.10.2023)')

LABELS = {
    'he': {
        'title': 'מפת מיקומים – חרבות ברזל',
        'search': 'חיפוש לפי שם או מקום...',
        'killed': 'מקום אירוע',
        'killed_exact': 'מקום אירוע - מדויק',
        'killed_approx': 'מקום אירוע - מקורב',
        'kidnapped': 'מקום חטיפה',
        'died': 'מקום מוות',
        'died_exact': 'מקום מוות - מדויק',
        'died_approx': 'מקום מוות - מקורב',
        'died_note': 'אם שונה ממקום האירוע',
        'hostages': 'חטופים',
        'at_event': '(אירוע)',
        'at_death': '(מוות)',
        'others': 'אחרים',
        'areas': 'שכונה\\ישוב',
        'legend': 'מקרא',
        'all': 'הכל',
        'clear': 'נקה',
        'help': 'מידע נוסף',
        'halo_hint': 'לחץ לשינוי עיצוב הטקסט',
        'localities': 'גבולות שכונות ויישובים (OSM)',
        'neighbourhoods': 'מרכזי שכונות (OCHA)',
        'front': 'זירה',
        'level_fronts': 'זירות',
        'level_regions': 'זירות ואזורים',
        'level_places': 'יישובים',
        'level_marks': 'מיקומים מדויקים',
        'to_level': 'מעבר לתצוגת',
        'by_status': 'צביעה לפי נהרגו / נחטפו',
        'by_roles': 'צביעה לפי תפקיד',
        'slice_killed': 'נהרגו במקום האירוע',
        'slice_taken': 'נחטפו חיים',
        'killed_short': 'נהרגו',
        'taken_short': 'נחטפו חיים',
        'role_civil': 'אזרחים, כבאים וצוותים רפואיים',
        'role_police': 'משטרה',
        'role_forces': 'חיילים, שב"כ וכיתות כוננות',
        'civil_short': 'אזרחים',
        'police_short': 'משטרה',
        'forces_short': 'כוחות',
        'g_strip': 'רצועת עזה',
        'g_envelope': 'עוטף עזה',
        'g_lebanon': 'דרום לבנון',
        'g_north': 'גבול הצפון',
        'no_survivors': 'ללא שורדי שבי ששוחררו או חולצו',
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
        'killed_exact': 'Event location - exact',
        'killed_approx': 'Event location - approximate',
        'kidnapped': 'Kidnapping location',
        'died': 'Death location',
        'died_exact': 'Death location - exact',
        'died_approx': 'Death location - approximate',
        'died_note': 'if different from the event location',
        'hostages': 'Hostages',
        'at_event': '(event)',
        'at_death': '(death)',
        'others': 'Others',
        'areas': 'Neighbourhood/locality',
        'legend': 'Legend',
        'all': 'All',
        'clear': 'Clear',
        'help': 'More information',
        'halo_hint': 'Click to change text styling',
        'localities': 'Locality boundaries (OSM)',
        'neighbourhoods': 'Neighbourhood centres (OCHA)',
        'front': 'Front',
        'level_fronts': 'Fronts',
        'level_regions': 'Fronts and regions',
        'level_places': 'Localities',
        'level_marks': 'Exact locations',
        'to_level': 'Show',
        'by_status': 'Colour by killed / taken',
        'by_roles': 'Colour by role',
        'slice_killed': 'Killed at the event',
        'slice_taken': 'Taken alive',
        'killed_short': 'killed',
        'taken_short': 'taken alive',
        'role_civil': 'Civilians, firefighters, medical teams',
        'role_police': 'Police',
        'role_forces': 'Soldiers, Shin Bet, standby squads',
        'civil_short': 'civilians',
        'police_short': 'police',
        'forces_short': 'forces',
        'g_strip': 'Gaza Strip',
        'g_envelope': 'Gaza envelope',
        'g_lebanon': 'South Lebanon',
        'g_north': 'Northern border',
        'no_survivors': 'released and rescued hostages not counted',
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

    # Blue is now "taken alive", full stop: any Status that opens with
    # kidnapped, whether or not it ends in killed. Red is left for those who
    # were killed where the event happened. What became of someone taken alive
    # is told by the white marker and by the survivor note, not by the colour
    # of the point they were taken from.
    taken_alive = bool(parts) and parts[0] == 'kidnapped'

    if 'killed' in parts:
        if 'kidnapped' in parts and parts.index('killed') < parts.index('kidnapped'):
            # Killed at the scene, the body taken and later retrieved. Where it
            # was retrieved from is not where he died.
            return event, None, None
    elif 'released' not in parts and 'rescued' not in parts:
        raise ValueError(
            f'pid {person["pid"]}: Status {status!r} has neither killed nor '
            f'released/rescued, so no colour rule applies. Add it to '
            f'war_victims_map_plan.md and to markers() in this file.')

    # A death coordinate only means something for someone who died; the people
    # who came home have one that is not a death place.
    white = death if 'killed' in parts else None
    return (None, event, white) if taken_alive else (event, None, white)


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


def death_circle(person, taken_alive, white, geometry):
    """The circle a hostage who died in Gaza is drawn on, or None.

    Only for someone taken alive who was later killed and whose death place has
    no coordinate of its own. Their death place is written without the
    'רצועת עזה' the event places carry -- bare רפיח, ג'באליה -- so the join runs
    through the alias rows in data/coord_circle.csv rather than matching by
    string. Fix the names in the csv and the aliases can go.
    """
    if not (taken_alive and 'killed' in person['Status']) or white:
        return None
    place = normalize(person['מקום המוות'])
    if not place or place == normalize(person['מקום האירוע']):
        return None
    circles, declined, aliases = geometry
    kind, circle = resolve(place, circles, declined, aliases)
    if circle and person['circle'] and \
            circle['name_he'] == person['circle']['name_he']:
        # Died where they were taken from, by two different spellings that land
        # on one circle. One dot, one list -- not a name in both of them.
        return None
    return (place, kind, circle)


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


def build(people, private, areas, geometry):
    """(records, polygons, hidden, unplaced_deaths, nowhere) per visibility level."""
    records, rings, hidden, nowhere = [], {}, [], []
    unknown, unplaced_deaths = Counter(), {}
    no_link_text = set()

    for person in people:
        red, blue, white = markers(person, unknown)
        record = person_record(person, red, blue, white)

        taken_alive = person['Status'].strip().startswith('kidnapped')
        found = death_circle(person, taken_alive, white, geometry)
        if found:
            place, kind, circle = found
            if circle:
                record['dcirc'] = circle['name_he']
            else:
                unplaced_deaths.setdefault((place, kind), []).append(person['pid'])

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
                # Which mark the ring stands in for. Zoomed out the page draws
                # a settlement as one circle split by colour, and a person whose
                # point was replaced still has to count as the red or the blue
                # they would have been. Only for an event mark: a ring standing
                # in for a white x is a death place, and that is counted at the
                # event, not twice.
                if key in ('red', 'blue'):
                    record['pk'] = key
                rings[props['name_he']] = (props, ring)

        # The publication that already put this area's addresses in the open.
        # It is the reason the marker is allowed to stand on the exact spot, so
        # the popup names it and links to it: the addresses were published
        # there, not here. Read from the event point, the one both the red and
        # the blue marker stand on, and gone from the record when that point
        # was replaced by a ring just above.
        coo = record.get('red') or record.get('blue')
        if coo:
            props = area_for(person['מקום האירוע'], coo, areas)
            if props and props['public_exact'] and props['source_url']:
                if not props['source_text']:
                    no_link_text.add(props['name_he'])
                else:
                    record['src'] = props['source_text']
                    record['url'] = props['source_url']

        if person['circle']:
            record['circ'] = person['circle']['name_he']
        # Someone with no coordinate, no circle and no ring is still written
        # out. Nothing draws them -- they carry no key to be drawn by -- but
        # the page's front view lumps every case of a front into one mark, and
        # a front that leaves its unplaced people out is counted short.
        if not any(k in record for k in ('red', 'blue', 'white', 'circ', 'poly',
                                          'dcirc')):
            nowhere.append(record['p'])
        records.append(record)

    if no_link_text:
        print('\npublished areas with a source_url but no source_text, so the '
              'popup has nothing to write the link on:')
        for name in sorted(no_link_text):
            print(f'  {name}')

    if unknown:
        print('\nStatus values not in the plan\'s table -- the colour rules '
              'handled them, check the table is still right:')
        for status, n in unknown.most_common():
            print(f'  {n:>4}  {status!r}')

    polygons = [{'name_he': props['name_he'],
                 'name_en': props.get('name_en') or props['name_he'],
                 'ring': [list(c) for c in ring.exterior.coords]}
                for props, ring in rings.values()]
    return records, polygons, hidden, unplaced_deaths, nowhere


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


def filter_translations(lang):
    """Raw value -> what the filter list shows, per language.

    data/dictionaries.json stores each pair in one direction only, and not the
    same direction for every column: frontEn and statusEn are English keyed to
    Hebrew, roleHe is Hebrew keyed to English. The csv holds the key side, so
    each language translates a different pair of fields and leaves the third.
    """
    with open(os.path.join(ROOT, 'data', 'dictionaries.json'), encoding='utf-8') as f:
        words = json.load(f)
    if lang == 'he':
        return {'f': words['frontEn'], 's': words['statusEn'], 'r': {}}
    return {'f': {}, 's': {}, 'r': words['roleHe']}


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
    used |= {r['dcirc'] for r in records if 'dcirc' in r}
    return [{'name_he': c['name_he'], 'name_en': c['name_en'],
             'lat': c['lat'], 'lon': c['lon']}
            for name, c in sorted(circles.items()) if name in used]


def map_center(records, circles, polygons, report=False):
    """Midrange of everything drawn inside REGION: (min + max) / 2 per axis.

    The midrange sits in the middle of the ground covered rather than in the
    middle of the crowd, so the sparse north weighs as much as the envelope.
    That also makes it defenceless against a single far-off mark, which is why
    it is computed over REGION alone.

    report says what was left out of the framing. Off by default: the centre is
    computed six times a build -- four files and the two summary lines -- and
    the same sentence six times reads as six different findings. The Hebrew
    public pass asks for it, and the count is the same for all six.
    """
    point = {c['name_he']: (c['lat'], c['lon']) for c in circles}
    ring = {}
    for poly in polygons:
        lats = [c[1] for c in poly['ring']]
        lons = [c[0] for c in poly['ring']]
        ring[poly['name_he']] = (sum(lats) / len(lats), sum(lons) / len(lons))

    lats, lons = [], []
    for record in records:
        for key in ('red', 'blue', 'white'):
            if key in record:
                lats.append(record[key][0])
                lons.append(record[key][1])
        for key, table in (('circ', point), ('dcirc', point), ('poly', ring)):
            if record.get(key) in table:
                lat, lon = table[record[key]]
                lats.append(lat)
                lons.append(lon)

    inside = [(lat, lon) for lat, lon in zip(lats, lons)
              if REGION['south'] <= lat <= REGION['north']
              and REGION['west'] <= lon <= REGION['east']]
    if not inside:
        return CENTER_FALLBACK
    lat_values = [lat for lat, _ in inside]
    lon_values = [lon for _, lon in inside]
    dropped = len(lats) - len(inside)
    if dropped and report:
        print(f'  {dropped} marks outside the region ignored when centring')
    return [round((min(lat_values) + max(lat_values)) / 2, 6),
            round((min(lon_values) + max(lon_values)) / 2, 6)]


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
        'center': map_center(records, circles, polygons,
                             report=lang == 'he' and not private),
        'region': REGION,
        'zoom': 9,
        'date_min': dates[0],
        'date_max': dates[-1],
        'unplaced': unplaced,
        'translate': filter_translations(lang),
    }
    banner = (f'<div id="private-banner">{labels["private"]}</div>'
              if private else '')

    for token, value in (
            ('__TITLE__', labels['title'] + (' (private)' if private else '')),
            ('__SEARCH_PLACEHOLDER__', labels['search']),
            ('__FILTERS__', labels['filters']),
            ('__LEGEND__', labels['legend']),
            ('__HELP_URL__', HELP_URL),
            ('__HELP_TITLE__', labels['help']),
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

    geometry = load_circles()
    for private in (False, True):
        records, polygons, hidden, unplaced_deaths, nowhere = build(
            people, private, areas, geometry)
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
        centre = map_center(records, payload, polygons)
        print(f'  {kind}: {len(records) - len(nowhere)} people drawn, '
              f'{len(nowhere)} carried without a location for the front view, '
              f'{len(polygons)} rings, {len(payload)} circles, '
              f'centre {centre[0]}, {centre[1]}')
        if hidden:
            places = Counter(name for _, name in hidden)
            print(f'  {len(hidden)} people are in an area with no ring and no '
                  f'publication, so the public map cannot show them at all:')
            for name, n in places.most_common():
                print(f'      {n:>4}  {name}')
        if unplaced_deaths and not private:
            total = sum(len(v) for v in unplaced_deaths.values())
            print(f'  {total} hostages died somewhere with no circle to put '
                  f'them on:')
            for (place, kind), pids in sorted(unplaced_deaths.items(),
                                              key=lambda kv: -len(kv[1])):
                print(f'      {len(pids):>4}  {place}  ({kind})  '
                      f'pid {", ".join(str(p) for p in pids)}')


if __name__ == '__main__':
    main()
