"""Export data to html map."""
import pandas as pd
import numpy as np
import geojson
from urllib import request
import json
import os
import sys
sys.path.append('/home/innereye/alarms/code/')
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('use: python map_export_foreign.py COMMENT')
    else:
        from map_export_loc import export_json, json2map
        comment = sys.argv[1]
        mapname, coos = export_json(language='Eng')
        center = np.median(coos, 0)
        json2map(mapname, center, comment)

# ##
# os.chdir('/home/innereye/alarms')
# # with open('.txt', 'r') as f:
# #     address = f.read().split('\n')[6]
# # with request.urlopen(address) as url:
# #     data = json.load(url)
# # pid = np.array([x['properties']['pid'] for x in data['features']])
# db = pd.read_csv('data/oct7database.csv')

# mapname, coos = export_json(language='Eng')
# center = np.mean(coos, 0)

# json2map()
