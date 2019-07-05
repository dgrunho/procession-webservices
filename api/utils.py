from datetime import datetime

import geopy.distance
import pymongo

from api.db import get_db
from datetime import timedelta


def updateRoute(id, allow_backtraking):
    data = {
        "id": id
    }
    db = get_db()

    ignore = False
    if allow_backtraking == False:
        processionsIgnore = db.processionTrackerIgnore.find({'identifier': data['id']})
        for procession in processionsIgnore:
            if procession['identifier'] == data['id']:
                ignore = procession['ignore']

    if ignore == False:
        positions = db.processionTrackerPositions.find({'identifier': data['id']})
        routes = db.routes.find({'identifier': data['id']})

        indexes = db.get_collection('processionTrackerIndexes').find({'identifier': data['id']})
        indexes_ins = db.get_collection('processionTrackerIndexes')

        head = (-1, -1)
        tail = (-1, -1)
        for position in positions:
            if position['processionPoint'] == "head":
                head = (position['position']['lat'], position['position']['lng'])
            if position['processionPoint'] == "tail":
                tail = (position['position']['lat'], position['position']['lng'])

        if head != (-1, -1):

            for route in routes:

                if tail == (-1, -1):
                    tail = route['coordinates'][0]

                headIndex = -1
                tailIndex = -1
                for index in indexes:
                    if index['identifier'] == data['id'] and index['processionPoint'] == 'head':
                        headIndex = index['index']
                        headIndexDate = index['date']
                    if index['identifier'] == data['id'] and index['processionPoint'] == 'tail':
                        tailIndex = index['index']
                        tailIndexDate = index['date']



                # Find new positions
                distance = 200000000
                ClosestIndex = 0

                for i in range(len(route['coordinates'])):
                    dt = geopy.distance.vincenty(head, route['coordinates'][i]).km
                    if dt < distance:
                        ClosestIndex = i
                        distance = dt
                if allow_backtraking == True:
                    headIndex = ClosestIndex
                    indexes_ins.remove({
                        'identifier': data['id'],
                        'processionPoint': 'head'
                    })
                    indexes_ins.insert({
                        'identifier': data['id'],
                        'index': headIndex,
                        'date': datetime.today(),
                        'processionPoint': 'head'
                    })

                if ClosestIndex >= headIndex:
                    if ClosestIndex >= headIndex + 5 and (datetime.today() - headIndexDate).total_seconds() <= 45:
                        #do nothing
                        headIndex = headIndex
                    else:
                        headIndex = ClosestIndex
                        indexes_ins.remove({
                            'identifier': data['id'],
                            'processionPoint': 'head'
                        })
                        indexes_ins.insert({
                            'identifier': data['id'],
                            'index': headIndex,
                            'date': datetime.today(),
                            'processionPoint': 'head'
                        })

                distance = 200000000
                ClosestIndex = 0
                for i in range(headIndex + 1):
                    dt = geopy.distance.vincenty(tail, route['coordinates'][i]).km
                    if dt < distance:
                        ClosestIndex = i
                        distance = dt
                if allow_backtraking == True:
                    tailIndex = ClosestIndex
                    indexes_ins.remove({
                        'identifier': data['id'],
                        'processionPoint': 'tail'
                    })
                    indexes_ins.insert({
                        'identifier': data['id'],
                        'index': tailIndex,
                        'date': datetime.today(),
                        'processionPoint': 'tail'
                    })

                if ClosestIndex > tailIndex:
                    if ClosestIndex >= tailIndex + 5 and (datetime.today() - tailIndexDate).total_seconds() <= 45:
                        #do nothing
                        tailIndex = tailIndex
                    else:
                        tailIndex = ClosestIndex
                        indexes_ins.remove({
                            'identifier': data['id'],
                            'processionPoint': 'tail'
                        })
                        indexes_ins.insert({
                            'identifier': data['id'],
                            'index': tailIndex,
                            'date': datetime.today(),
                            'processionPoint': 'tail'
                        })

                # minimum distance just in case
                #if headIndex - tailIndex < 6:
                #    tailIndex = tailIndex - 6
                #    if tailIndex < 0:
                #        tailIndex = 0

                # fill positions to update
                FinalHead = headIndex + 1
                if FinalHead > len(route['coordinates']):
                    FinalHead = headIndex

                posIns = []
                for i in range(tailIndex, FinalHead):
                    dt = datetime.today()
                    dtf = dt + timedelta(milliseconds=i)
                    posIns.append({
                        'identifier': data['id'],
                        'position': {
                            'lat': route['coordinates'][i][0],
                            'lng': route['coordinates'][i][1]
                        },
                        'date': dtf,
                        'processionPoint': 'head',
                        'index': i
                    })

                positionsAll = db.get_collection('processionPositions')
                # delete old positions
                positionsAll.remove({
                    'identifier': data['id']
                })
                # insert new positions
                positionsAll.insert_many(posIns)


def updateRoute_ios(id, allow_backtraking):
    data = {
        "id": id
    }
    if data['id'] == "501" or data['id'] == "502" or data['id'] == "503":
        updateRoute_calc_ios(data['id'], True)
    else:
        db = get_db()
        ignore = False
        if allow_backtraking == False:
            processionsIgnore = db.processionTrackerIgnore.find({'identifier': data['id']})
            for procession in processionsIgnore:
                if procession['identifier'] == data['id']:
                    ignore = procession['ignore']

        if ignore == False:
            positions = db.processionTrackerPositions.find({'identifier': data['id']})
            routes = db.routes_ios.find({'identifier': data['id']})

            indexes = db.get_collection('processionTrackerIndexes').find({'identifier': data['id']})
            indexes_ins = db.get_collection('processionTrackerIndexes')

            head = (-1, -1)
            tail = (-1, -1)
            for position in positions:
                if position['processionPoint'] == "head":
                    head = (position['position']['lat'], position['position']['lng'])
                if position['processionPoint'] == "tail":
                    tail = (position['position']['lat'], position['position']['lng'])

            if head != (-1, -1):

                for route in routes:

                    if tail == (-1, -1):
                        tail = route['coordinates'][0]

                    headIndex = -1
                    tailIndex = -1
                    for index in indexes:
                        if index['identifier'] == data['id'] and index['processionPoint'] == 'head':
                            headIndex = index['index']
                            headIndexDate = index['date']
                        if index['identifier'] == data['id'] and index['processionPoint'] == 'tail':
                            tailIndex = index['index']
                            tailIndexDate = index['date']


                    # fill positions to update
                    FinalHead = headIndex + 1
                    if FinalHead > len(route['coordinates']):
                        FinalHead = headIndex

                    posIns = []
                    for i in range(tailIndex, FinalHead):
                        dt = datetime.today()
                        dtf = dt + timedelta(milliseconds=i)
                        posIns.append({
                            'identifier': data['id'],
                            'position': {
                                'lat': route['coordinates'][i][0],
                                'lng': route['coordinates'][i][1]
                            },
                            'date': dtf,
                            'processionPoint': 'head',
                            'index': i
                        })

                    positionsAll = db.get_collection('processionPositions_ios')
                    # delete old positions
                    positionsAll.remove({
                        'identifier': data['id']
                    })
                    # insert new positions
                    positionsAll.insert_many(posIns)

def updateRoute_calc_ios(id, allow_backtraking):
    data = {
        "id": id
    }
    db = get_db()
    ignore = False
    if allow_backtraking == False:
        processionsIgnore = db.processionTrackerIgnore.find({'identifier': data['id']})
        for procession in processionsIgnore:
            if procession['identifier'] == data['id']:
                ignore = procession['ignore']

    if ignore == False:
        positions = db.processionTrackerPositions.find({'identifier': data['id']})
        routes = db.routes_ios.find({'identifier': data['id']})

        indexes = db.get_collection('processionTrackerIndexes_ios').find({'identifier': data['id']})
        indexes_ins = db.get_collection('processionTrackerIndexes_ios')

        head = (-1, -1)
        tail = (-1, -1)
        for position in positions:
            if position['processionPoint'] == "head":
                head = (position['position']['lat'], position['position']['lng'])
            if position['processionPoint'] == "tail":
                tail = (position['position']['lat'], position['position']['lng'])

        if head != (-1, -1):

            for route in routes:

                if tail == (-1, -1):
                    tail = route['coordinates'][0]

                headIndex = -1
                tailIndex = -1
                for index in indexes:
                    if index['identifier'] == data['id'] and index['processionPoint'] == 'head':
                        headIndex = index['index']
                        headIndexDate = index['date']
                    if index['identifier'] == data['id'] and index['processionPoint'] == 'tail':
                        tailIndex = index['index']
                        tailIndexDate = index['date']



                # Find new positions
                distance = 200000000
                ClosestIndex = 0

                for i in range(len(route['coordinates'])):
                    dt = geopy.distance.vincenty(head, route['coordinates'][i]).km
                    if dt < distance:
                        ClosestIndex = i
                        distance = dt
                if allow_backtraking == True:
                    headIndex = ClosestIndex
                if ClosestIndex > headIndex:
                    if ClosestIndex >= headIndex + 5 and (datetime.today() - headIndexDate).total_seconds() <= 45:
                        #do nothing
                        headIndex = headIndex
                    else:
                        headIndex = ClosestIndex
                        indexes_ins.remove({
                            'identifier': data['id'],
                            'processionPoint': 'head'
                        })
                        indexes_ins.insert({
                            'identifier': data['id'],
                            'index': headIndex,
                            'date': datetime.today(),
                            'processionPoint': 'head'
                        })

                distance = 200000000
                ClosestIndex = 0
                for i in range(headIndex + 1):
                    dt = geopy.distance.vincenty(tail, route['coordinates'][i]).km
                    if dt < distance:
                        ClosestIndex = i
                        distance = dt
                if allow_backtraking == True:
                    tailIndex = ClosestIndex
                if ClosestIndex > tailIndex:
                    if ClosestIndex >= tailIndex + 5 and (datetime.today() - tailIndexDate).total_seconds() <= 45:
                        #do nothing
                        tailIndex = tailIndex
                    else:
                        tailIndex = ClosestIndex
                        indexes_ins.remove({
                            'identifier': data['id'],
                            'processionPoint': 'tail'
                        })
                        indexes_ins.insert({
                            'identifier': data['id'],
                            'index': tailIndex,
                            'date': datetime.today(),
                            'processionPoint': 'tail'
                        })

                # minimum distance just in case
                #if headIndex - tailIndex < 6:
                #    tailIndex = tailIndex - 6
                #    if tailIndex < 0:
                #        tailIndex = 0





                # fill positions to update
                FinalHead = headIndex + 1
                if FinalHead > len(route['coordinates']):
                    FinalHead = headIndex

                posIns = []
                for i in range(tailIndex, FinalHead):
                    dt = datetime.today()
                    dtf = dt + timedelta(milliseconds=i)
                    posIns.append({
                        'identifier': data['id'],
                        'position': {
                            'lat': route['coordinates'][i][0],
                            'lng': route['coordinates'][i][1]
                        },
                        'date': dtf,
                        'processionPoint': 'head',
                        'index': i
                    })

                positionsAll = db.get_collection('processionPositions_ios')
                # delete old positions
                positionsAll.remove({
                    'identifier': data['id']
                })
                # insert new positions
                positionsAll.insert_many(posIns)

def endProcession(id):
    data = {
        "id": id
    }
    db = get_db()
    positionsAll = db.get_collection('processionPositions')
    positions = db.get_collection('processionPositions').find({'identifier': data['id']}).sort('date',
                                                                                               pymongo.ASCENDING)
    position_history = db.get_collection('procession_history')

    positionsTracker = db.get_collection('processionTrackerPositions')
    positionsTrackerIndexes = db.get_collection('processionTrackerIndexes')

    positionsAll.remove({
        'identifier': data['id']
    })

    positionsTracker.remove({
        'identifier': data['id']
    })

    positionsTrackerIndexes.remove({
        'identifier': data['id']
    })

    for position in positions:
        del position.id
        position['date'] = datetime.today()
        position_history.insert(position)

    # IOS

    positionsAll = db.get_collection('processionPositions_ios')
    positions = db.get_collection('processionPositions_ios').find({'identifier': data['id']}).sort('date',
                                                                                                   pymongo.ASCENDING)
    position_history = db.get_collection('procession_history_ios')

    positionsTracker = db.get_collection('processionTrackerPositions')
    positionsTrackerIndexes = db.get_collection('processionTrackerIndexes_ios')

    positionsAll.remove({
        'identifier': data['id']
    })

    positionsTracker.remove({
        'identifier': data['id']
    })

    positionsTrackerIndexes.remove({
        'identifier': data['id']
    })

    for position in positions:
        del position.id
        position['date'] = datetime.today()
        position_history.insert(position)