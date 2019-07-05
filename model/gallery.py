__author__ = '0100849'


class Gallery():
    def __init__(self, urls):
        self.urls = urls

    def __str__(self):
        return str(self.__dict__)