#
# $Log: user_administration.py,v $
# Revision 1.7  2007/12/08 23:21:25  streapy
# -
#
# Revision 1.6  2007/12/08 23:02:25  streapy
# Login
#
# Revision 1.5  2007/12/01 04:02:49  streapy
# Verzeichnis-Freigaben und Gruppenverwaltung
#
# Revision 1.4  2007/11/30 18:53:45  streapy
# ajax angefangen
#
# Revision 1.3  2007/11/30 18:03:05  jeldrik
# md5.digest -> md5.hexdigest()
#
# Revision 1.2  2007/11/30 17:46:23  streapy
# Tobi darf das Skript Jelles Wuenschen entsprechend anpassen
#
# Revision 1.1  2007/11/25 17:36:14  streapy
# Benutzer hinzufuegen/Bearbeiten
#
#
#

from snakeserver.snakelet import Snakelet

import sqlite3, random, md5

from function import  *

class UserAdministration(Snakelet):
    def init(self):
        pass
    
    def serve(self, request, response):  
        dbcon = DBConnect() 
        myconn, cursor = dbcon.connect_db()
        
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

            action = f.get("action")

        except:
            action = ""
        
        if action == "add":          

            # moegliche Gruppen auslesen
            qry = "SELECT id, groupname FROM groups"
            cursor.execute(qry) 
            rctx.groups = cursor.fetchall() 

            

            send=escapeString(f.get('senden',''))
                
            if send == "true":   
                valid_error = False
                try:
                    username=escapeString(f.get('username',''))
                    pass1=escapeString(f.get('pass1',''))
                    pass2=escapeString(f.get('pass2',''))
                    gruppen = f.get('gruppen','')

                except:
                    valid_error = True   
                    
                if username == ""  or pass1 == "" or pass2 == "":
                    valid_error = True
                    rctx.error_messages += ["Es wurden nicht alle Felder ausgefuellt."]
                if pass1 != pass2:
                    valid_error = True
                    rctx.error_messages += ["Die eingegebenen Passwoerter stimmen nicht ueberein."]
                # Pruefen, ob es den Benutzernamen schon gibt
                qry = "SELECT id FROM users WHERE username = '%s'" %(username)
                cursor.execute(qry) 
                check_user = cursor.fetchone() 
                if  check_user != None:
                    valid_error = True
                    rctx.error_messages += ["Es gibt bereits einen Benutzer mit diesem Namen."]
                 
                    
                if valid_error == False:
                    # Salt berechnen
                    salt = random.randint(0,999999999)
                    pw_konk = pass1 + str(salt)
                    m = md5.new()
                    m.update(pw_konk)
                    pw_md5 = m.hexdigest()
                    pw_md5 = str(pw_md5)

                    # Benutzer in die Datenbank schreiben
                    qry = "INSERT INTO users (username, password, salt) VALUES('%s', '%s', '%s')"  %(username, pw_md5, salt)
                    cursor.execute(qry) 

                    
                    
                    # User-ID auslesen
                    qry = "SELECT id FROM users WHERE username = '%s'"  %(username)
                    cursor.execute(qry) 
                    userid = cursor.fetchone()[0]

                    
                    for gruppe in gruppen:
                        # User zu gruppen hinzufuegen
                        qry = "INSERT INTO user_groups (user_id, group_id) VALUES ('%s', '%s')" %(userid, gruppe)
                        cursor.execute(qry) 
                    
                    rctx.success_messages += ["Der Benutzer wurde hinzgefuegt."]


            cursor.close()                
            myconn.close()              
            
            self.redirect('user_add.y',request,response)

        elif action == "delete":
            userid=escapeString(f.get('userid',''))
            qry = "DELETE FROM users WHERE id = '%s'" %(userid)
            cursor.execute(qry) 

            cursor.close()                
            myconn.close()     
            rctx.message = "Der Benutzer wurde geloescht."
            self.redirect('show_message.y',request,response)  
            
        elif action == "change":
            # Benutzer auslesen
            qry = "SELECT * FROM users ORDER by username ASC"
            cursor.execute(qry) 
            rctx.user = cursor.fetchall()  
        

            cursor.close()                
            myconn.close()     
            self.redirect('user_change.y',request,response)     
        elif action == "ajax_change_user":

            userid=escapeString(f.get('userid','a'))

            qry = "SELECT username, admin FROM users WHERE id = '%s'" %(int(userid))
            cursor.execute(qry) 
            result = cursor.fetchone()  
            rctx.username = str(result[0])
            rctx.userid = userid
            if result[1] == 1:
                rctx.admin_check = ' checked="checked" '
            
            # gruppen auslesen
            qry = "SELECT id, groupname FROM groups"
            cursor.execute(qry) 
            rctx.groups = cursor.fetchall()          
            
            
            # auslesen in welchen gruppen der user ist
            qry = "SElECT group_id FROM user_groups WHERE user_id = '%s'" %(userid)
            cursor.execute(qry) 
            rctx.usergroups = cursor.fetchall()   
             

            cursor.close()                
            myconn.close()     


           
            self.redirect('ajax_user_change.y',request,response)       
        elif action == "change_user_change":
            
            username=escapeString(f.get('username',''))
            pass1=escapeString(f.get('pass1',''))
            pass2=escapeString(f.get('pass2',''))     
            userid=escapeString(f.get('userid',''))   
            admin = escapeString(f.get('admin','0'))   

            gruppen = f.get('gruppen','')    
            
            
            # Pruefen, ob es den Benutzernamen bereits gibt
            qry = "SELECT id FROM users WHERE username = '%s' and id != '%s'" %(username, userid)
            cursor.execute(qry) 
            result = cursor.fetchone()    
            if result != None:
                rctx.message = "Es gibt bereits einen Benutzer mit diesen Namen!"
                self.redirect('show_message.y',request,response)  
                return
                        
    
            if pass1 != "" and pass2 != "" and pass1 == pass2:
                # Salt berechnen
                salt = random.randint(0,999999999)
                pw_konk = pass1 + str(salt)
                m = md5.new()
                m.update(pw_konk)
                pw_md5 = m.hexdigest()
                pw_md5 = str(pw_md5)                
                
                qry= "UPDATE users SET admin = '%s', username = '%s', password = '%s', salt = '%s' WHERE id = '%s'" %(admin, username, pw_md5, salt, userid)
            
            else:
                qry= "UPDATE users SET admin = '%s', username = '%s' WHERE id = '%s'" %(admin, username, userid)
            
            # Benutzer updated
            cursor.execute(qry) 
            
            # Alle Gruppenbeteiligungen loeschen
            qry = "DELETE FROM user_groups WHERE user_id = '%s'" %(userid)
            cursor.execute(qry) 
            
            # Benutzer zu den Gruppen hinzufuegen
            
            for gruppe in gruppen:
                # Pruefen, ob der Benutzer schon in der Gruppe ist
                qry_add = "INSERT INTO user_groups (user_id, group_id) VALUES('%s', '%s')" %(userid, gruppe)
                cursor.execute(qry_add) 
            
            rctx.message = "Der Benutzer wurde bearbeitet"
            
            cursor.close()                
            myconn.close()              


           
            self.redirect('show_message.y',request,response)                          
        else:
            cursor.close()                
            myconn.close()              
            self.redirect('index.y',request,response)
        