"""Where a person with no coordinate of their own goes, and who is left out.

A place name is a path: 'רצועת עזה; רפיח; מחנה פליטים' is Rafah refugee camp
inside Rafah inside the Gaza Strip. The circle file holds a centre for some of
those paths and not others, so every place without a coordinate falls into one
of four cases:

    circle    the place itself has a circle
    lumped    it has no circle, but a shorter path of it does -- the people are
              drawn on that coarser circle, which is a loss of detail and is
              reported so the finer coordinate can be collected later
    region    too big, or too linear, to carry one dot, and nothing is drawn.
              Two ways to be here -- the name is a shorter path of places that
              do have circles, or it carries a row in the circle file with no
              lat/lon and comment = too_general.
    missing   no circle anywhere on its path -- the work queue

A circle whose row says too_general *and* has a lat/lon is drawn like any
other, at a point chosen so that its people are on the map at all rather than
at a point anyone knows: עוטף עזה, כביש 234, a third of the Strip. It is
flagged, and the build lists those places and their counts on every run --
they are the standing caveat of the map, which is why that list is the one
thing the build prints when not asked to be verbose.

The region test runs before the lump test only in the sense that a place with
its own circle short-circuits both; a place that is both a parent of circles
and a child of one is lumped, because the parent circle is a real point that
someone judged placeable, while being a parent proves only that the name has
named sub-places.

    python code/iron_swords_places.py     # the reports, on live data
"""
import csv
import os
from collections import Counter

from normalize_semicolons import normalize

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIRCLES = os.path.join(ROOT, 'data', 'coord_circle.csv')


def load_circles(people=None):
    """(circles, declined, aliases), keyed on the normalised name so that 'א;ב'
    and 'א; ב' are one place.

    data/coord_circle.csv: name_he, lat, lon, comment. The comment is free
    text except for two values the build reads:

        too_general              with lat/lon: drawn there and flagged
                                 (circle['general']); without: no marker
        alias: <other name_he>   the same place under another name; no lat/lon

    The alias is for siblings, which the ';' path cannot express: 'ליד מסדרון
    נצרים' and 'מסדרון נצרים' sit side by side under 'רצועת עזה; עזה', so
    neither is a prefix of the other, but they are one place on the ground.

    Two rows with the same lat, lon are one circle; the other names become
    its aliases. That is how a few names too general to tell apart share one
    mark instead of piling up on one point, and the printout says which names
    were joined. Given people, the circle is named by the name that covers
    the most of them, a place counting for itself and for every shorter path
    of it: רצועת עזה covers the whole Strip, so it outranks צפון רצועת עזה,
    and three at עוטף עזה outrank one on כביש 234. Without people, the first
    row in the file names it.
    """
    circles, declined, aliases, at = {}, {}, {}, {}
    with open(CIRCLES, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            name = normalize(row['name_he'])
            comment = (row.get('comment') or '').strip()
            if not row['lat'] or not row['lon']:
                if comment.startswith('alias:'):
                    aliases[name] = normalize(comment.split(':', 1)[1])
                else:
                    declined[name] = comment or 'too_general'
                continue
            point = (float(row['lat']), float(row['lon']))
            if point in at:
                aliases[name] = at[point]
                circles[at[point]]['joined'].append(name)
                continue
            at[point] = name
            circles[name] = {
                'name_he': name,
                'lat': point[0],
                'lon': point[1],
                'general': comment == 'too_general',
                'joined': [],
            }

    if people:
        carried = Counter()
        for person in people:
            for col in ('מקום האירוע', 'מקום המוות'):
                place = normalize(person[col])
                if place:
                    carried.update([place] + parents(place))
        for name in [n for n, c in circles.items() if c['joined']]:
            circle = circles.pop(name)
            group = [name] + circle['joined']
            best = max(group, key=lambda n: (carried[n], -group.index(n)))
            circle['name_he'] = best
            circle['joined'] = [n for n in group if n != best]
            circles[best] = circle
            for other in circle['joined']:
                aliases[other] = best
            aliases.pop(best, None)

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
    circles, declined, aliases = load_circles(people)
    cases = {'circle': {}, 'alias': {}, 'lumped': {}, 'region': {}, 'missing': {}}

    for person in people:
        if person['event_coo'] is not None:
            person['circle'] = None
            continue
        place = normalize(person['מקום האירוע'])
        person['circle'] = None
        kind, circle = ('missing', None) if not place \
            else resolve(place, circles, declined, aliases)
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
    """The verbose printouts: names merged, detail lost to lumping, places
    with no circle. The too-general list is report_general(), printed on
    every build."""
    alias = cases['alias']
    if alias:
        people = sum(len(e['pids']) for e in alias.values())
        print(f'\nmerged into another name -- {len(alias)} places, '
              f'{people} people. two names for one place on the ground:')
        for place, entry in sorted(alias.items(),
                                   key=lambda kv: -len(kv[1]['pids'])):
            print(f'  {place}\n      -> {entry["into"]["name_he"]}   '
                  f'({len(entry["pids"])} people)')

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


def report_general(cases):
    """The places too general to be a point, and how many people stand on
    each: the ones drawn anyway at a chosen point, then the ones not drawn.
    Printed on every build, verbose or not."""
    drawn = {}
    for kind in ('circle', 'alias'):
        for place, entry in cases[kind].items():
            circle = entry['into']
            if not circle['general']:
                continue
            group = drawn.setdefault(circle['name_he'], {})
            group[place] = len(entry['pids'])
    if drawn:
        people = sum(sum(g.values()) for g in drawn.values())
        print(f'\ntoo general to place, drawn anyway at a chosen point -- '
              f'{len(drawn)} circles, {people} people:')
        for name, group in sorted(drawn.items(),
                                  key=lambda kv: -sum(kv[1].values())):
            print(f'  {sum(group.values()):>4}  {name}')
            if len(group) > 1 or name not in group:
                for place, n in sorted(group.items(), key=lambda kv: -kv[1]):
                    print(f'      {n:>4}  {place}')

    region = cases['region']
    if region:
        people = sum(len(e['pids']) for e in region.values())
        print(f'\ntoo general to place, no marker drawn -- {len(region)} names, '
              f'{people} people:')
        for place, entry in sorted(region.items(),
                                   key=lambda kv: -len(kv[1]['pids'])):
            print(f'  {len(entry["pids"]):>4}  {place}   ({entry["why"]})')
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