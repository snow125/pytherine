__author__ = 'root'

class DBNotFoundException(Exception):

    def __init__(self,message='DB not found'):
        self.message = message

    def __str__(self):
        if not (isinstance(self.message, str) or isinstance(self.message, unicode)):
            self.message='DB not found'
        return self.message

class DBNotExistException(Exception):

    def __init__(self,message='DB not exist'):
        self.message = message

    def __str__(self):
        if not (isinstance(self.message, str) or isinstance(self.message, unicode)):
            self.message='DB not exist'
        return self.message