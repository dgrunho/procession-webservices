from datetime import datetime

import cherrypy
import pymongo
from bson import ObjectId
from cherrypy import tools

from api.db import get_db
from api.errorstatus import ErrorStatus
from api.utils import updateRoute
from api.utils import updateRoute_ios
from api.utils import endProcession


class WebServices:
    def __init__(self):
        self.__db = None

    @property
    def _db(self):
        if self.__db is None:
            self.__db = get_db()

        return self.__db

    @cherrypy.expose('procession')
    @tools.json_out()
    @tools.json_in()
    @tools.allow(methods=['POST', 'OPTIONS'])
    def post_procession(self):
        if cherrypy.request.method == "POST":
            data = cherrypy.request.json
            data['date'] = datetime.today()

            db = self._db
            positions = db.get_collection('processionTrackerPositions')

            if data['processionPoint'] == 'tail':
                positions.remove({
                    'identifier': data['id'],
                    'processionPoint': 'tail'
                })

                positions.insert({
                    'identifier': data['id'],
                    'position': data['position'],
                    'date': data['date'],
                    'processionPoint': 'tail'
                })

            else:
                positions.remove({
                    'identifier': data['id'],
                    'processionPoint': 'head'
                })

                positions.insert({
                    'identifier': data['id'],
                    'position': data['position'],
                    'date': data['date'],
                    'processionPoint': 'head'
                })

            updateRoute(data['id'], True)
            updateRoute_ios(data['id'], True)
            return 'ok'
            #positions = db.get_collection('processionPositions')
            #position_history = db.get_collection('procession_history')

            #if data['processionPoint'] == 'tail':
            #    # Find the tail point that was previously marked,
            #    # and use its date to remove any points older than it,
            #    # that also belong to the current procession.
            #    current_tail_point = positions.find_one({
            #        'position.lat': data['position']['lat'],
            #        'position.lng': data['position']['lng'],
            #        'identifier': data['id']
            #    })

            #    positions.remove({
            #        'date': {
            #            '$lt': current_tail_point['date']
            #        },
            #        'identifier': current_tail_point['identifier']
            #    })
            #else:
            #    positions.insert({
            #        'identifier': data['id'],
            #        'position': data['position'],
            #        'date': data['date']
            #    })

            #data['identifier'] = data['id']
            #del data['id']

            #position_history.insert(data)

            #return 'ok'

    @cherrypy.expose('post_procession_tracker')
    @tools.json_out()
    @tools.json_in()
    @tools.allow(methods=['POST', 'OPTIONS'])
    def post_procession(self):
        if cherrypy.request.method == "POST":
            db = self._db

            try:
                positions_log = db.get_collection('processionTrackerPositionsLog')
                positions_log.insert({
                    'data': cherrypy.request.json
                })
            except:
                a = 0

            data = cherrypy.request.json
            data['date'] = datetime.today()

            positions = db.get_collection('processionTrackerPositions')

            if data['processionPoint'] == 'tail':
                positions.remove({
                    'identifier': data['id'],
                    'processionPoint': 'tail'
                })

                positions.insert({
                    'identifier': data['id'],
                    'position': data['position'],
                    'date': data['date'],
                    'processionPoint': 'tail'
                })
                updateRoute(data['id'], False)
                updateRoute_ios(data['id'], False)
            elif data['processionPoint'] == 'head':
                positions.remove({
                    'identifier': data['id'],
                    'processionPoint': 'head'
                })

                positions.insert({
                    'identifier': data['id'],
                    'position': data['position'],
                    'date': data['date'],
                    'processionPoint': 'head'
                })
                updateRoute(data['id'], False)
                updateRoute_ios(data['id'], False)
            else:
                endProcession(data['id'])


            return 'ok'

    @cherrypy.expose('post_location')
    @tools.json_out()
    @tools.json_in()
    @tools.allow(methods=['POST', 'OPTIONS'])
    def post_procession(self):
        if cherrypy.request.method == "POST":
            data = cherrypy.request.json
            data['date'] = datetime.today()

            db = self._db

            try:
                positions_log = db.get_collection('processionTrackerPositionsLog')
                positions_log.insert({
                    'data': cherrypy.request.json
                })
            except:
                a = 0

            locations = db.get_collection('processionTrackerLocations')
            locations.remove({
                'device_identifier': data['deviceid']
            })

            locations.insert({
                'device_identifier': data['deviceid'],
                'position': data['position'],
                'date': data['date']
            })
            return 'ok'

    @cherrypy.expose('update_procession_route')
    @tools.json_out()
    @tools.json_in()
    @tools.allow(methods=['POST', 'OPTIONS'])
    def post_procession_update(self):
        if cherrypy.request.method == "POST":
            data = cherrypy.request.json
            updateRoute(data['id'])
            updateRoute_ios(data['id'])
            return 'ok'

    @cherrypy.expose('get_procession_tracker')
    @tools.allow(methods='GET')
    @tools.json_out()
    def get_procession(self, id=None):
        cherrypy.response.headers['Content-Type'] = "application/json"

        db = self._db
        positions = db.processionTrackerPositions.find({'identifier': id})
        return [{
            'id': position['identifier'],
            'position': position['position'],
            'processionPoint': position['processionPoint'],
            'date': position['date'].isoformat()
        } for position in positions]

    @cherrypy.expose('get_tracker_locations')
    @tools.allow(methods='GET')
    @tools.json_out()
    def get_procession(self):
        cherrypy.response.headers['Content-Type'] = "application/json"

        db = self._db
        locations = db.processionTrackerLocations.find({})
        return [{
            'device_id': location['device_identifier'],
            'position': location['position'],
            'date': location['date'].isoformat()
        } for location in locations]

    @cherrypy.expose('processionFinish')
    @tools.json_out()
    @tools.json_in()
    @tools.allow(methods=['POST', 'OPTIONS'])
    def post_procession(self):
        if cherrypy.request.method == "POST":
            data = cherrypy.request.json

            endProcession(data['id'])
            return 'ok'

    @cherrypy.expose('expectedroute')
    @tools.json_out()
    def get_expected_position(self, id=None):
        if id is None:
            raise cherrypy.HTTPError(status=400, message='No id specified.')

        db = self._db
        position = db.get_collection('routes').find_one({'identifier': id})

        return [{
            'lat': coordinate[0],
            'lng': coordinate[1]
        } for coordinate in position['coordinates']]

    @cherrypy.expose('processionposition')
    @tools.json_out()
    def get_current_position(self, id=None):
        if id is None:
            raise cherrypy.HTTPError(status=400, message='No id specified.')

        db = self._db
        positions = db.get_collection('processionPositions').find({'identifier': id}).sort(
            'date', pymongo.ASCENDING)

        return [{
            'position': position['position'],
            'date': position['date'].isoformat(),
            'index': position['index']
        } for position in positions]

    @cherrypy.expose('processionposition_ios')
    @tools.json_out()
    def get_current_position(self, id=None):
        if id is None:
            raise cherrypy.HTTPError(status=400, message='No id specified.')

        db = self._db
        positions = db.get_collection('processionPositions_ios').find({'identifier': id}).sort(
            'date', pymongo.ASCENDING)

        return [{
            'position': position['position'],
            'date': position['date'].isoformat(),
            'index': position['index']
        } for position in positions]

    @cherrypy.expose('remove')
    @tools.json_out()
    def delete_collection(self, collection='processionPositions'):
        if collection not in ['processionPositions', 'events']:
            return ErrorStatus(400, 'Invalid collection value').__dict__

        db = self._db
        db[collection].remove({})

        return 'ok'

    @cherrypy.expose('parkingget')
    @tools.json_out()
    @tools.allow(methods=['GET'])
    def get_parking(self):
        db = self._db

        parks = db.get_collection('parking').find({})

        return [{
            'id': str(park['_id']),
            'name': park['name']
        } for park in parks]

    @cherrypy.expose('routesummary')
    @tools.json_out()
    @tools.json_in()
    def get_route_summary(self):
        db = self._db

        routes = db.get_collection('routes').find({})

        return [{
            'id': str(route['identifier']),
            'name': route['name']
        } for route in routes]

    @cherrypy.expose('parkingupdate')
    @tools.json_out()
    @tools.json_in()
    @tools.allow(methods=['POST', 'OPTIONS'])
    def post_parking(self):
        if cherrypy.request.method == "POST":
            data = cherrypy.request.json

            db = self._db

            db.get_collection('parking').update(
                {
                    '_id': ObjectId(data['id'])
                },
                {
                    '$set': {
                        'date': datetime.today(),
                        'allocation': data['allocation']
                    }
                })

            db.get_collection('parking_en').update(
                {
                    '_id': ObjectId(data['id'])
                },
                {
                    '$set': {
                        'date': datetime.today(),
                        'allocation': data['allocation']
                    }
                })
