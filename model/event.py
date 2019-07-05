__author__ = '0100849'


class Event:
    def __init__(self, name, time, duration, coordinates):
        self.name = name
        self.time = time
        self.duration = duration
        self.coordinates = coordinates

    def __str__(self):
        return str(self.__dict__)