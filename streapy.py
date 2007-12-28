#!/usr/bin/python
import server.server as server
import sqlite3
import time
while True:
    time.sleep(0.5)
    try:
        myconn = sqlite3.connect("db/streapy_db", isolation_level = None)
        cursor = myconn.cursor()
        qry = "SELECT * FROM server_config"
        cursor.execute(qry)
        config = cursor.fetchone()
        myserver = server.ConnectionManager(config[2] ,config[0], config[1], config[3], config[4])
        myserver.startServer()
    except KeyboardInterrupt:
        myserver.stopServer()
        break
    except Exception, e:
        print str(e).replace("'","")
        break
