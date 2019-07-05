import os
import cherrypy
import api.services as services
import json

from pymongo import MongoClient

# class RootServer:
#     @cherrypy.expose
#     def index(self):
#         return """This is the default public SmarterFest Web Services!"""
#
#
# def CORS():
#     # cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
#     cherrypy.response.headers["Access-Control-Allow-Origin"] = "http://smarterfest.eu-gb.mybluemix.net"
#     cherrypy.response.headers["Access-Control-Allow-Methods"] = "POST, GET, DELETE, PUT"
#     cherrypy.response.headers["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
#
# if __name__ == '__main__':
#
#
#     # Get host/port from the Bluemix environment, or default to local
#     HOST_NAME = os.getenv('VCAP_APP_HOST', '127.0.0.1')
#     PORT_NUMBER = int(os.getenv('VCAP_APP_PORT', '9999'))
#     cherrypy.config.update({
#             'server.socket_host': HOST_NAME,
#             'server.socket_port': PORT_NUMBER,
#     })
#
#     # Start the server
#     print("Listening on %s:%d" % (HOST_NAME, PORT_NUMBER))
#
#     #Get the connection credentials from VCAP variables
#     vcap_config = os.environ.get('VCAP_SERVICES')
#     decoded_config = json.loads(vcap_config)
#     for key, value in decoded_config.iteritems():
#          if key.startswith('mongodb'):
#              mongo_creds = decoded_config[key][0]['credentials']
#     mongo_url = str(mongo_creds['url'])
#
#     client = MongoClient(mongo_url)
#
#     #client.db.processionPositions.insert_one({'ola': 'mundo'})
#
#     print client
#
#     print client.db.collection_names()
#
#     print client.db.processionPoints.find()
#
#     print os.path.abspath(os.path.join(os.getcwd(), '/webapp/js'))
#
#     #root = RootServer()
#     root = services.SmarterServices()
#     cherrypy.tools.CORS = cherrypy.Tool('before_finalize', CORS)
#     cherrypy.quickstart(root, '/', services.conf)
#

services.do_main()

