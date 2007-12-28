#
# $Log: server_config.py,v $
# Revision 1.4  2007/12/08 23:02:25  streapy
# Login
#
# Revision 1.3  2007/12/08 22:06:22  streapy
# reload and restart the server
#
# Revision 1.2  2007/11/25 17:36:14  streapy
# Benutzer hinzufuegen/Bearbeiten
#
# Revision 1.1  2007/11/25 05:37:48  streapy
# Initial Import
# Design, Menue, Server-Konfiguration, Datenbankklasse
#
#

from snakeserver.snakelet import Snakelet

import sqlite3, os, sys


try:
    sys.path.append(os.getcwd().rstrip("snakelets_webserver/Snakelets-1.44"))
    import xml_api.xmlapi_client as xmlapi_client
except:
    print "Could not import the xmlapi"


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

class ServerConfig(Snakelet):
    def init(self):
        pass
    
    def serve(self, request, response):  
        rctx=request.getContext()
        

        rctx.error_messages = []
        rctx.success_messages = []
        sess = request.getSessionContext()
        try:
            a = sess.zugriff
        except:
            self.redirect('index.y',request,response)           
        
        try:
            f=request.getForm()
            akt = f.get("akt")
            action = f.get("action")

        except:
            action = ""
        
        if akt == "change_server_details":
            valid_error = False
            if action == "update":
                try:
                    server_ip=escapeString(f.get('server_ip',''))
                    server_port=escapeString(f.get('server_port',''))
                    server_docroot=escapeString(f.get('server_docroot',''))
                    max_connections=escapeString(f.get('max_connections',''))
                    max_bandwith=escapeString(f.get('max_bandwith',''))
                except:
                    valid_error = True
                
                
                
                if valid_error == False:
                    if server_ip == "" or server_port == "" or server_docroot == "" or max_connections == "" or max_bandwith == "":
                        rctx.error_messages += ["Es wurden nicht alle Felder ausgefuellt"]
                    else:
                        qry_update = "UPDATE server_config SET server_ip = '%s', server_port='%s', server_docroot='%s', max_connections='%s', max_bandwith='%s'"  %(server_ip, server_port, server_docroot, max_connections, max_bandwith)
                        dbcon = DBConnect() 
                        myconn, cursor = dbcon.connect_db()
                        cursor.execute(qry_update) 
                        rctx.success_messages += ["Die Server-Konfiguration wurde geaendert"]
                        cursor.close()                
                        myconn.close()                     
            
            self.getServerConfig(request, request)
            
            self.redirect('server_config.y',request,response)
        
        elif akt == "restart_server":
            # Server-Infos auslesen
            info = self.getServerConfig(request, response)
 
            try:
                api_obj = xmlapi_client.XMLApiClient(sess.username, sess.passwort, rctx.server_ip, int(rctx.server_port))
                api_obj.doServerRestart()
                rctx.message = "Der Server wurde neu gestartet."
            except:
                rctx.message = "Der Server scheint nicht zu laufen."
            self.redirect('show_message.y',request,response)     
            
        elif akt == "reload_shares":
            # Server-Infos auslesen
            info = self.getServerConfig(request, response)
 
            try:
                api_obj = xmlapi_client.XMLApiClient(sess.username, sess.passwort, rctx.server_ip, int(rctx.server_port))
                api_obj.reloadShares()
                rctx.message = "Die Freigaben wurden neu geladen"
            except:
                rctx.message = "Der Server scheint nicht zu laufen."
            
            self.redirect('show_message.y',request,response)             

    def getServerConfig(self, request, response):
        
        rctx=request.getContext()
        rctx.server_ip = ""
        rctx.server_port = ""
        rctx.server_docroot = ""
        rctx.max_connections = ""
        rctx.max_bandwith = ""

        
        qry_server_config = "SELECT * FROM server_config"  
        dbcon = DBConnect() 
        myconn, cursor = dbcon.connect_db()
        cursor.execute(qry_server_config) 
        config = cursor.fetchone()  

        
        rctx.server_ip =  str(config[0])
        rctx.server_port = str(config[1])
        rctx.server_docroot =  str(config[2])
        rctx.max_connections = str(config[3])
        rctx.max_bandwith =  str(config[4])  
        

        cursor.close()                
        myconn.close()  
            
        