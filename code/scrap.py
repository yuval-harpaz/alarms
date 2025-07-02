import pandas as pd
import numpy as np
import os
os.chdir('/home/innereye/alarms/')
db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})
if db['הספריה הלאומית'][0][-4:] == 'e+17':
    print('Bad NLI IDs')
else:
    print('passed')