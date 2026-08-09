"""Resolve the place-name issues found by code/check_locations.py.

Each issue is presented in a dialog offering the competing forms, a free-text
box for a new translation, and Skip. Every answer is appended to
data/location_decisions.tsv the moment it is given, so the session can be
interrupted and resumed -- answered issues are not asked again.

    python code/check_locations.py          # find the issues first
    python code/fix_locations.py            # answer them (dialog)
    python code/fix_locations.py --terminal # same, without a window
    python code/fix_locations.py --apply    # dry run: show what would change
    python code/fix_locations.py --apply --write   # actually edit the files

--apply never touches a file until you have seen the dry run. The csv is edited
as text, one token at a time, so the long quoted numbers in הספריה הלאומית keep
their quotes -- pandas would reformat them.
"""
import csv
import json
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'data', 'oct7database.csv')
DICTS = os.path.join(ROOT, 'data', 'dictionaries.json')
LOCDICT = os.path.join(ROOT, 'data', 'location_dictionary.csv')
ISSUES = os.path.join(ROOT, 'data', 'location_issues.tsv')
DECISIONS = os.path.join(ROOT, 'data', 'location_decisions.tsv')

PAIRS = [('מקום האירוע', 'Event location'), ('מקום המוות', 'Death location')]
ASKABLE = ('he_multi_en', 'en_multi_he', 'hebrew_in_english', 'no_english',
           'dictionary_conflict', 'segment_inconsistent', 'api_breaking')


# --------------------------------------------------------------- decisions ---

def load_decisions():
    if not os.path.exists(DECISIONS):
        return {}
    with open(DECISIONS, newline='', encoding='utf-8') as f:
        return {(r['kind'], r['key']): r for r in csv.DictReader(f, delimiter='\t')}


def record(kind, key, choice, scope, field=''):
    new = not os.path.exists(DECISIONS)
    with open(DECISIONS, 'a', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, delimiter='\t',
                           fieldnames=['kind', 'key', 'choice', 'scope', 'field'])
        if new:
            w.writeheader()
        w.writerow({'kind': kind, 'key': key, 'choice': choice, 'scope': scope,
                    'field': field})


# ------------------------------------------------------------------- asking ---

def question(issue):
    """(prompt, [candidate answers], scope) for one issue, or None to skip it."""
    kind, he, en = issue['kind'], issue['hebrew'], issue['english']
    if kind == 'he_multi_en':
        return (f'{he}\n\nis translated in {issue["n"]} rows as more than one thing.\n'
                f'Which English form is correct?', en.split(' | '), 'location')
    if kind == 'hebrew_in_english':
        return (f'{he}\n\nhas Hebrew left in its English cell:\n  {en}\n\n'
                f'What should the English be?', [], 'location')
    if kind == 'no_english':
        return (f'{he}\n\nhas an empty English cell in {issue["n"]} rows.\n'
                f'What should the English be?', [], 'location')
    if kind == 'dictionary_conflict':
        forms = [p.split('=', 1)[1] for p in en.split(' | ')]
        return (f'{he}\n\nthe dictionary and the data disagree.\n'
                f'Which form is correct?', forms, 'location')
    if kind == 'en_multi_he':
        return (f'These Hebrew names all map to "{en}":\n  '
                + '\n  '.join(he.split(' | '))
                + '\n\nIf they are the same place, keep it. If not, this needs '
                  'different English per name -- answer the he_multi_en questions '
                  'instead and skip this one.\nEnglish for all of them:',
                [en], 'location')
    if kind == 'segment_inconsistent':
        forms = [p.rsplit(' (', 1)[0] for p in en.split(' | ')]
        return (f'The segment "{he}" is translated inconsistently inside compound '
                f'names:\n  ' + '\n  '.join(en.split(' | '))
                + '\n\nWhich form should every compound use?', forms, 'segment')
    if kind == 'api_breaking':
        return (f'{issue["field"]} value "{he}" is missing from dictionaries.json,\n'
                f'so war23_api.py raises KeyError for pid {issue["pids"]}.\n\n'
                f'What is its translation?', [], 'dictionary')
    return None


def ask_terminal(prompt, candidates):
    print('\n' + '=' * 72)
    print(prompt)
    for i, c in enumerate(candidates, 1):
        print(f'   [{i}] {c}')
    print('   [s] skip    [q] quit')
    while True:
        a = input('> ').strip()
        if a == 'q':
            return None, True
        if a == 's' or a == '':
            return None, False
        if a.isdigit() and 1 <= int(a) <= len(candidates):
            return candidates[int(a) - 1], False
        if a:
            return a, False


def ask_dialog(prompt, candidates):
    import tkinter as tk
    box = {'value': None, 'quit': False}
    root = tk.Tk()
    root.title('place names')
    root.geometry('720x420')
    tk.Label(root, text=prompt, justify='left', anchor='w', wraplength=680,
             font=('TkDefaultFont', 11)).pack(fill='x', padx=14, pady=(14, 8))
    choice = tk.StringVar(value=candidates[0] if candidates else '')
    for c in candidates:
        tk.Radiobutton(root, text=c, variable=choice, value=c, anchor='w',
                       justify='left').pack(fill='x', padx=28)
    tk.Label(root, text='or type another form:', anchor='w').pack(fill='x', padx=14,
                                                                  pady=(12, 2))
    entry = tk.Entry(root, font=('TkDefaultFont', 11))
    entry.pack(fill='x', padx=14)
    entry.focus_set()

    def use(_=None):
        box['value'] = entry.get().strip() or choice.get().strip() or None
        root.destroy()

    def skip():
        root.destroy()

    def quit_all():
        box['quit'] = True
        root.destroy()

    bar = tk.Frame(root)
    bar.pack(side='bottom', fill='x', pady=12)
    tk.Button(bar, text='Use this', command=use, width=12).pack(side='left', padx=14)
    tk.Button(bar, text='Skip', command=skip, width=10).pack(side='left')
    tk.Button(bar, text='Quit', command=quit_all, width=10).pack(side='right', padx=14)
    root.bind('<Return>', use)
    root.bind('<Escape>', lambda _: skip())
    root.mainloop()
    return box['value'], box['quit']


def run_questions(terminal):
    with open(ISSUES, newline='', encoding='utf-8') as f:
        issues = [r for r in csv.DictReader(f, delimiter='\t') if r['kind'] in ASKABLE]
    done = load_decisions()
    todo = [i for i in issues if (i['kind'], i['hebrew']) not in done]
    print(f'{len(issues)} issues, {len(issues) - len(todo)} already answered, '
          f'{len(todo)} to go')
    ask = ask_terminal if terminal else ask_dialog
    for n, issue in enumerate(todo, 1):
        q = question(issue)
        if q is None:
            continue
        prompt, candidates, scope = q
        answer, stop = ask(f'[{n}/{len(todo)}]  {prompt}', candidates)
        if stop:
            print('stopped; rerun to continue where you left off')
            return
        if answer:
            record(issue['kind'], issue['hebrew'], answer, scope, issue['field'])
            print(f'  {issue["hebrew"]} -> {answer}')
    print('all questions answered; run --apply to see the changes')


# ------------------------------------------------------------------ applying ---

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


def quote(value):
    if any(c in value for c in ',"'):
        return '"%s"' % value.replace('"', '""')
    return value


def unquote(token):
    """The value inside a raw csv token. An empty token parses to no fields."""
    parsed = next(csv.reader([token]), [])
    return parsed[0] if parsed else ''


def apply(write):
    decisions = load_decisions()
    if not decisions:
        print(f'no decisions in {DECISIONS}; answer the questions first')
        return
    loc = {k[1]: v['choice'] for k, v in decisions.items() if v['scope'] == 'location'}
    segs = {k[1]: v['choice'] for k, v in decisions.items() if v['scope'] == 'segment'}
    dictionary = {k: v for k, v in decisions.items() if v['scope'] == 'dictionary'}

    with open(DB, newline='', encoding='utf-8') as f:
        raw = f.read()
    nl = '\r\n' if '\r\n' in raw else '\n'
    lines = raw.split(nl)
    header = split_top_level(lines[0])
    idx = [(header.index(he), header.index(en)) for he, en in PAIRS]

    changes = defaultdict(int)
    for n, line in enumerate(lines[1:], 1):
        if not line:
            continue
        tok = split_top_level(line)
        touched = False
        for i_he, i_en in idx:
            he, old = unquote(tok[i_he]), unquote(tok[i_en])
            if not he:
                continue
            new = loc.get(he, old)
            if segs:                       # rewrite segment by segment
                hp = [x.strip() for x in he.split(';')]
                ep = [x.strip() for x in new.split(';')]
                if len(hp) == len(ep):
                    ep = [segs.get(a, b) for a, b in zip(hp, ep)]
                    new = '; '.join(ep)
            if new != old:
                tok[i_en] = quote(new)
                changes[f'{old!r} -> {new!r}'] += 1
                touched = True
        if touched:
            lines[n] = ','.join(tok)

    print(f'{sum(changes.values())} cells would change in {os.path.basename(DB)}:')
    for k, v in sorted(changes.items(), key=lambda x: -x[1]):
        print(f'   {v:>4}  {k}')

    with open(DICTS, encoding='utf-8') as f:
        dicts = json.load(f)
    added = []
    for (kind, key), d in dictionary.items():
        sub = next((k for k, col in REQ.items() if col == d['field']), None)
        if sub is None:
            print(f'   ?? no dictionaries.json section for column {d["field"]!r}')
            continue
        added.append((sub, key, d['choice']))
    if added:
        print(f'\n{len(added)} entries would be added to dictionaries.json:')
        for sub, k, v in added:
            print(f'   {sub}[{k}] = {v}')

    if not write:
        print('\ndry run; add --write to apply')
        return
    with open(DB, 'w', newline='', encoding='utf-8') as f:
        f.write(nl.join(lines))
    print(f'wrote {DB}')
    if added:
        for sub, k, v in added:
            dicts.setdefault(sub, {})[k] = v
        with open(DICTS, 'w', encoding='utf-8') as f:
            json.dump(dicts, f, ensure_ascii=False, indent=2)
            f.write('\n')
        print(f'wrote {DICTS}')


REQ = {'genderEn': 'Gender', 'residenceHe': 'Residence', 'countryHe': 'Country',
       'roleHe': 'Role', 'statusEn': 'Status', 'frontEn': 'front',
       'causeOfDeathHe': 'סיבת המוות'}


if __name__ == '__main__':
    if '--apply' in sys.argv:
        apply('--write' in sys.argv)
    else:
        run_questions('--terminal' in sys.argv)
