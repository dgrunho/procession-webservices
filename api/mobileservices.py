import operator
import re
import threading
from datetime import datetime

from datetime import timedelta

import cherrypy
from cachetools import cachedmethod, TTLCache, keys
from cherrypy import tools

from api.db import get_db, save_to_mongo
from api.errorstatus import ErrorStatus


def _get_cache_key(name):
    def key(*args, **kwargs):
        return keys.hashkey(name, *args, **kwargs)

    return key


class MobileServices:
    def __init__(self):
        self.__db = None

        self._short_cache = TTLCache(maxsize=128, ttl=60)
        self._short_cache_lock = threading.RLock()

        self._long_cache = TTLCache(maxsize=128, ttl=600)
        self._long_cache_lock = threading.RLock()

    @property
    def _db(self):
        if self.__db is None:
            self.__db = get_db()

        return self.__db

    @cherrypy.expose('parking')
    @tools.json_out()
    # cache e header não combinam bem
    #@cachedmethod(
    #    cache=operator.attrgetter('_short_cache'),
    #    key=_get_cache_key('parking'),
    #    lock=operator.attrgetter('_short_cache_lock')
    #)
    def get_parking(self):
        db = self._db

        lang = cherrypy.request.headers.get('Accept-Language')
        if lang is None:
            lang = "en"

        if lang.lower().startswith("pt"):
            parking = db.parking.find({}, {'_id': False})
        else:
            parking = db.parking_en.find({}, {'_id': False})


        park_list = []



        for park in parking:
            park_list.append(
                {
                    "allocation": park['allocation'],
                    "coordinates": [
                        park['coordinates']['lat'],
                        park['coordinates']['lng']
                    ],
                    "name": park['name'],
                    "last_update": str(park['date']) if type(park['date']) == datetime else park['date'].isoformat(),
                    "cars_allowed": park['cars_allowed'],
                    "handicap_parking": park['handicap_parking'],
                    "buses_allowed": park['buses_allowed'],
                    "camping_vans_allowed": park['camping_vans_allowed'],
                    "paid": park['paid'],
                    "address": park['address'],
                    "other_info": park['other_info'],
                    "areas": park['areas']
                }
            )

        return park_list

    @cherrypy.expose('events')
    @tools.json_out()
    # cache e header não combinam bem
    #@cachedmethod(
    #    cache=operator.attrgetter('_long_cache'),
    #    key=_get_cache_key('events'),
    #    lock=operator.attrgetter('_long_cache_lock')
    #)
    def get_events(self):
        db = self._db
        # result = db.events.find({}, {'_id': False})

        lang = cherrypy.request.headers.get('Accept-Language')
        if lang is None:
            lang = "en"

        if lang.lower().startswith("pt"):
            agenda = db.agenda_pt.find({}, {'_id': False})
        else:
            agenda = db.agenda_en.find({}, {'_id': False})

        event_list = []

        for event in agenda:
            is_event_recent = event['date'] > datetime.now()
            if type(event['longitude']) == float and type(event['latitude']) and is_event_recent:
                event_list.append(event)

        coordinates_list = []
        for event in event_list:
            event_coordinates = (event['longitude'], event['latitude'])
            if event_coordinates not in coordinates_list:
                coordinates_list.append(event_coordinates)

        recent_events = []
        event_date = None
        for coordinates in coordinates_list:
            tmp = []
            for event in event_list:

                event_coordinates = (event['longitude'], event['latitude'])
                if event_coordinates == coordinates:
                    tmp.append(event)

            if len(tmp) == 1:
                recent_events.append(tmp[0])
            elif len(tmp) > 1:
                for event in tmp:
                    if event_date is None:
                        event_date = event['date']
                        recent_events.append(event)
                        continue

                    date_valid_recent = event['date'] < event_date \
                                        and not event['date'] < datetime.now()

                    if date_valid_recent:
                        event_date = event['date']
                        recent_events[-1] = event
        for event in recent_events:
            if event['date'] is not None:
                event['date'] = event['date'].isoformat()
        return recent_events

    @cherrypy.expose('processions_agenda')
    @tools.json_out()
    # cache e header não combinam bem
    #@cachedmethod(
    #    cache=operator.attrgetter('_long_cache'),
    #    key=_get_cache_key('processions_agenda'),
    #    lock=operator.attrgetter('_long_cache_lock')
    #)
    def get_processions_agenda(self):
        db = self._db

        lang = cherrypy.request.headers.get('Accept-Language')
        if lang is None:
            lang = "en"

        if lang.lower().startswith("pt"):
            agenda = db.agenda_pt.find({}, {'_id': False})
        else:
            agenda = db.agenda_en.find({}, {'_id': False})

        procession_list = []

        for procession in agenda:
            has_coordinates = type(procession['longitude']) == float and type(procession['latitude']) == float
            # is_procession = procession['description'].lower() in PROCESSIONS
            if not has_coordinates:
                if procession['date'] is not None:
                    procession['date'] = procession['date'].isoformat()
                procession_list.append(procession)

        return procession_list

    @cherrypy.expose('agenda')
    @tools.json_out()
#    @cachedmethod(
#        cache=operator.attrgetter('_long_cache'),
#        key=_get_cache_key('agenda'),
#        lock=operator.attrgetter('_long_cache_lock')
#    )
    def get_agenda(self, status='current'):
        if status not in ['current', 'past']:
            return ErrorStatus(400, 'Invalid status value').__dict__

        results = []
        db = self._db

        lang = cherrypy.request.headers.get('Accept-Language')
        if lang is None:
            lang = "en"

        query = {}


        dtCompare = datetime.now() + timedelta(hours=1) #o servidor não está na timezone correta e houve stress a mudar

        if status == 'current':
            query['date'] = {'$gt': dtCompare}
        else:
            query['date'] = {'$lt': dtCompare}

        if lang.lower().startswith("pt"):
            query_result = db.agenda_pt.find(query, {'_id': False}).sort('date',1)
        else:
            query_result = db.agenda_en.find(query, {'_id': False}).sort('date',1)

        for event in query_result:
            event['date'] = event['date'].isoformat()

            if lang.lower().startswith("pt"):
                event['is_cortejo'] = ("cortejo" in event['description'].lower())
            else:
                event['is_cortejo'] = ("procession" in event['description'].lower())

            results.append(event)

        return results

    @cherrypy.expose('routes')
    @tools.json_out()
    #@cachedmethod(
    #    cache=operator.attrgetter('_long_cache'),
    #    key=_get_cache_key('routes'),
    #    lock=operator.attrgetter('_long_cache_lock')
    #)
    def get_routes(self):
        db = self._db

        device = cherrypy.request.headers.get('Device')
        if device is None:
            device = "Android"

        if device == "IOS":
            result = db.routes_ios.find({}, {'_id': False})
        else:
            result = db.routes.find({}, {'_id': False})

        return list(result)

    @cherrypy.expose('routesWith')
    @tools.json_out()
    @cachedmethod(
        cache=operator.attrgetter('_short_cache'),
        key=_get_cache_key('routesWith'),
        lock=operator.attrgetter('_short_cache_lock')
    )
    def get_routes(self, procession_name=''):
        db = self._db

        term = re.compile(re.escape(procession_name), re.IGNORECASE)

        routes = db.routes.find({'name': term}, {'_id': False})
        route_list = []

        for route in routes:
            route_list.append(route)

        return route_list

    @cherrypy.expose('processions')
    @tools.allow(methods='GET')
    @tools.json_out()
    #@cachedmethod(
    #    cache=operator.attrgetter('_short_cache'),
    #    key=_get_cache_key('processions'),
    #    lock=operator.attrgetter('_short_cache_lock')
    #)
    def get_procession(self):
        cherrypy.response.headers['Content-Type'] = "application/json"

        db = self._db

        device = cherrypy.request.headers.get('Device')
        if device is None:
            device = "Android"

        if device == "IOS":
            result = db.get_collection('processionPositions_ios').aggregate([
                {
                    "$sort": {"identifier": 1, "index": 1}
                },
                {
                    "$group": {
                        "_id": "$identifier",
                        "positions": {
                            "$push": {
                                "identifier": "$identifier",
                                "position": "$position",
                                "date": {
                                    # Ensure that the date is formatted as the apps expect it
                                    # (2019-05-28 15:07:46)
                                    "$dateToString": {
                                        "format": "%Y-%m-%d %H:%M:%S",
                                        "date": "$date"
                                    }
                                }
                            }
                        }
                    }
                }
            ])
        else:
            result = db.get_collection('processionPositions').aggregate([
                {
                    "$sort": {"identifier": 1, "index": 1}
                },
                {
                    "$group": {
                        "_id": "$identifier",
                        "positions": {
                            "$push": {
                                "identifier": "$identifier",
                                "position": "$position",
                                "date": {
                                    # Ensure that the date is formatted as the apps expect it
                                    # (2019-05-28 15:07:46)
                                    "$dateToString": {
                                        "format": "%Y-%m-%d %H:%M:%S",
                                        "date": "$date"
                                    }
                                }
                            }
                        }
                    }
                }
            ])



        return [r['positions'] for r in result]

    @cherrypy.expose
    @tools.json_out()
    @tools.json_in()
    @tools.allow(methods='Post')
    def post_agenda_pt(self):
        agendas = cherrypy.request.json

        db = self._db
        db['agenda_pt'].remove()

        last_event_hour = "00:00:00"
        for agenda in agendas:
            event_hour = agenda["start_hour"].lower()
            event_hour = event_hour.replace("00h00", "23:59")
            event_hour = event_hour.replace("hh", ":")
            event_hour = event_hour.replace("h", ":")
            event_hour = event_hour.replace(" ", "")

            try:
                agenda["date"] = datetime.fromisoformat(agenda["date"] + " " + event_hour + ":00")
                last_event_hour = event_hour
            except ValueError:
                dtsave = datetime.strptime(agenda["date"] + " " + last_event_hour + ":00", '%Y-%m-%d %H:%M:%S')
                dtsaveFinal = dtsave + timedelta(hours=1)
                agenda["date"] = dtsaveFinal #datetime.fromisoformat(agenda["date"] + " " + last_event_hour + ":00")


            save_to_mongo(agenda, 'agenda_pt')

        return 'ok'

    @cherrypy.expose
    @tools.json_out()
    @tools.json_in()
    @tools.allow(methods='Post')
    def post_agenda_en(self):
        agendas = cherrypy.request.json

        db = self._db
        db['agenda_en'].remove()

        last_event_hour = "00:00:00"
        for agenda in agendas:
            event_hour = agenda["start_hour"].lower()
            event_hour = event_hour.replace("00h00", "23:59")
            event_hour = event_hour.replace("hh", ":")
            event_hour = event_hour.replace("h", ":")
            event_hour = event_hour.replace(" ", "")

            try:
                agenda["date"] = datetime.fromisoformat(agenda["date"] + " " + event_hour + ":00")
                last_event_hour = event_hour
            except ValueError:
                agenda["date"] = datetime.fromisoformat(agenda["date"] + " " + last_event_hour + ":01")
            save_to_mongo(agenda, 'agenda_en')

        return 'ok'

    @cherrypy.expose
    @tools.json_out()
    @tools.json_in()
    @tools.allow(methods='Post')
    def post_routes(self):
        routes = cherrypy.request.json

        for route in routes:
            save_to_mongo(route, 'routes')

        return 'ok'

    @cherrypy.expose
    @tools.json_out()
    @tools.json_in()
    @tools.allow(methods='Post')
    def post_routes_ios(self):
        routes = cherrypy.request.json

        for route in routes:
            save_to_mongo(route, 'routes_ios')

        return 'ok'

    @cherrypy.expose
    @tools.json_out()
    @tools.json_in()
    @tools.allow(methods='Post')
    def post_parking(self):
        parking = cherrypy.request.json
        for park in parking:
            park["date"] = datetime.fromisoformat(park["date"])
            # db = self._db
            # db['parking'].remove()
            save_to_mongo(park, 'parking')

        return 'ok'

    @cherrypy.expose
    @tools.json_out()
    @tools.json_in()
    @tools.allow(methods='Post')
    def post_parking_en(self):
        parking = cherrypy.request.json
        for park in parking:
            park["date"] = datetime.fromisoformat(park["date"])
            # db = self._db
            # db['parking_en'].remove()
            save_to_mongo(park, 'parking_en')

        return 'ok'

    @cherrypy.expose('remove')
    @tools.json_out()
    def delete_collection(self, collection='events'):
        db = self._db

        if collection not in db.collection_names():  # ['processionPositions', 'events']:
            return ErrorStatus(400, 'Invalid collection value').__dict__

        db[collection].remove()

        return 'ok'
