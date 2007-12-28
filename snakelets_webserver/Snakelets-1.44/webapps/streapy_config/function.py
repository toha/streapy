import sqlite3

class DBConnect(object):
    def __init__(self):
        self.__myconn = None
        self.__cursor = None
        


    def connect_db(self):
        try:
            self.__myconn = sqlite3.connect("../../db/streapy_db", isolation_level = None)
            self.__cursor = self.__myconn.cursor()             
        except:
            print "EXCEPTION WERFEN"
    
        return self.__myconn, self.__cursor

def escapeString(s):
    return s