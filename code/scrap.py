import pandas as pd
import numpy as np
import os


uptodate = pd.read_csv('~/Documents/NLI 4 oct7database - manual.csv', 
                       dtype={'NLI': str, 'suggestion': str})
db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})
# check pid are the same
min_len = min([len(db), len(uptodate)])
if np.mean(db['pid'].values[:min_len] == uptodate['pid'].values[:min_len]) != 1:
    first_unequal = np.where(db['pid'].values[:min_len] != uptodate['pid'].values[:min_len])[0][0]
    print('pid issues, first one for pid ' + str(db['pid'].values[first_unequal]) + ' at index ')
    raise ValueError('pid mismatch between oct7database.csv and NLI 4 oct7database - manual.csv')

for row, pid in enumerate(uptodate['pid'].values[:min_len]):
    # row = np.where(db['pid'].values == pid)[0][0]
    nli_value = str(uptodate['suggestion'].values[row])
    db_value = str(db['הספריה הלאומית'].values[row])
    harpaz_id = uptodate['harpaz_id'][row]
    if pid == harpaz_id and nli_value[0] == '9' and db_value[:3] == 'nan':
        print(f"pid {pid} has harpaz_id {harpaz_id} and NLI value {nli_value} but no NLI ID in DB")
        db.at[row, 'הספריה הלאומית'] = nli_value
db.to_csv('data/oct7database.csv', index=False)
