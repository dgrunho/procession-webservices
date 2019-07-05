import os

__author__ = 'mac02-softinsa'

from requests.auth import HTTPBasicAuth
from bson.objectid import ObjectId
from datetime import datetime

import gpxpy
import gpxpy.gpx
import requests
import json
from os import path

SERVER_BASE = os.getenv('SMARTERFEST_HOST', 'https://smarterfest.eu-gb.mybluemix.net')
#SERVER_BASE = os.getenv('SMARTERFEST_HOST', 'https://smarterfest-dev-diogo-grunho.eu-gb.mybluemix.net')
#SERVER_BASE = os.getenv('SMARTERFEST_HOST', 'http://127.0.0.1:9999')

# region file config
# FILE_PATH = r'C:\Users\0100849\Desktop\coordinates' + '\\'
FILE_PATH = path.dirname(path.realpath(__file__))
FILES = {
    'events': [], # 'Bodo_pontos_20.gpx', 'JPopulares_pontos_20.gpx', 'Parciais_pontos_20.gpx'],
    #'routes': ['Rapazes_1.gpx',
    #           'Tabuleiros_10.gpx',
    #           'Mordomo_3.gpx',
    #           'Bodo_12.gpx',
    #           'Parciais_5.gpx'],
    'routes': [os.path.join('OSM', 'Rapazes_1.gpx'),
               os.path.join('OSM', 'Tabuleiros_10.gpx'),
               os.path.join('OSM', 'Mordomo_3.gpx'),
               os.path.join('OSM', 'Bodo_12.gpx'),
               os.path.join('OSM', 'Parciais Hotel Templários_501.gpx'),
               os.path.join('OSM', 'Parciais Rua Alexandre Herculano_502.gpx'),
               os.path.join('OSM', 'Parciais Rua Major Ferreira Amaral_503.gpx')],
    'routes_ios': [os.path.join('IOS', 'Rapazes_1.gpx'),
                   os.path.join('IOS', 'Tabuleiros_10.gpx'),
                   os.path.join('IOS', 'Mordomo_3.gpx'),
                   os.path.join('IOS', 'Bodo_12.gpx'),
                   os.path.join('IOS', 'Parciais Hotel Templários_501.gpx'),
                   os.path.join('IOS', 'Parciais Rua Alexandre Herculano_502.gpx'),
                   os.path.join('IOS', 'Parciais Rua Major Ferreira Amaral_503.gpx')],
    'parking': ['Parques_estacionamento.gpx']
}


STRING_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
# endregion


# region network config


USER = 'mobile'
PASSWORD = 'mobile_tabuleiros_2015'
EVENTS_URL = f'{SERVER_BASE}/mobile/post_events'
ROUTES_URL = f'{SERVER_BASE}/mobile/post_routes'
ROUTES_IOS_URL = f'{SERVER_BASE}/mobile/post_routes_ios'
REMOVE_COLLECTION_URL = f'{SERVER_BASE}/mobile/remove?collection='
PARKING_URL = f'{SERVER_BASE}/mobile/post_parking'

# endregion


class WayPoint():
    def __init__(self, name, latitude, longitude):
        self.name = name if name is not None else ObjectId()
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return str(self.__dict__)


class Route():
    def __init__(self, name, coordinates):
        self.name = name.split('_')[0]
        self.coordinates = coordinates
        self.identifier = name.split('_')[1].split('.')[0]

    def __str__(self):
        return str(self.__dict__)


# Parsing an existing file:
# -------------------------

# gpx_file = open(FILE_PATH + FILES['routes'][0], 'r')
#
# gpx = gpxpy.parse(gpx_file)
#
# for track in gpx.tracks:
#     for segment in track.segments:
#         for point in segment.points:
#             print 'Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation)
#
# for waypoint in gpx.waypoints:
#     print 'waypoint {0} -> ({1},{2})'.format(waypoint.name, waypoint.latitude, waypoint.longitude)

# for route in gpx.routes:
#     print 'Route:'
#     for point in route.points:
#         print 'Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation)

# There are many more utility methods and functions:
# You can manipulate/add/remove tracks, segments, points, waypoints and routes and
# get the GPX XML file from the resulting object:

# print 'GPX:', gpx.to_xml()


def get_gpx(files, route=False, parking=False):
    gpx_list = []
    parking_count = 0

    for i in files:
        gpx_file = open(path.join(FILE_PATH, i), 'r')
        gpx = gpxpy.parse(gpx_file)

        if route:
            gpx_list.append(
                Route(
                    name=i[4:],
                    coordinates=[[waypoint.latitude, waypoint.longitude] for waypoint in gpx.waypoints]
                ).__dict__
            )
        elif parking:
            for waypoint in gpx.waypoints:
                gpx_list.append(
                    {
                        "coordinates": {
                            "lat": waypoint.latitude,
                            "lng": waypoint.longitude
                        },
                        "name": "Parque {}".format(parking_count + 1),
                        "date": datetime.now().isoformat(),
                        "allocation": "low",
                        "buses_allowed": True,
                        "paid": True
                    }
                )
                parking_count += 1
        else:
            for waypoint in gpx.waypoints:
                gpx_list.append(
                    WayPoint(
                        # waypoint.name,
                        name=i.split('_')[0],
                        latitude=waypoint.latitude,
                        longitude=waypoint.longitude
                    ).__dict__
                )

    return gpx_list


def send_to_service(url, data):
    r = requests.post(
        url,
        data,
        auth=HTTPBasicAuth('mobile', 'mobile_tabuleiros_2015'),
        headers={'Content-type': 'application/json', 'Accept': 'text/plain'}
    )

    if r.status_code is not 200:
        raise Exception('invalid response {}'.format(r.status_code))
    else:
        print('job done')
    return

def remove_collection(collection):
    r = requests.post(
        REMOVE_COLLECTION_URL + collection,
        '',
        auth=HTTPBasicAuth('mobile', 'mobile_tabuleiros_2015'),
        headers={'Content-type': 'application/json', 'Accept': 'text/plain'}
    )

    if r.status_code is not 200:
        raise Exception('invalid response {}'.format(r.status_code))
    else:
        print('remove collection done')
    return

def do_main():

    routes = get_gpx(FILES['routes'], route=True)
    remove_collection('routes')
    send_to_service(ROUTES_URL, json.dumps(routes, default=Route.__dict__))

    routes_IOS = get_gpx(FILES['routes_ios'], route=True)
    remove_collection('routes_ios')
    send_to_service(ROUTES_IOS_URL, json.dumps(routes_IOS, default=Route.__dict__))

    # events = get_gpx(FILES['events'])
    # send_to_service(EVENTS_URL, json.dumps(events, default=WayPoint.__dict__))

    # usar antes o load-parking.py
    # parking = get_gpx(FILES['parking'], parking=True)
    # send_to_service(PARKING_URL, json.dumps(parking))
do_main()
