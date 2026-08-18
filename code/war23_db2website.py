"""
push oct7database.csv to the website. the website data is read with the API (war23_api.py),
so nothing has to be downloaded manually from wix CMS or from oct7database.com/table.
    python code/war23_db2website.py        send the missing and the changed records
    python code/war23_db2website.py dry    only print what would be sent
    python code/war23_db2website.py clear  also empty fields which have data on the website but not in the csv
"""
import sys
from war23_api import db, website_pid, get_all_records, missing_pid, extra_pid, changed_pid, pid2record, send_records

if __name__ == '__main__':
    args = [a.lower() for a in sys.argv[1:]]
    dry = len([a for a in args if a[0] in ['d', 'n']]) > 0
    clear = len([a for a in args if a[0] == 'c']) > 0
    pids = website_pid()
    print(f'{len(pids)} records on the website, {len(db)} in oct7database.csv')
    extra = extra_pid(pids)
    if len(extra) > 0:
        print(f'{len(extra)} pid on the website but not in the csv, leaving them alone: {extra}')
    missing = missing_pid(pids)
    if len(missing) > 0:
        print('n missing pid:', len(missing))
        for pid in missing:
            record = pid2record(pid)
            print(f"new {pid}: {record.get('firstNameHe')} {record.get('lastNameHe')}")
            if not dry:
                send_records(record)
        if not dry:
            pids = website_pid()  # to compare the records which were just sent
    records, not_found = get_all_records(pids)
    if len(not_found) > 0:
        print(f'getRecords did not return {not_found}')
    changed = changed_pid(verbose=dry, records=records, clear=clear)
    if len(changed) > 0:
        print('n changed pid:', len(changed))
        for pid in changed.keys():
            print(f"{pid}: " + ', '.join([f for f in changed[pid].keys() if f != 'pid']))
            if not dry:
                send_records(changed[pid])
    if dry:
        print('dry run, nothing was sent. run with no arguments to push')
    else:
        print('done, run war23_db_tests.py a to check')
