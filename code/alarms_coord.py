import requests
import pandas as pd
import numpy as np
import os


def update_coord(latest=None, coord_file='data/coord.csv'):
    local = '/home/innereye/alarms/'
    if os.path.isdir(local):
        os.chdir(local)
        with open('/home/innereye/alarms/oath.txt') as f:
            oauth = f.readlines()[0][:-1]
        with open('/home/innereye/alarms/.txt') as f:
            cities_url = f.readlines()[1][:-1]
    else:
        oauth = os.environ['OAuth']
        cities_url = os.environ['cities_url']
    def get_coordinates(city_name):
        # city_name = city_name + ', ישראל'
        geocoder_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={city_name}&key={oauth}&language=iw'
        geocoding_result = requests.get(geocoder_url).json()
        if geocoding_result['results'] == []:
            lat = 0
            long = 0
        else:
            lat = geocoding_result['results'][0]['geometry']['location']['lat']
            long = geocoding_result['results'][0]['geometry']['location']['lng']
        return lat, long

    def get_coordinates_zofar(city_name):
        # cities = pd.read_json(cities_url)
        cities = requests.get(cities_url).json()
        if city_name in cities['cities'].keys():
            lat = cities['cities'][city_name]['lat']
            long = cities['cities'][city_name]['lng']
        else:
            lat = 0
            long = 0
        return lat, long

    coo = pd.read_csv(coord_file)
    if latest is None:
        latest = pd.read_csv('data/alarms.csv')
        latest = list(latest['cities'])
    missing = []
    for cit in np.unique(latest):
        if cit not in coo['loc'].values:
            missing.append(cit)

    # missing.extend(list(coo['loc'][bad]))
    # lat_long = [[], []]
    if len(missing) > 0:
        for miss in missing:
            lat, long = get_coordinates(miss)
            coo.loc[len(coo)+1] = [miss, lat, long]
        coo.sort_values('loc', inplace=True)
        coo.to_csv(coord_file, sep=',', index=False)
    bad = np.where((coo['lat'] == 31.046051) & (coo['long'] == 34.851612))[0]
    if len(bad) > 0:
        print(f'fixing {len(bad)} locations')
        for bd in bad:
            lat, long = get_coordinates_zofar(coo['loc'][bd])
            if lat == 0:
                lat, long = get_coordinates(coo['loc'][bd])
            coo.loc[bd] = [coo['loc'][bd], lat, long]
        coo.sort_values('loc', inplace=True)
        coo.to_csv(coord_file, sep=',', index=False)
    print('BAD COORDINATES:')
    print(list(coo['loc'][coo['lat'] == 0]))

