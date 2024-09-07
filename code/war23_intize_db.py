import pandas as pd
import os
import numpy as np


local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    local = True

with open('data/oct7database.csv', "r+") as f:
    data = f.read()
    data.replace('.0,', ',')
    f.write(data)

