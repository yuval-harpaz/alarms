"""People whose exact place is public although the ring around them is not.

data/coord_exact.tsv, one row per publication (tab separated, because the
first column holds commas):

    pids         pids from oct7database.csv, comma separated
    source_text  link text of the publication that put the place in the open
    source_url   the publication itself. Both empty -> the place is shown
                 exact with nothing to link to; one of the two empty -> error
    note         for whoever reads the file; the build ignores it

It is keyed by pid because this is a fact about one person's place and not
about the area they stand in: their neighbours inside the same ring stay
blurred, and the ring is still drawn for them. A whole area whose addresses
were published is a source_url on the ring in data/coord_area.geojson, not a
row here.

A row applies to every point the person has, the death point as well as the
event one, which is what tells it apart from an area's own source_url. A ring
is drawn over addresses, so the publication behind it justifies an address
and the page keeps it off the death marks; these publications are about a
case, and the place somebody died in it is as much of the case as the place
they were taken from.

Names are never written in the file. The build looks each pid up in the csv
and prints the names it found, which is the check that the pid is the person
meant; a pid the csv does not have stops the build.
"""
import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, 'data', 'coord_exact.tsv')
COLUMNS = ('pids', 'source_text', 'source_url', 'note')


def parse(rows):
    """{pid: (source_text, source_url) or None} out of the tsv rows.

    Raises ValueError on anything that would otherwise be built around
    silently: a token that is not a pid, a pid in two rows, a link with text
    and no url or the other way round. Spaces around a pid -- the residue of a
    copy-paste -- are stripped and only mentioned.
    """
    exact, seen_in = {}, {}
    for number, row in enumerate(rows, 2):
        where = f'coord_exact.tsv row {number}'
        text = (row.get('source_text') or '').strip()
        url = (row.get('source_url') or '').strip()
        if bool(text) != bool(url):
            raise ValueError(f'{where}: source_text and source_url must be '
                             f'both filled or both empty, got '
                             f'{text!r} / {url!r}')
        source = (text, url) if url else None

        tokens = (row.get('pids') or '').split(',')
        tokens = [t for t in tokens if t.strip()]
        if not tokens:
            print(f'  {where} lists nobody and does nothing')
            continue
        padded = [t for t in tokens if t != t.strip()]
        if padded:
            print(f'  {where}: spaces around {", ".join(repr(t) for t in padded)}'
                  f' stripped')
        for token in tokens:
            token = token.strip()
            if not token.isdigit():
                raise ValueError(f'{where}: {token!r} is not a pid')
            pid = int(token)
            if pid in seen_in:
                raise ValueError(f'{where}: pid {pid} is already in row '
                                 f'{seen_in[pid]}')
            seen_in[pid] = number
            exact[pid] = source
    return exact


def load_exact(people, path=PATH):
    """{pid: (source_text, source_url) or None}, checked against the people.

    Prints one line per row of the file with the names the pids resolve to,
    so a valid pid that is the wrong person is seen at build time rather than
    on the map.
    """
    if not os.path.exists(path):
        print(f'no {os.path.relpath(path, ROOT)}: nobody is exact inside a ring')
        return {}
    with open(path, encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        missing = [c for c in COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f'coord_exact.tsv lacks column(s) '
                             f'{", ".join(missing)}')
        rows = list(reader)

    exact = parse(rows)
    names = {p['pid']: f'{p["שם פרטי"]} {p["שם משפחה"]}'.strip()
             for p in people}
    unknown = sorted(pid for pid in exact if pid not in names)
    if unknown:
        raise ValueError(f'coord_exact.tsv names pid(s) not in oct7database.csv: '
                         f'{" ".join(str(p) for p in unknown)}')

    print(f'\n{os.path.relpath(path, ROOT)}: {len(exact)} people shown exact '
          f'inside a ring')
    for number, row in enumerate(rows, 2):
        pids = [int(t) for t in (row.get('pids') or '').split(',') if t.strip()]
        if not pids:
            continue
        link = (row.get('source_text') or '').strip() or 'no link'
        note = (row.get('note') or '').strip()
        print(f'  row {number}: {len(pids):>3}  {link:<10} {note}')
        print(f'      {", ".join(names[p] for p in pids)}')
    return exact
