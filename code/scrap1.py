import pandas as pd
import os
import numpy as np
import sys

df = pd.read_csv('data/oct7database.csv')
notathome = [str(df['Residence'][x]) not in str(df['מקום האירוע'][x]) for x in range(len(df))]
noparty = np.array(df['Party'].isnull())
oct7 = df['Death date'].values == '2023-10-07'
citizen = df['Role'].values == 'אזרח'
res = np.unique(df['Residence'][~df['Residence'].isnull()])
nores = np.array([str(x).split(';')[0] not in res for x in df['מקום האירוע'].values])
nozikim = np.array(['זיקים' not in str(x) for x in df['מקום האירוע']])
candidates = oct7 & notathome & noparty & citizen & nores & nozikim
np.unique(df['מקום האירוע'][candidates])
select = df[candidates]
select.to_csv('~/Downloads/party_candidates.csv', index=False)
nomutzav = np.array(['מוצב' not in str(x) for x in df['מקום האירוע']])
migunit = np.array(['מיגונ' in str(x) for x in df['מקום האירוע']])

dfm = df[migunit & noparty]
dfm.to_csv('~/Downloads/migunit.csv', index=False)
