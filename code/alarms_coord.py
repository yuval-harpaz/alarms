import requests
import pandas as pd
import numpy as np
import os


def update_coord():
    local = '/home/innereye/alarms/'
    if os.path.isdir(local):
        os.chdir(local)
        with open('/home/innereye/alarms/oath.txt') as f:
            oauth = f.readlines()[0][:-1]
    else:
        oauth = os.environ['OAuth']

    def get_coordinates(city_name):
        city_name = city_name + ', ישראל'
        geocoder_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={city_name}&key={oauth}&language=iw'
        geocoding_result = requests.get(geocoder_url).json()
        if geocoding_result['results'] == []:
            lat = 0
            long = 0
        else:
            lat = geocoding_result['results'][0]['geometry']['location']['lat']
            long = geocoding_result['results'][0]['geometry']['location']['lng']
        return lat, long
    
    coo = pd.read_csv('data/coord.csv')
    prev = pd.read_csv('data/alarms.csv')
    missing = []
    for cit in np.unique(prev['cities']):
        if cit not in coo['loc'].values:
            missing.append(cit)
    # lat_long = [[], []]
    if len(missing) > 0:
        for miss in missing:
            lat, long = get_coordinates(miss)
            coo.loc[len(coo)+1] = [miss, lat, long]
        coo.sort_values('loc', inplace=True)
        coo.to_csv('data/coord.csv', sep=',', index=False)


