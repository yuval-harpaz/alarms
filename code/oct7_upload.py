"""Send the coordinates and the secure map to oct7database.com.

    python code/oct7_upload.py --coordinates [--tsv FILE]
    python code/oct7_upload.py --coordinates --sheet  # from the deployed exec, no tsv
    python code/oct7_upload.py --map $WEBSITE/iron_swords_locations_private.html
    python code/oct7_upload.py --get-coordinates     # what the site holds now
    add --dry-run to any of them to see what would be sent, sending nothing
    add --verbose (-v) to print every request and response, key masked, to
    stderr: python code/oct7_upload.py --map FILE -v 2> support.log

Every endpoint takes the same key, $OCT7KEY.

Coordinates go to the site's Coordinates collection, one row per pid, 500 rows
to a request. They are the exact ones, from the sheet exported as tsv (TSV),
so the site holds what the private map draws, not the rings of the public one.

The map is too big for one record, so it goes up in chunks of CHUNK characters
under a fresh version id, and a commit naming that id and the chunk count tells
the site the upload is whole. Until the commit the site keeps showing the
previous version, so a failed upload leaves the old map in place: run it again.
"""
import csv
import json
import os
import sys
import uuid
from datetime import datetime, timezone

import requests

BASE = 'https://www.oct7database.com/_functions'
CHUNK = 100_000  # characters, not bytes: the site slices the string it gets
BATCH = 500
# the sheet, exported as tsv: the coordinates come from here
TSV = os.path.expanduser('~/Documents/oct7database - Data.tsv')
# --verbose: every request and response to stderr, for support
VERBOSE = False


def headers():
    key = os.environ.get('OCT7KEY')
    if not key:
        raise SystemExit('OCT7KEY is not set')
    return {'x-api-key': key}


def shorten(payload):
    """The payload as support needs to see it: the map chunk cut to its
    start, a coordinate batch to its first rows."""
    if isinstance(payload, list):
        return payload[:2] + ([f'... {len(payload)} rows in all']
                              if len(payload) > 2 else [])
    if isinstance(payload, dict) and 'content' in payload:
        content = payload['content']
        return dict(payload, content=f'{content[:80]}... ({len(content)} chars)')
    return payload


def log(request, r):
    """Both sides of one call, with the key masked, ready to paste to
    support."""
    print(f'--- {datetime.now(timezone.utc).isoformat(timespec="seconds")}',
          file=sys.stderr)
    print(f'{request.method} {request.url}', file=sys.stderr)
    for k, v in request.headers.items():
        print(f'{k}: {"***" if k.lower() == "x-api-key" else v}',
              file=sys.stderr)
    print(json.dumps(shorten(json.loads(request.body or 'null')),
                     ensure_ascii=False, indent=1), file=sys.stderr)
    print(f'\n{r.status_code} {r.reason}  ({r.elapsed.total_seconds():.2f}s)',
          file=sys.stderr)
    for k, v in r.headers.items():
        print(f'{k}: {v}', file=sys.stderr)
    print(r.text[:2000], file=sys.stderr)


def post(endpoint, payload=None, timeout=60):
    r = requests.post(f'{BASE}/{endpoint}', json=payload, headers=headers(),
                      timeout=timeout)
    if VERBOSE:
        log(r.request, r)
    if not r.ok:
        raise SystemExit(f'{endpoint}: {r.status_code} {r.text[:500]}')
    return r.json() if r.content else None


def point(text):
    """(lat, lng) out of 'lat, lng', or None. The sheet leaves a zero-width
    space after some of them."""
    text = text.replace('\u200b', '').strip()
    if not text:
        return None
    lat, lng = (float(x) for x in text.split(','))
    return lat, lng


def coordinate_rows(path=TSV):
    """[{pid, eventLat, eventLng, deathLat, deathLng}] for every pid with a
    coordinate. deathLat/deathLng are None when the sheet has no death
    coordinate, meaning the person died where the event was."""
    rows = []
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f, delimiter='\t'):
            event = point(row['event_coordinates'])
            death = point(row['death_coordinates'])
            if not event and not death:
                continue
            rows.append({'pid': int(row['pid']),
                         'eventLat': event[0] if event else None,
                         'eventLng': event[1] if event else None,
                         'deathLat': death[0] if death else None,
                         'deathLng': death[1] if death else None})
    return rows


def sheet_rows(data):
    """The same rows as coordinate_rows(), out of the sheet deployment
    (iron_swords_data.fetch()), whose points are [lng, lat]."""
    rows = []
    for feature in data['features']:
        geometry = feature.get('geometry')
        event = geometry['coordinates'][:2] if geometry else None
        death = feature['properties'].get('deathcoo', '')
        death = death if isinstance(death, list) and len(death) == 2 else None
        if not event and not death:
            continue
        rows.append({'pid': int(feature['properties']['pid']),
                     'eventLat': event[1] if event else None,
                     'eventLng': event[0] if event else None,
                     'deathLat': death[1] if death else None,
                     'deathLng': death[0] if death else None})
    return rows


def upload_coordinates(rows, dry_run):
    for i in range(0, len(rows), BATCH):
        if not dry_run:
            post('addCoordinates', rows[i:i + BATCH])
        print(f'coordinates {i + 1}-{min(i + BATCH, len(rows))} of {len(rows)}')


def upload_secure_map(path, dry_run):
    # the site keeps one map per language; the file name says which this is
    lang = 'en' if path.endswith('_en.html') else 'he'
    with open(path, encoding='utf-8') as f:
        html = f.read()
    version = uuid.uuid4().hex
    chunks = [html[i:i + CHUNK] for i in range(0, len(html), CHUNK)]
    for i, content in enumerate(chunks):
        if not dry_run:
            post('uploadSecureMapChunk',
                 {'lang': lang, 'version': version, 'chunkIndex': i,
                  'content': content})
    if not dry_run:
        post('commitSecureMap', {'lang': lang, 'version': version,
                                 'totalChunks': len(chunks)}, timeout=120)
    print(f'{os.path.basename(path)} ({lang}): {len(html)} characters in {len(chunks)} '
          f'chunks, version {version}' + (' (dry run)' if dry_run else ''))


def main():
    global VERBOSE
    args = sys.argv[1:]
    dry_run = '--dry-run' in args
    VERBOSE = '--verbose' in args or '-v' in args
    if '--get-coordinates' in args:
        records = post('getCoordinates', timeout=120)['records']
        json.dump(records, sys.stdout, ensure_ascii=False, indent=1)
        print(f'\n{len(records)} records', file=sys.stderr)
    elif '--coordinates' in args and '--sheet' in args:
        from iron_swords_data import fetch
        upload_coordinates(sheet_rows(fetch()), dry_run)
    elif '--coordinates' in args:
        tsv = args[args.index('--tsv') + 1] if '--tsv' in args else TSV
        upload_coordinates(coordinate_rows(tsv), dry_run)
    elif '--map' in args:
        upload_secure_map(args[args.index('--map') + 1], dry_run)
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
