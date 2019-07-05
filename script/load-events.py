#!/usr/local/bin/python
#  coding: utf-8
__author__ = 'mac02-softinsa'

import os
import xlrd
import pymongo
import requests
import json
import json
# from dao.mongoaccess import MongoAccess as mongo
from requests.auth import HTTPBasicAuth
from datetime import datetime

SERVER_BASE = os.getenv('SMARTERFEST_HOST', 'http://smarterfest-smarterservices.apps.softinsa.com')

# FILE_PATH = r'/Users/mac02-softinsa/Desktop/'
# FILE_PATH = r'C:\Users\0100849\Desktop' + '\\'
# FILE_NAME = r'eventos.xlsx'
FILE_PATH = os.path.dirname(os.path.realpath(__file__)) + '/'
FILE_NAME = r'agenda_pt.xlsx'
FILE_NAME_en = r'agenda_en.xlsx'
POST_AGENDA_URL = f'{SERVER_BASE}/mobile/post_agenda_pt'
POST_AGENDA_URL_en = f'{SERVER_BASE}/mobile/post_agenda_en'

USER = 'mobile'
PASSWORD = 'mobile_tabuleiros_2015'
STRING_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


class Event():
    def __init__(self, date, start_hour,
                 location, latitude, longitude, description, other_information, download_link):
        # strttime(STRING_DATE_FORMAT)
        self.date = date.isoformat()
        self.start_hour = start_hour
        self.location = location
        if latitude != "":
            self.latitude = latitude
            self.longitude = longitude
        self.description = description
        self.other_information = other_information
        self.download_link = download_link

    def __str__(self):
        return str(self.__dict__)


def do_main():
    db = pymongo.MongoClient('localhost', 27017).smarterfestdb
    event_list = []

    book = xlrd.open_workbook(FILE_PATH + FILE_NAME)
    sheet = book.sheet_by_index(0)
    try:
        for line in range(1, sheet.nrows):
            row = sheet.row(line)
            event_list.append(
                Event(
                    date=datetime(*xlrd.xldate_as_tuple(row[1].value, book.datemode)),
                    start_hour=row[2].value,
                    location=row[3].value,
                    latitude=row[4].value,
                    longitude=row[5].value,
                    description=row[6].value,
                    other_information=row[7].value,
                    download_link=row[8].value
                ).__dict__
            )
    except Exception as e:
        print('error: {} \n stack trace: {}'.format(e.message, e))

    # for event in event_list:
    #     db['events'].insert_one(event.__dict__)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(POST_AGENDA_URL,
                      # json.dumps(event_list, default=Event.__dict__),
                      json.dumps(event_list),
                      headers=headers,
                      auth=HTTPBasicAuth(USER, PASSWORD))
    if r.status_code is not 200:
        raise Exception('Invalid HTTP Status {}'.format(r.status_code))
    else:
        print('PT job done!')



    event_list = []

    book = xlrd.open_workbook(FILE_PATH + FILE_NAME_en)
    sheet = book.sheet_by_index(0)
    try:
        for line in range(1, sheet.nrows):
            row = sheet.row(line)
            event_list.append(
                Event(
                    date=datetime(*xlrd.xldate_as_tuple(row[1].value, book.datemode)),
                    start_hour=row[2].value,
                    location=row[3].value,
                    latitude=row[4].value,
                    longitude=row[5].value,
                    description=row[6].value,
                    other_information=row[7].value,
                    download_link=row[8].value
                ).__dict__
            )
    except Exception as e:
        print('error: {} \n stack trace: {}'.format(e.message, e))

    # for event in event_list:
    #     db['events'].insert_one(event.__dict__)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(POST_AGENDA_URL_en,
                      # json.dumps(event_list, default=Event.__dict__),
                      json.dumps(event_list),
                      headers=headers,
                      auth=HTTPBasicAuth(USER, PASSWORD))
    if r.status_code is not 200:
        raise Exception('Invalid HTTP Status {}'.format(r.status_code))
    else:
        print('EN job done!')
do_main()




