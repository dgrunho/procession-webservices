__author__ = '0100849'


class Parking:
    def __init__(self, coordinates, allocation, park_id=None):
        self.id = str(park_id)
        self.coordinates = coordinates
        self.allocation = allocation

    def __str__(self):
        return str(self.__dict__)