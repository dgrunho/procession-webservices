import json
import logging
import os
import ssl
from collections import Counter

import pymongo

_log = logging.getLogger(__name__)


def _get_mongo_uri():
    vcap_config = os.environ.get('VCAP_SERVICES')

    if os.getenv('SMARTERFEST_MONGO'):
        _log.info("A usar a BD definida em $SMARTERFEST_MONGO")
        return os.environ.get('SMARTERFEST_MONGO')  # 'mongodb://localhost/smarterfestdb'

    if vcap_config is not None:
        _log.info("A procurar em $VCAP_SERVICES")

        decoded_config = json.loads(vcap_config) or {}

        mongo_creds = {}

        for key, value in decoded_config.iteritems():
            if key.startswith('mongodb'):
                _log.info("Obtida a configuração do $VCAP_SERVICES")
                mongo_creds = decoded_config[key][0]['credentials']

        return str(mongo_creds['url'])

    raise ValueError('Não foi possivel encontrar a ligação a base de dados')


_mongo_uri = _get_mongo_uri()


def get_db():
    client = pymongo.MongoClient(_mongo_uri, ssl_cert_reqs=ssl.CERT_NONE)

    client['admin'].command('connectionStatus', {'showPrivileges': False})

    return client.get_database()


def save_to_mongo(structure, collection_name):
    # open connection to mongo
    db = get_db()

    if type(structure) is dict:
        db[collection_name].insert_one(structure)
        return
    for item in structure:
        if type(item) == dict:
            keys = item.keys()
            entry = Counter({})
            for key in keys:
                entry += Counter({key: item[key]})
            # insert new registry with :entry{import_date, filename, state}
            db[collection_name].insert_one(entry)
