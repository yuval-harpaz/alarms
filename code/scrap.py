import pandas as pd
import numpy as np
import os
os.chdir('/home/innereye/alarms/')
db = pd.read_csv('data/oct7database.csv', dtype={'הספריה הלאומית': str})
loc = pd.read_csv('~/Documents/oct7database_location_class.csv')
for ii in range(len(loc)):
    db.at[ii, 'Event location class'] = loc['Event location class'][ii]
    db.at[ii, 'Death location class'] = loc['Death location class'][ii]
db.to_csv('data/oct7database.csv', index=False)