# import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
# from datetime import datetime
# import Levenshtein
# import re
import os
# import re
df = pd.read_csv('https://raw.githubusercontent.com/middle-east-buka/Gaza-Strip/refs/heads/main/idf/ground_offensive_idf_kia.csv')
db = pd.read_csv('data/oct7database.csv')
first = db['שם פרטי'].values
last =db['שם משפחה'].values
for ii in range(len(df)):
    name = df['Hebrew Name'][ii]
    row = np.where(np.array([x in name for x in first]) & np.array([x in name for x in last]))[0]
    if len(row) == 1:
        row = row[0]
        cause = df['Reason of Death'][ii]
        if
    else:
        print('missing '+name)


