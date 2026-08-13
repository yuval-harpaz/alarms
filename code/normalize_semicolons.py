"""Put exactly one space after every ';' in the place-name columns.

A compound place name written 'דרום לבנון;דיר סיריאן' is a different string from
'דרום לבנון; דיר סיריאן', so it becomes a second entry in every list keyed by
place name -- which is how the same village ended up being asked for twice in
the circle queue.

Status is deliberately left alone: its parts are split on ';' and stripped, and
its spacing is its own convention.

    python code/normalize_semicolons.py           # dry run
    python code/normalize_semicolons.py --write

Edited as text, one token at a time, so the long quoted numbers in
הספריה הלאומית keep their quotes.
"""
import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TARGETS = {
    os.path.join(ROOT, 'data', 'oct7database.csv'):
        ['מקום האירוע', 'מקום המוות', 'Event location', 'Death location'],
    os.path.join(ROOT, 'data', 'oct7database_additional.csv'):
        ['מקום האירוע', 'מקום המוות'],
    os.path.join(ROOT, 'data', 'oct_7_9.csv'):
        ['location'],
}


def normalize(value):
    return re.sub(r'\s*;\s*', '; ', value).strip()


def split_top_level(line):
    out, cur, inq = [], [], False
    for ch in line:
        if ch == '"':
            inq = not inq
            cur.append(ch)
        elif ch == ',' and not inq:
            out.append(''.join(cur))
            cur = []
        else:
            cur.append(ch)
    out.append(''.join(cur))
    return out


def unquote(token):
    parsed = next(csv.reader([token]), [])
    return parsed[0] if parsed else ''


def quote(value):
    if any(c in value for c in ',"'):
        return '"%s"' % value.replace('"', '""')
    return value


def run(write):
    total = 0
    for path, columns in TARGETS.items():
        with open(path, newline='', encoding='utf-8') as f:
            raw = f.read()
        nl = '\r\n' if '\r\n' in raw else '\n'
        lines = raw.split(nl)

        with open(path, newline='', encoding='utf-8') as f:
            assert len([x for x in lines if x]) == len(list(csv.reader(f))), \
                f'{path}: a record spans several lines'

        header = split_top_level(lines[0])
        idx = [header.index(c) for c in columns if c in header]
        changed = []
        for n, line in enumerate(lines[1:], 1):
            if not line:
                continue
            tok = split_top_level(line)
            touched = False
            for i in idx:
                old = unquote(tok[i])
                new = normalize(old)
                if new != old:
                    tok[i] = quote(new)
                    changed.append((tok[0], header[i], old, new))
                    touched = True
            if touched:
                lines[n] = ','.join(tok)

        name = os.path.basename(path)
        if not changed:
            print(f'{name}: already consistent')
            continue
        print(f'{name}: {len(changed)} cells')
        for pid, col, old, new in changed:
            print(f'   pid {pid:>5}  [{col}]  {old!r} -> {new!r}')
        total += len(changed)
        if write:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                f.write(nl.join(lines))
    if total and not write:
        print('\ndry run; add --write to apply')
    elif write:
        print(f'\nwrote {total} cells')


if __name__ == '__main__':
    run('--write' in sys.argv)
