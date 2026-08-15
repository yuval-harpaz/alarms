"""Strip leading/trailing spaces from every cell of a csv, in place.

Text edit, not a table rewrite: pandas turns the National Library ids into
floats (987012802875705171 -> 9.87e+17) and drops the quotes the csv puts round
them, so the file is patched field by field and every other byte is left as it
was found.
"""
import csv
import io
import sys


def split_fields(line):
    """The raw fields of one csv line, quotes and all."""
    fields, cur, quoted = [], '', False
    for char in line:
        if char == '"':
            quoted = not quoted
            cur += char
        elif char == ',' and not quoted:
            fields.append(cur)
            cur = ''
        else:
            cur += char
    fields.append(cur)
    return fields


def strip_field(field):
    """The field without spaces at either end, keeping the quotes it had."""
    field = field.strip()
    if len(field) > 1 and field.startswith('"') and field.endswith('"'):
        return '"' + field[1:-1].strip() + '"'
    return field


def strip_csv(path):
    with open(path, encoding='utf-8', newline='') as f:
        before = f.read()

    lines = before.split('\n')
    fixed = 0
    for row, line in enumerate(lines):
        fields = split_fields(line)
        stripped = [strip_field(field) for field in fields]
        if stripped != fields:
            fixed += sum(a != b for a, b in zip(fields, stripped))
            lines[row] = ','.join(stripped)
    after = '\n'.join(lines)

    # The file must still parse into the same table, minus the spaces.
    was = list(csv.reader(io.StringIO(before, newline='')))
    now = list(csv.reader(io.StringIO(after, newline='')))
    assert len(was) == len(now), 'row count changed'
    for old, new in zip(was, now):
        assert [cell.strip() for cell in old] == new, f'row changed: {old[0]}'

    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(after)
    print(f'{fixed} cells stripped in {path}')


if __name__ == '__main__':
    strip_csv(sys.argv[1] if len(sys.argv) > 1 else 'data/oct7database.csv')
