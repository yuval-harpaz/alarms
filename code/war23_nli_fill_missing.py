"""One time update: fill missing NLI IDs in oct7database.csv from the reviewed NLI 710 issues list
(~/Documents/אוג' 2026 רשימת זהויות 710 של הספרייה - אי התאמה.tsv).
Only rows with comment "ID in NLI not found in oct7database" and a pid in the last column are used.
The NLI ID is taken from the link (the nli_id column is in scientific notation).
oct7database.csv is edited as text, only the 'הספריה הלאומית' field of the updated lines is changed.
An existing NLI ID is never overwritten, except pids in overwrite (reviewed in ~/Documents/nli710_double_ids.xlsx).
Failed updates are printed and saved to ~/Documents/nli710_failed_updates.tsv.
Set dry_run = False to actually save.
"""
import os
import re
import csv
import Levenshtein

dry_run = False
overwrite = ['38', '687', '797', '1317']  # replace our NLI ID with theirs
skip = ['2548']  # two NLI IDs, don't fill
name_confirmed = ['1678', '1724', '239']  # name mismatch confirmed manually

for home in ['innereye', 'yuval']:
    if os.path.isdir('/home/'+home+'/alarms/'):
        os.chdir('/home/'+home+'/alarms/')
        break

issues_path = os.path.expanduser("~/Documents/אוג' 2026 רשימת זהויות 710 של הספרייה - אי התאמה.tsv")
failed_path = os.path.expanduser('~/Documents/nli710_failed_updates.tsv')
db_path = 'data/oct7database.csv'
nli_col = 'הספריה הלאומית'


def split_raw(line):
    """split a csv line on commas outside quotes, keeping each field's raw text (quotes included)"""
    fields, start, in_quotes = [], 0, False
    for i, ch in enumerate(line):
        if ch == '"':
            in_quotes = not in_quotes
        elif ch == ',' and not in_quotes:
            fields.append(line[start:i])
            start = i + 1
    fields.append(line[start:])
    return fields


def normalize(name):
    name = name.replace('׳', "'").replace('״', '"').replace('`', "'").replace('-', ' ')
    name = re.sub(r'[֑-ׇ]', '', name)  # remove niqqud
    return ' '.join(name.split())


def name_check(first, last, rec):
    """returns (ok, exact). ok when last name and first word of first name are each within
    Levenshtein distance 2 of the db names (spaces and geresh ignored)"""
    eng = bool(re.search('[A-Za-z]', first + last))
    cols = ['first name', 'middle name', 'nickname', 'last name'] if eng else ['שם פרטי', 'שם נוסף', 'כינוי', 'שם משפחה']
    db_first = [normalize(rec[c]) for c in cols[:3] if rec[c].strip()]
    db_last = normalize(rec[cols[3]])
    first, last = normalize(first), normalize(last)
    if not first or not last:
        return False, False

    def squash(s):
        return s.replace(' ', '').replace("'", '').lower()
    # first word of the NLI first name vs each db first-name word, and vs whole db first names
    candidates = [w for n in db_first for w in n.split()] + db_first
    d_first = min([Levenshtein.distance(squash(first.split()[0]), squash(c)) for c in candidates] + [99])
    d_last = Levenshtein.distance(squash(last), squash(db_last))
    exact = normalize(rec[cols[0]]) == first and db_last == last
    return d_first <= 2 and d_last <= 2, exact


# read the database as text
with open(db_path, encoding='utf-8', newline='') as f:
    lines = f.readlines()
header = next(csv.reader([lines[0]]))
header[0] = header[0].lstrip('﻿')
i_nli = header.index(nli_col)
pid_line = {}  # pid -> line index
records = {}  # pid -> dict of parsed fields
existing_ids = {}  # nli id -> pid
for il in range(1, len(lines)):
    if not lines[il].strip():
        continue
    parsed = next(csv.reader([lines[il]]))
    if len(parsed) != len(header) or len(split_raw(lines[il].rstrip('\r\n'))) != len(header):
        raise Exception('unexpected number of fields in line ' + str(il + 1) + ' of ' + db_path)
    rec = dict(zip(header, parsed))
    pid_line[rec['pid']] = il
    records[rec['pid']] = rec
    if rec[nli_col].strip():
        existing_ids[rec[nli_col].strip()] = rec['pid']

# read the reviewed issues list
with open(issues_path, encoding='utf-8', newline='') as f:
    issues = list(csv.DictReader(f, delimiter='\t'))

failed = []
updated = []
for row in issues:
    if not row['comment'].startswith('ID in NLI not found in oct7database'):
        continue
    pid = (row['pid'] or '').strip()
    if not pid:
        continue
    nli_name = (row['שם פרטי'] + ' ' + row['שם משפחה']).strip()
    match = re.search(r'authorities/(\d+)', row['link'])
    if not match:
        failed.append([pid, '', nli_name, '', 'no NLI ID in link'])
        continue
    nli_id = match.group(1)
    if pid not in records:
        failed.append([pid, nli_id, nli_name, '', 'pid not found in oct7database'])
        continue
    rec = records[pid]
    db_full = ' '.join([rec[c] for c in ['שם פרטי', 'שם נוסף', 'שם משפחה', 'כינוי'] if rec[c].strip()])
    if pid in skip:
        failed.append([pid, nli_id, nli_name, db_full, 'skipped, two NLI IDs'])
        continue
    if rec[nli_col].strip():
        if pid in overwrite:
            print('overwriting pid ' + pid + ' NLI ID ' + rec[nli_col].strip())
            existing_ids.pop(rec[nli_col].strip(), None)
        else:
            failed.append([pid, nli_id, nli_name, db_full, 'already has NLI ID ' + rec[nli_col].strip()])
            continue
    if nli_id in existing_ids:
        failed.append([pid, nli_id, nli_name, db_full, 'NLI ID already used by pid ' + existing_ids[nli_id]])
        continue
    ok, exact = name_check(row['שם פרטי'], row['שם משפחה'], rec)
    if pid in name_confirmed:
        ok, exact = True, True
    if not ok:
        failed.append([pid, nli_id, nli_name, db_full, 'name mismatch'])
        continue
    if not exact:
        print('ALERT fuzzy name match, updating anyway: pid ' + pid + ', NLI: ' + nli_name + ', db: ' + db_full)
    il = pid_line[pid]
    eol = lines[il][len(lines[il].rstrip('\r\n')):]
    fields = split_raw(lines[il].rstrip('\r\n'))
    fields[i_nli] = '"' + nli_id + '"'
    lines[il] = ','.join(fields) + eol
    rec[nli_col] = nli_id
    existing_ids[nli_id] = pid
    updated.append(pid)
    print('updated pid ' + pid + ' (' + db_full + ') with NLI ID ' + nli_id)

print('\n' + str(len(updated)) + ' updated, ' + str(len(failed)) + ' failed:')
for fl in failed:
    print('FAILED pid ' + fl[0] + ', NLI ' + fl[1] + ' (' + fl[2] + '), db: ' + fl[3] + ' -> ' + fl[4])

if dry_run:
    print('\ndry run, nothing saved')
else:
    with open(db_path, 'w', encoding='utf-8', newline='') as f:
        f.writelines(lines)
    with open(failed_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['pid', 'nli_id', 'NLI name', 'oct7database name', 'reason'])
        writer.writerows(failed)
    print('\nsaved ' + db_path + ' and ' + failed_path)
