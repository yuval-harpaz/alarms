"""Check Hebrew<->English place names for one-to-one consistency.

Which dictionary is authoritative depends on the column, and this follows what
code/war23_api.py actually does:

  Locations. db2api sends 'מקום האירוע' -> eventLocationHe and 'Event location'
  -> eventLocationEn straight from the csv, and locations are absent from
  require_translation. So the csv's own column pairing IS the location
  dictionary, and the only thing to enforce is that the pairing is one-to-one.
  data/location_dictionary.csv is derived -- nothing in the live pipeline reads
  it, only the stale code/locations_heb2en.py -- so drift against it is reported
  as advisory, never as truth.

  Residence and the other single-language columns. These reach the api through
  require_translation, which looks up dictionary[key][value] in
  dictionaries.json with no fallback, so a value missing there is a KeyError
  that stops the upload. Those are reported as api_breaking.

Nothing is written to the data files. Issues go to a tsv that
code/fix_locations.py reads to drive the resolution dialog.

    python code/check_locations.py            # report
    python code/check_locations.py --quiet    # only the summary and the tsv
"""
import csv
import json
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'data', 'oct7database.csv')
EXTRA = os.path.join(ROOT, 'data', 'oct7database_additional.csv')
LOCDICT = os.path.join(ROOT, 'data', 'location_dictionary.csv')
DICTS = os.path.join(ROOT, 'data', 'dictionaries.json')
OUT = os.path.join(ROOT, 'data', 'location_issues.tsv')

PAIRS = [('מקום האירוע', 'Event location'), ('מקום המוות', 'Death location')]
# mirrors require_translation in code/war23_api.py: api field -> db column
REQUIRE_TRANSLATION = {'genderEn': 'Gender', 'residenceHe': 'Residence',
                       'countryHe': 'Country', 'roleHe': 'Role',
                       'statusEn': 'Status', 'frontEn': 'front',
                       'causeOfDeathHe': 'סיבת המוות'}
HEB = set(range(0x0590, 0x0600))


def is_hebrew(text):
    return any(ord(c) in HEB for c in text)


def is_latin(text):
    return any(c.isalpha() and ord(c) < 128 for c in text)


def rows(path):
    with open(path, encoding='utf-8') as f:
        return list(csv.DictReader(f))


def main():
    quiet = '--quiet' in sys.argv
    db, extra = rows(DB), rows(EXTRA)
    with open(LOCDICT, encoding='utf-8') as f:
        locdict = {r['Hebrew'].strip(): r['English'].strip() for r in csv.DictReader(f)}
    with open(DICTS, encoding='utf-8') as f:
        dicts = json.load(f)

    # Hebrew -> {English: [pids]} as actually paired inside the tables
    he2en = defaultdict(lambda: defaultdict(list))
    en2he = defaultdict(lambda: defaultdict(list))
    he_seen = defaultdict(list)
    for r in db:
        for he_col, en_col in PAIRS:
            he, en = r[he_col].strip(), r[en_col].strip()
            if not he:
                continue
            he_seen[he].append(r['pid'])
            he2en[he][en].append(r['pid'])
            if en:
                en2he[en][he].append(r['pid'])
    for r in extra:                       # no English columns of its own
        for he_col, _ in PAIRS:
            if r[he_col].strip():
                he_seen[r[he_col].strip()].append(r['pid'])

    issues = []

    def add(kind, field, he, en, pids, note=''):
        issues.append({'kind': kind, 'field': field, 'hebrew': he, 'english': en,
                       'n': len(pids), 'pids': ','.join(map(str, pids[:40])),
                       'note': note})

    for he, forms in sorted(he2en.items()):
        named = {e: p for e, p in forms.items() if e}
        blank = forms.get('', [])
        if len(named) > 1:
            add('he_multi_en', 'location', he, ' | '.join(sorted(named)),
                [p for ps in named.values() for p in ps],
                'one Hebrew name, several English forms')
        if blank:
            add('no_english', 'location', he, '', blank,
                'Hebrew name with an empty English cell')
        for en in named:
            if is_hebrew(en):
                add('hebrew_in_english', 'location', he, en, named[en],
                    'Hebrew characters in the English column')

    for en, forms in sorted(en2he.items()):
        if len(forms) > 1:
            add('en_multi_he', 'location', ' | '.join(sorted(forms)), en,
                [p for ps in forms.values() for p in ps],
                'one English name, several Hebrew forms')
        if is_latin(en) is False:
            add('no_latin_in_english', 'location', ' | '.join(forms), en,
                [p for ps in forms.values() for p in ps],
                'English column holds no Latin letters')

    for he, pids in sorted(he_seen.items()):
        if he not in locdict:
            add('not_in_dictionary', 'location', he,
                sorted(k for k in he2en.get(he, {}) if k)[:1] and
                sorted(k for k in he2en[he] if k)[0] or '', pids,
                'used in the data, absent from location_dictionary.csv')
        else:
            used = {e for e in he2en.get(he, {}) if e}
            if used and locdict[he] not in used:
                add('dictionary_conflict', 'location', he,
                    f'dict={locdict[he]} | data={" | ".join(sorted(used))}', pids,
                    'dictionary and data disagree')

    unused = sorted(set(locdict) - set(he_seen))

    # Columns the api translates through dictionaries.json. war23_api.py:117 does
    # dictionary[key][value] with no fallback, so an unknown value is a KeyError
    # that stops that person being uploaded.
    for key, col in REQUIRE_TRANSLATION.items():
        known = dicts.get(key, {})
        unknown = defaultdict(list)
        for r in db:
            v = r[col].strip()
            if v and v not in known:
                unknown[v].append(r['pid'])
        for v, pids in sorted(unknown.items()):
            add('api_breaking', col, v, '', pids,
                f'missing from dictionaries.json[{key}] -> KeyError on upload')
        for v, translated in known.items():
            if not isinstance(translated, str):
                add('api_breaking', col, v, str(translated), [],
                    f'dictionaries.json[{key}] holds a list, not a string')

    # a compound name should translate segment by segment the same way everywhere
    seg = defaultdict(lambda: defaultdict(set))
    for he, forms in he2en.items():
        for en in forms:
            if not en:
                continue
            hp, ep = [x.strip() for x in he.split(';')], [x.strip() for x in en.split(';')]
            if len(hp) == len(ep):
                for a, b in zip(hp, ep):
                    seg[a][b].add(he)
    for a, forms in sorted(seg.items()):
        if len(forms) > 1:
            add('segment_inconsistent', 'location', a,
                ' | '.join(f'{b} ({len(v)}x)' for b, v in sorted(forms.items())), [],
                'the same Hebrew segment is translated differently')

    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, delimiter='\t',
                           fieldnames=['kind', 'field', 'hebrew', 'english', 'n', 'pids', 'note'])
        w.writeheader()
        w.writerows(issues)

    counts = defaultdict(int)
    for i in issues:
        counts[i['kind']] += 1
    if not quiet:
        for kind in sorted(counts):
            print(f'\n===== {kind} ({counts[kind]}) '
                  f'{"=" * max(0, 50 - len(kind))}')
            for i in issues:
                if i['kind'] == kind:
                    print(f"  {i['hebrew']:38s} -> {i['english']:50s} "
                          f"{i['n']:>4} people")
    print(f'\n{len(he_seen)} distinct Hebrew place names, '
          f'{len(locdict)} dictionary entries, {len(unused)} of them unused')
    print(f'{len(issues)} issues written to {OUT}')
    for kind in sorted(counts):
        print(f'   {counts[kind]:>4}  {kind}')


if __name__ == '__main__':
    main()
