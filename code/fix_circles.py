"""Collect a circle centre for each place that has no coordinate of its own.

Walks the queue from code/coverage_report.py, biggest place first, and asks for
one "lat, lon" per place. Every answer is appended to data/coord_circle.csv the
moment it is given, so the job can be spread over several sessions -- places
already in the file are never asked again.

    python code/coverage_report.py     # build the queue
    python code/fix_circles.py         # fill it in (dialog)
    python code/fix_circles.py --terminal
    python code/fix_circles.py --list  # what is done and what is left

Radius starts at 500 m for every circle. It is a per-row column, so tuning one
place later is an edit to the csv, not a code change.
"""
import csv
import os
import re
import sys

from hebrew import rtl
from normalize_semicolons import normalize

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE = os.path.join(ROOT, 'data', 'location_coverage.tsv')
CIRCLES = os.path.join(ROOT, 'data', 'coord_circle.csv')

FIELDS = ['name_he', 'name_en', 'lat', 'lon', 'radius_m', 'n_people', 'source', 'filled']
DEFAULT_RADIUS = 500


def parse_coo(text):
    text = re.sub(r'[^0-9.,\- ]', '', text or '').strip()
    parts = [p for p in re.split(r'[ ,]+', text) if p]
    if len(parts) != 2:
        return None
    try:
        lat, lon = float(parts[0]), float(parts[1])
    except ValueError:
        return None
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None
    if not (29 < lat < 34 and 33 < lon < 37):
        print(f'   note: {lat}, {lon} is outside Israel and its neighbours')
    return lat, lon


def load_circles():
    """Keyed on the normalised name, so 'א;ב' and 'א; ב' count as one place."""
    if not os.path.exists(CIRCLES):
        return {}
    with open(CIRCLES, newline='', encoding='utf-8') as f:
        return {normalize(r['name_he']): r for r in csv.DictReader(f)}


def append(row):
    new = not os.path.exists(CIRCLES)
    with open(CIRCLES, 'a', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)


def load_queue():
    with open(QUEUE, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def ask_terminal(place, n, total):
    print('\n' + '=' * 72)
    print(f'[{n}/{total}]  {place["name_he"]}')
    print(f'          {place["name_en"]}')
    print(f'          {place["n_people"]} people, {place["kind"]} location')
    print('   paste "lat, lon"    [s] skip    [q] quit')
    while True:
        a = input('> ').strip()
        if a == 'q':
            return None, True
        if a in ('s', ''):
            return None, False
        coo = parse_coo(a)
        if coo:
            return coo, False
        print('   could not read that as a coordinate pair')


def ask_dialog(place, n, total):
    import tkinter as tk
    box = {'value': None, 'quit': False}
    root = tk.Tk()
    root.title(f'circle {n}/{total}')
    root.geometry('640x300')
    tk.Label(root, text=rtl(place['name_he']), font=('TkDefaultFont', 16),
             anchor='e').pack(fill='x', padx=16, pady=(18, 2))
    tk.Label(root, text=place['name_en'], font=('TkDefaultFont', 12),
             anchor='w', fg='#555').pack(fill='x', padx=16)
    tk.Label(root, text=f'{place["n_people"]} people   ({place["kind"]} location)',
             anchor='w', fg='#777').pack(fill='x', padx=16, pady=(2, 14))
    tk.Label(root, text='centre of the circle, as "lat, lon":',
             anchor='w').pack(fill='x', padx=16)
    entry = tk.Entry(root, font=('TkDefaultFont', 13))
    entry.pack(fill='x', padx=16, pady=4)
    entry.focus_set()
    warn = tk.Label(root, text='', fg='#a00', anchor='w')
    warn.pack(fill='x', padx=16)

    def use(_=None):
        coo = parse_coo(entry.get())
        if not coo:
            warn.config(text='could not read that as a coordinate pair')
            return
        box['value'] = coo
        root.destroy()

    def skip():
        root.destroy()

    def quit_all():
        box['quit'] = True
        root.destroy()

    bar = tk.Frame(root)
    bar.pack(side='bottom', fill='x', pady=14)
    tk.Button(bar, text='Save', command=use, width=12).pack(side='left', padx=16)
    tk.Button(bar, text='Skip', command=skip, width=10).pack(side='left')
    tk.Button(bar, text='Quit', command=quit_all, width=10).pack(side='right', padx=16)
    root.bind('<Return>', use)
    root.bind('<Escape>', lambda _: skip())
    root.mainloop()
    return box['value'], box['quit']


def main():
    if not os.path.exists(QUEUE):
        print(f'no queue at {QUEUE}; run code/coverage_report.py first')
        return
    queue, done = load_queue(), load_circles()
    todo = [p for p in queue if normalize(p['name_he']) not in done]
    if '--list' in sys.argv:
        print(f'{len(done)} places have a circle, {len(todo)} still to do')
        for p in todo:
            print(f'  {p["n_people"]:>4}  {p["name_he"]}')
        return
    print(f'{len(queue)} places in the queue, {len(done)} already done, '
          f'{len(todo)} to go')
    ask = ask_terminal if '--terminal' in sys.argv else ask_dialog
    for n, place in enumerate(todo, 1):
        coo, stop = ask(place, n, len(todo))
        if stop:
            break
        if coo is None:
            continue
        append({'name_he': place['name_he'], 'name_en': place['name_en'],
                'lat': f'{coo[0]:.6f}', 'lon': f'{coo[1]:.6f}',
                'radius_m': DEFAULT_RADIUS, 'n_people': place['n_people'],
                'source': 'manual', 'filled': ''})
        print(f'  {place["name_he"]} -> {coo[0]:.6f}, {coo[1]:.6f}')
    left = len(load_queue()) - len(load_circles())
    print(f'\n{len(load_circles())} circles saved, {left} places still without one')


if __name__ == '__main__':
    main()
