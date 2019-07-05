class ErrorStatus:
    def __init__(self, error_code, message):
        self.error_code = error_code
        self.message = message

    def __str__(self):
        return str(self.__dict__)
