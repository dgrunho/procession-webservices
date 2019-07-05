#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = '0100849'

import json
import logging
import multiprocessing
import os

import cherrypy

from api.mobileservices import MobileServices
from api.public import PublicServices
from api.webservices import WebServices

_log = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))

USERS = json.loads(
    os.getenv(
        'SMARTERFEST_USERS',
        '{"WEB": {"webapp": "tabuleiros_web_2015"}, "MOBILE": {"mobile": "mobile_tabuleiros_2015"}}'
    )
)

PROCESSIONS = ['rapazes', 'tabuleiros', 'mordomo', 'bodo', 'parciais']


def CORS():
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    cherrypy.response.headers["Access-Control-Allow-Headers"] = "Content-Type"


def parse_text(text):
    # from hashlib import sha256
    # text_without_secret = text[:-len(sha256(SECRET_KEY).hexdigest())]
    #
    # is_mobile = text_without_secret == sha256(USERS['MOBILE']['mobile']).hexdigest()
    # is_web = text_without_secret == sha256(USERS['WEB']['webapp']).hexdigest()
    #
    # if is_mobile:
    #     return USERS['MOBILE']['mobile']
    # elif is_web:
    #     return USERS['WEB']['webapp']
    # return None
    return text


def validate_password(realm, username, password):
    realm_users = {}

    if realm == 'Aplicação Web':
        realm_users = USERS["WEB"]

    if realm == 'ServicosMobile':
        realm_users = USERS["MOBILE"]

    return username in realm_users and realm_users[username] == password


# endregion

# region cherrypy config


conf = {
    '/': {
        'tools.response_headers.headers': [('Access-Control-Allow-Origin', '*')],
        'tools.CORS.on': True,
        'tools.log_headers.on': False,
        'request.show_tracebacks': False,
        'request.show_mismatched_params': False,
        'log.screen': False,
    },
    '/web': {
        'tools.auth_basic.on': True,
        'tools.auth_basic.realm': u'Aplicação Web',
        'tools.auth_basic.checkpassword': validate_password,
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.path.join(current_dir, '../webapp'),
        'tools.staticdir.index': "index.html"
    },

    '/mobile': {
        'tools.auth_basic.on': True,
        'tools.auth_basic.realm': 'ServicosMobile',
        'tools.auth_basic.checkpassword': validate_password,
    },

    '/css': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.path.join(current_dir, '../webapp', 'css')
    },

    '/img': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.path.join(current_dir, '../webapp', 'img')
    },

    '/images': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.path.join(current_dir, '../static/', 'images')
    },

    '/js': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.path.join(current_dir, '../webapp', 'js')
    },

}


# endregion


def do_main():
    logging.basicConfig(level=getattr(logging, os.getenv('SMARTERFEST_LOG_LEVEL', 'INFO')))

    host_name = os.getenv('VCAP_APP_HOST', '127.0.0.1')
    port_number = int(os.getenv('VCAP_APP_PORT', '9999'))

    num_workers = int(os.getenv('SMARTERFEST_NUM_WORKERS', multiprocessing.cpu_count() * 16))

    _log.info("Num workers: %s", num_workers)

    cherrypy.config.update({
        'server.socket_host': host_name,
        'server.socket_port': port_number,
        'server.thread_pool': num_workers,
        'engine.autoreload_on': False,
        'checker.on': False,
    })

    cherrypy.tools.CORS = cherrypy.Tool('before_finalize', CORS)

    # seeder.do_main()
    root = PublicServices()
    root.web = WebServices()
    root.mobile = MobileServices()
    cherrypy.quickstart(root, '/', conf)


if __name__ == '__main__':
    do_main()
