"""Where a person with no coordinate of their own goes, and who is left out.

A place name is a path: 'רצועת עזה; רפיח; מחנה פליטים' is Rafah refugee camp
inside Rafah inside the Gaza Strip. The circle file holds a centre for some of
those paths and not others, so every place without a coordinate falls into one
of four cases:

    circle    the place itself has a circle
    lumped    it has no circle, but a shorter path of it does -- the people are
              drawn on that coarser circle, which is a loss of detail and is
              reported so the finer coordinate can be collected later
    region    too big, or too linear, to be a 500 m circle: 'רצועת עזה' is not a
              point and a circle in the middle of it would be a claim about
              where these people died. Nothing is drawn. Two ways to be here --
              the name is a shorter path of places that do have circles, or it
              carries a row in the circle file with no lat/lon and
              source = too_general, which is how a region nobody has subdivided
              yet (עוטף עזה, כביש 234) opts out by hand.
    missing   no circle anywhere on its path -- the work queue

The region test runs before the lump test only in the sense that a place with
its own circle short-circuits both; a place that is both a parent of circles
and a child of one is lumped, because the parent circle is a real point that
someone judged placeable, while being a parent proves only that the name has
named sub-places.

    python code/iron_swords_places.py     # the reports, on live data
"""
import csv
import os

from normalize_semicolons import normalize

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIRCLES = os.path.join(ROOT, 'data', 'coord_circle.csv')


def load_circles():
    """(circles, declined, aliases), keyed on the normalised name so that 'א;ב'
    and 'א; ב' are one place.

    A row with no lat/lon is a place deliberately left off the map, not an
    unfinished one. Two kinds:

        source = too_general              no marker at all
        source = alias: <other name_he>   the same place under another name

    The alias is for siblings, which the ';' path cannot express: 'ליד מסדרון
    נצרים' and 'מסדרון נצרים' sit side by side under 'רצועת עזה; עזה', so
    neither is a prefix of the other, but they are one place on the ground.
    """
    circles, declined, aliases = {}, {}, {}
    with open(CIRCLES, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            name = normalize(row['name_he'])
            if not row['lat'] or not row['lon']:
                source = (row['source'] or 'too_general').strip()
                if source.startswith('alias:'):
                    aliases[name] = normalize(source.split(':', 1)[1])
                else:
                    declined[name] = source
                continue
            circles[name] = {
                'name_he': name,
                'name_en': row['name_en'],
                'lat': float(row['lat']),
                'lon': float(row['lon']),
                'radius_m': float(row['radius_m'] or 500),
            }

    for name, target in sorted(aliases.items()):
        if target not in circles:
            print(f'alias points at a name with no circle: {name} -> {target}')
    return circles, declined, aliases


def parts(place):
    return [p for p in normalize(place).split('; ') if p]


def parents(place):
    """Every shorter path of a place, longest first: the most specific parent
    is the one we would rather lump into."""
    p = parts(place)
    return ['; '.join(p[:i]) for i in range(len(p) - 1, 0, -1)]


def resolve(place, circles, declined, aliases):
    """(kind, circle). circle is None for 'region' and 'missing'."""
    place = normalize(place)
    if place in circles:
        return 'circle', circles[place]
    if place in aliases and aliases[place] in circles:
        return 'alias', circles[aliases[place]]
    if place in declined:
        return 'region', None
    for parent in parents(place):
        if parent in circles:
            return 'lumped', circles[parent]
        if parent in declined:
            break       # the parent is a region; a child of it is not lumpable
    prefix = place + '; '
    if any(name.startswith(prefix) for name in circles):
        return 'region', None
    return 'missing', None


def place_people(people):
    """Attach a circle to everyone with no event coordinate.

    Returns (circles_used, cases) where cases maps kind -> place -> pids, kept
    so the caller can print the two reports and write them to the coverage file.
    """
    circles, declined = load_circles()
    cases = {'circle': {}, 'lumped': {}, 'region': {}, 'missing': {}}

    for person in people:
        if person['event_coo'] is not None:
            person['circle'] = None
            continue
        place = normalize(person['מקום האירוע'])
        person['circle'] = None
        kind, circle = ('missing', None) if not place \
            else resolve(place, circles, declined)
        person['circle'] = circle
        why = declined.get(place, 'parent of finer circles') \
            if kind == 'region' else ''
        entry = cases[kind].setdefault(place, {'pids': [], 'into': circle,
                                               'why': why})
        entry['pids'].append(person['pid'])

    return circles, cases


def pid_list(pids, limit=25):
    shown = ', '.join(str(p) for p in sorted(pids)[:limit])
    return shown + (f', ... (+{len(pids) - limit})' if len(pids) > limit else '')


def report(cases):
    """The two printouts: detail lost to lumping, and places never drawn."""
    lumped = cases['lumped']
    if lumped:
        people = sum(len(e['pids']) for e in lumped.values())
        print(f'\nlumped into a coarser circle -- {len(lumped)} places, '
              f'{people} people.')
        print('the finer location is not known; collect it and these move:')
        for place, entry in sorted(lumped.items(),
                                   key=lambda kv: -len(kv[1]['pids'])):
            print(f'  {place}\n      -> {entry["into"]["name_he"]}   '
                  f'({len(entry["pids"])} people)')
            print(f'      pid {pid_list(entry["pids"])}')

    region = cases['region']
    if region:
        people = sum(len(e['pids']) for e in region.values())
        print(f'\ntoo general to place -- {len(region)} names, {people} people, '
              f'no marker drawn.')
        print('a 500 m circle in the middle of these would invent a location:')
        for place, entry in sorted(region.items(),
                                   key=lambda kv: -len(kv[1]['pids'])):
            print(f'  {place}   ({len(entry["pids"])} people, {entry["why"]})')
            print(f'      pid {pid_list(entry["pids"])}')

    missing = cases['missing']
    if missing:
        people = sum(len(e['pids']) for e in missing.values())
        print(f'\nno circle anywhere on the path -- {len(missing)} places, '
              f'{people} people. run code/coverage_report.py and '
              f'code/fix_circles.py:')
        for place, entry in sorted(missing.items(),
                                   key=lambda kv: -len(kv[1]['pids'])):
            label = place or '(no place name at all)'
            print(f'  {label}   ({len(entry["pids"])} people)')
            print(f'      pid {pid_list(entry["pids"])}')


if __name__ == '__main__':
    from iron_swords_data import load_people

    people = load_people()
    circles, cases = place_people(people)
    on_circle = sum(1 for p in people
                    if p['event_coo'] is None and p['circle'])
    print(f'{len(people)} people, '
          f'{sum(p["event_coo"] is not None for p in people)} with a coordinate, '
          f'{on_circle} on a circle')
    report(cases)