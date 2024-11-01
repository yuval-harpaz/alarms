"""Import cause of death from Buka."""
import pandas as pd
import numpy as np
df = pd.read_csv('https://raw.githubusercontent.com/middle-east-buka/Gaza-Strip/refs/heads/main/idf/ground_offensive_idf_kia.csv')
db = pd.read_csv('data/oct7database.csv')
first = db['שם פרטי'].values
last = db['שם משפחה'].values
for ii in range(len(df)):
    name = df['Hebrew Name'][ii]
    row = np.where(np.array([x in name for x in first])
                   & np.array([x in name for x in last]))[0]
    if len(row) == 1:
        row = row[0]
        cause = df['Reason of Death'][ii]
        if cause != 'No Details':
            if cause == 'IED':
                cause = 'מטען'
            elif cause == 'Mortar':
                cause = 'פצמ"ר'
            elif cause == 'RPG/ATGM':
                cause = 'נ.ט.'
            elif cause == 'Small Arms':
                cause = 'ירי'
            elif cause == 'Sniper':
                cause = 'צלף'
            current = str(db['סיבת המוות'][row])
            if current == 'nan':
                db.at[row, 'סיבת המוות'] = cause
            else:
                if current != cause:
                    print(f"{name} is currently {current}, not {cause}")
    else:
        print('missing '+name)
db.to_csv('data/oct7database.csv', index=False)
