"""
push oct7database.csv to the website. the website data is read with the API (war23_api.py),
so nothing has to be downloaded manually from wix CMS or from oct7database.com/table.
a field which has a value on the website and no value in the csv is deleted, by sending an empty string.
    python code/war23_db2website.py         send the missing records and the changed fields
    python code/war23_db2website.py dry     only print what would be sent
    python code/war23_db2website.py keep    do not delete, only add and change
    python code/war23_db2website.py 1636    work on these pids only, good for trying one record first
"""
import sys
from war23_api import (db, csv_diff, website_pid, get_all_records, missing_pid, extra_pid, changed_pid,
                        pid2record, send_records)

if __name__ == '__main__':
    args = [a.lower() for a in sys.argv[1:]]
    dry = len([a for a in args if a[0] in ['d', 'n']]) > 0
    keep = len([a for a in args if a[0] == 'k']) > 0
    only = [int(a) for a in args if a.isdigit()]
    not_pushed = csv_diff()
    if len(not_pushed) > 0:  # the csv being sent is the one on github, not the local file
        print(f'{len(not_pushed)} pid differ between the local oct7database.csv and the one on github:')
        print(str(not_pushed).replace("'", ''))
        print('commit and push them first, or they will not reach the website')
        if not dry:
            sys.exit(1)
    all_pids = website_pid()
    print(f'{len(all_pids)} records on the website, {len(db)} in oct7database.csv')
    extra = extra_pid(all_pids)
    if len(extra) > 0:
        print(f'{len(extra)} pid on the website but not in the csv, leaving them alone: {extra}')
    missing = missing_pid(all_pids)
    if len(only) > 0:
        missing = [p for p in missing if p in only]
    if len(missing) > 0:
        print('n missing pid:', len(missing))
        for pid in missing:
            record = pid2record(pid)
            print(f"new {pid}: {record.get('firstNameHe')} {record.get('lastNameHe')}")
            if not dry:
                send_records(record)
        if not dry:
            all_pids = website_pid()  # to compare the records which were just sent
    pids = all_pids if len(only) == 0 else [p for p in all_pids if p in only]
    records, not_found = get_all_records(pids)
    if len(not_found) > 0:
        print(f'getRecords did not return {not_found}')
    changed = changed_pid(verbose=dry, records=records, clear=not keep)
    if len(changed) > 0:
        print('n changed pid:', len(changed))
        for pid in changed.keys():
            fields = [f for f in changed[pid].keys() if f != 'pid']
            print(f'{pid}: ' + ', '.join([f + [' (delete)' if changed[pid][f] in ['', None] else ''][0] for f in fields]))
            if not dry:
                send_records(changed[pid])
    if dry:
        print('dry run, nothing was sent. run with no arguments to push')
    else:
        print('done, run war23_db_tests.py a to check')
