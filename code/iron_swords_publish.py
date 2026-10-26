"""Publish the iron_swords map in one go:

    python code/iron_swords_publish.py [--verbose] [--dry-run] [--all]

1. download the coordinates from the deployed sheet exec (line 7 of .txt)
2. upload to the Coordinates collection on oct7database.com only those that
   differ from what the site holds (--all: every one of them)
3. git pull misc
4. build the public and private maps into $WEBSITE from that same download,
   so the maps draw what was just uploaded
5. commit and push the two public maps in misc
6. upload the two private maps to oct7database.com

--verbose is passed to the build (every build note). --dry-run downloads and
builds, but uploads, commits and pushes nothing.
The build stops when data/oct7database.csv was not pushed; see
iron_swords_map_update.md.
"""
import os
import subprocess
import sys

import iron_swords_data
import oct7_upload

PUBLIC = ['iron_swords_locations.html', 'iron_swords_locations_en.html']
PRIVATE = ['iron_swords_locations_private.html', 'iron_swords_locations_private_en.html']


def git(*args):
    print('git ' + ' '.join(args))
    return subprocess.run(['git', '-C', website] + list(args), check=True,
                          capture_output=True, text=True).stdout


args = sys.argv[1:]
dry_run = '--dry-run' in args
verbose = '--verbose' in args or '-v' in args
website = os.environ.get('WEBSITE')
if not website:
    raise SystemExit('WEBSITE is not set')

# 1-2. coordinates, sheet -> wix
data = iron_swords_data.fetch()
rows = oct7_upload.sheet_rows(data)
print(f'{len(rows)} pids with coordinates in the sheet')
oct7_upload.upload_coordinates(rows if '--all' in args else oct7_upload.changed_rows(rows),
                               dry_run)

# 3. pull before building, so the new files don't clash with remote changes
if not dry_run:
    print(git('pull'))

# 4. build from the download above, not from a second call to the exec
iron_swords_data.fetch = lambda: data
sys.argv = sys.argv[:1] + (['--verbose'] if verbose else [])
import iron_swords_map  # noqa: E402, needs $WEBSITE at import
iron_swords_map.main()

# 5. public maps -> misc
if dry_run:
    print(git('status', '--short', *PUBLIC) or 'public maps unchanged')
else:
    git('add', *PUBLIC)
    if git('diff', '--cached', '--name-only', *PUBLIC).strip():
        git('commit', '-m', 'iron swords map', '--', *PUBLIC)
        print(git('push'))
    else:
        print('public maps unchanged, nothing to push')

# 6. private maps -> wix
for name in PRIVATE:
    oct7_upload.upload_secure_map(os.path.join(website, name), dry_run)
print('dry run, nothing uploaded or pushed' if dry_run else 'done')
