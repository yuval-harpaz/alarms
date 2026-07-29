"""
Download csv from
https://docs.google.com/spreadsheets/d/1-f2JeU3BjIuP8-wBPZm2mCR172HJQKCuNuGao4AnHKg/edit
to
NLI 4 oct7database - manual.csv
and find duplicates.
"""
import pandas as pd
import os
import numpy as np
import xlsxwriter


nli = pd.read_csv('~/Documents/NLI 4 oct7database - manual.csv', dtype={'הספריה הלאומית': str})

df = pd.DataFrame(columns=['nli_id', 'pid', 'name'])
ids = [s for s in nli['הספריה הלאומית'].unique() if len(str(s)) > 4]
for idstr in ids:
    rows = np.where(nli['הספריה הלאומית'] == idstr)[0]
    name = ''
    pid = ''
    for row in rows:
        name = name + nli.at[row, 'שם פרטי'] + ' ' + nli.at[row, 'שם משפחה'] + ' ' +  nli.at[row, 'Residence'] +';'
        pid = pid + str(nli.at[row, 'pid']) + ';'
    name = name[:-1]
    pid = pid[:-1]
    df.loc[len(df)] = [idstr, pid, name]

# Save as xlsx with nli_id as hyperlink

out_path = os.path.expanduser('~/Documents/NLIduplicates.xlsx')
workbook = xlsxwriter.Workbook(out_path)
worksheet = workbook.add_worksheet()
link_format = workbook.add_format({'color': 'blue', 'underline': 1})
# Header
for col, header in enumerate(df.columns):
    worksheet.write(0, col, header)
# Rows
for row_idx, row in df.iterrows():
    for col_idx, col_name in enumerate(df.columns):
        val = row[col_name]
        if col_name == 'nli_id' and isinstance(val, str) and len(val) > 4:
            url = f'https://www.nli.org.il/he/authorities/{val}'
            worksheet.write_url(row_idx + 1, col_idx, url, link_format, val)
        else:
            worksheet.write(row_idx + 1, col_idx, val)
workbook.close()
