__author__ = '0100849'
from hashlib import sha256
import requests
from requests.auth import HTTPBasicAuth

USER = 'webapp'
PASSWORD = 'tabuleiros_web_2015'
MOBILE_TEST = 'http://localhost:8989/mobile/events'
WEB_TEST = 'http://localhost:8989/web/page'
SECRET_KEY = 'tabfest#?2015'


def generate_key(key):
    return sha256(b'{}'.format(key)).hexdigest() + \
           sha256(b'{}'.format(SECRET_KEY)).hexdigest()


def do_main():
    r = requests.get(WEB_TEST, auth=HTTPBasicAuth(USER, generate_key(PASSWORD)))
    if r.status_code is not 200:
        raise Exception('invalid response')
    else:
        print('job done')
    return


do_main()