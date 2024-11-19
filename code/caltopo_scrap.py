# import re
# from matplotlib import colors
# import folium
# import pandas as pd
# import numpy as np
import os
from caltopo_python import CaltopoSession


local = '/home/innereye/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True
cts = CaltopoSession('caltopo.com', 'AH0621E',
                     configpath='caltopo.ini',
                     account='yuvharpaz@gmail.com')
# tmp = cts.getMapList()
# data = cts.getFeature('Marker', 'data')
myMarker=cts.getFeature('Marker','אביב ברעם')
