import pandas as pd
import os
import numpy as np
from geopy.distance import geodesic
import sys
sys.path.append('code')
from map_deaths_name_search import group_locs
local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    local = True

# map = pd.read_csv('data/oct_7_9.csv')
# db = pd.read_excel('~/Documents/oct7database.xlsx', 'Data')
# cref = pd.read_csv('data/crossref.csv')
df = pd.read_csv('~/Documents/locations.csv')
##
subloc = {'232 Blocked Road': [31.399963, 34.474210],
          'Alumim Bomb Shelter (West)': [31.450412, 34.516401],
          "Be'eri Bomb Shelter": [31.428803, 34.496924],
          'Gama Junction Bomb Shelter (North)': [31.381336, 34.447480],
          'Gama Junction Bomb Shelter (West)': [31.380127, 34.447162],
          "Hostage Situation in Be'eri": [31.42804511392142, 34.49307314081499],
          'Main Stage': [31.397771, 34.469951],
          'Nahal Grar Bridge': [31.400212, 34.474301],
          'Nova Ambulance': [31.397351, 34.469556],
          'Nova Bar': [31.398900, 34.470031],
          'Nova Entrance Bomb Shelter': [31.400190, 34.473742],
          "Re'im Bomb Shelter (East)": [31.389740, 34.459447],
          "Re'im Bomb Shelter (West)": [31.3897815832395, 34.45805954741456],
          'Yellow Containers': [31.398628, 34.470782]}
sublocheb = {'אשקלון; בי"ח ברזילי': [31.6632444309682, 34.5578359719349],
             'בארי; ארוע בני ערובה': [31.423137676630546, 34.493090778786325],
             'יד מרדכי - נתיב העשרה; קבוצת ריצה': [31.57576149845013, 34.55275119619444],
             'כביש רעים – אורים (צפון)': [31.3830878311482, 34.4552414506731],
             'מטעים של בארי (מגורי עובדים)': [31.4054968725694, 34.4537661162609],
             'מיגונית בצומת גמה (דרום)': [31.380127,34.447162],
             'מיגונית בצומת גמה (מערב)': [31.380127, 34.447162],
             'מיגונית בצומת גמה (צפון)': [31.381336, 34.447480],
             'מיגונית בצומת רעים (מזרח)': [31.389740, 34.459447],
             'מיגונית בצומת רעים (מערב)': [31.389781, 34.458059],
             'סמוך למיגונית בצומת גמה (דרום)': [31.380216626100477, 34.44733662392307],
             'סמוך למיגונית בצומת גמה (צפון)': [31.381307046724753, 34.44754169695219],
             'עזה; ביה"ח שיפא': [31.399963, 34.474210],
             'עזה; מבנה סמוך לביה"ח שיפא': [31.399963, 34.474210],
             'עזה; מסגד סמוך לביה"ח שיפא': [31.399963, 34.474210],
             'פסטיבל נובה; אמבולנס': [31.397351, 34.469556],
             'פסטיבל נובה; במה מרכזית': [31.397771, 34.469951],
             'פסטיבל נובה; בר': [31.398900, 34.470031],
             'פסטיבל נובה; גשר נחל גרר': [31.400212, 34.474301],
             'פסטיבל נובה; חסימה בכביש 232': [31.399963, 34.474210],
             'פסטיבל נובה; מכולות צהובות': [31.398628, 34.470782],
             'שדרות; אוטובוס הגמלאים': [31.52677040015094, 34.60108324482743],
             'שדרות; תחנת משטרה': [31.52249812718559, 34.59202432204493]}
db = pd.read_excel('~/Documents/oct7database.xlsx', 'Data')
##
pids = df['pid'].values
subs = np.where(df['event loc'].str.contains(';'))[0]
for ii in subs:
    loc = df['event loc'][ii]
    if type(db['event_coordinates'][ii]) != str and loc in sublocheb.keys():
        # print(str(sublocheb[loc]))
        db.at[ii, 'event_coordinates'] = str(sublocheb[loc])[1: -1]
db.to_csv('~/Documents/subloc.csv', index=False)
