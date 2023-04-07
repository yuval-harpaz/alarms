import requests
import pandas as pd
import numpy as np
import os



local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    with open('/home/innereye/alarms/oath.txt') as f:
        oath = f.readlines()[0][:-1]
else:
    oath = os.environ['OAuth']
# get_coordinates(city_name)
    
def get_coordinates(city_name):
    city_name = city_name + ', ישראל'
    geocoder_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={city_name}&key={oath}&language=iw'
    geocoding_result = requests.get(geocoder_url).json()
    if geocoding_result['results'] == []:
        lat = 0
        long = 0
    else:
        lat = geocoding_result['results'][0]['geometry']['location']['lat']
        long = geocoding_result['results'][0]['geometry']['location']['lng']
    return (lat, long)


missing = ['רחובות','חולון']
lt = []
lg = []
for miss in missing:
    lat, long = get_coordinates(miss)
    lt.append(lat)
    lg.append(long)
df = pd.DataFrame(missing, columns=['loc'])
df['lat'] = lt
df['long'] = lg
df.to_csv('test.csv', sep=',', index=False)



