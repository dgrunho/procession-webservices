import os

__author__ = 'PT101410'

from requests.auth import HTTPBasicAuth
from bson.objectid import ObjectId
from datetime import datetime

import requests
import json
from os import path

SERVER_BASE = os.getenv('SMARTERFEST_HOST', 'https://smarterfest.eu-gb.mybluemix.net')

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
    'routes': ['OSM\\Rapazes_1.gpx',
               'OSM\\Tabuleiros_10.gpx',
               'OSM\\Mordomo_3.gpx',
               'OSM\\Bodo_12.gpx',
               'OSM\\Parciais_5.gpx'],
    'parking': ['Parques_estacionamento.gpx']
}


STRING_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
# endregion


# region network config


USER = 'mobile'
PASSWORD = 'mobile_tabuleiros_2015'
PARKING_URL = f'{SERVER_BASE}/mobile/post_parking'
PARKING_URL_EN = f'{SERVER_BASE}/mobile/post_parking_en'
# endregion



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


def do_main():
    with open('Parques_estacionamento.json') as json_file:
        parking = json.load(json_file)
    for park in parking:
        park["date"] = datetime.now().isoformat()
    send_to_service(PARKING_URL, json.dumps(parking))

    with open('Parques_estacionamento_en.json') as json_file2:
        parking_en = json.load(json_file2)
    for park in parking_en:
        park["date"] = datetime.now().isoformat()
    send_to_service(PARKING_URL_EN, json.dumps(parking_en))
do_main()
