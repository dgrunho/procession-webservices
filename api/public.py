import cherrypy


class PublicServices:
    def __init__(self):
        return

    @staticmethod
    @cherrypy.expose
    def index():
        return "Welcome to smarterfest Services!"
