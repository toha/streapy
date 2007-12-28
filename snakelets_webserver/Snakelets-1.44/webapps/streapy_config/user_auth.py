#
# $Log: user_auth.py,v $
# Revision 1.2  2007/12/09 00:07:04  streapy
# -
#
# Revision 1.1  2007/12/08 23:02:25  streapy
# Login
#

#
#

from snakeserver.snakelet import Snakelet

import sqlite3, os, sys, md5


try:
    sys.path.append(os.getcwd().rstrip("snakelets_webserver/Snakelets-1.44"))
    import xml_api.xmlapi_client as xmlapi_client
except:
    print "Could not import the xmlapi"


from function import  *

class userAuth(Snakelet):
    def init(self):
        pass
    
    def serve(self, request, response):  
        dbcon = DBConnect() 
        myconn, cursor = dbcon.connect_db()        
        rctx=request.getContext()
        sess = request.getSessionContext()

        rctx.error_messages = []
        rctx.success_messages = []
        
        try:
            f=request.getForm()
            akt = f.get("akt")

        except:
            akt = ""
        
        if akt == "login":
            valid_error = False

            try:
                username=escapeString(f.get('username',''))
                passwort=escapeString(f.get('passwort',''))
            except:
                valid_error = True
                
            if username == "" or passwort == "" or valid_error:
                rctx.error_messages += ["Es wurden nicht alle Felder ausgefuellt"]
                self.redirect('index.y',request,response)  
            else:
                # Pruefen, ob es den Benutzer gibt.
                qry = "SELECT * FROM users WHERE username = '%s' and admin = '1'"%(username)
                cursor.execute(qry) 
                user = cursor.fetchone()
                if user == None:
                    self.redirect('index.y',request,response)      
                else:
                    pw = user[2]
                    salt = user[3]
                    pw_konk = passwort + str(salt)

                    m = md5.new()
                    m.update(pw_konk)
                    pw_md5 = m.hexdigest()
                    pw_md5 = str(pw_md5)  
                    if pw != pw_md5:  
                        self.redirect('index.y',request,response)   
                    else:
                        # Zugriff
                        sess.zugriff = "yes"
                        sess.username = username
                        sess.passwort = passwort
                        rctx.message = "Herzlich Willkommen"
                        self.redirect('show_message.y',request,response) 
                
        
            
        
        
        
