#
# $Log: group_administration.py,v $
# Revision 1.2  2007/12/08 23:02:25  streapy
# Login
#
# Revision 1.1  2007/12/01 04:02:49  streapy
# Verzeichnis-Freigaben und Gruppenverwaltung
#
#
#
#

from snakeserver.snakelet import Snakelet

import sqlite3, random, md5

from function import  *

class GroupAdministration(Snakelet):
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

            send=escapeString(f.get('senden',''))
                
            if send == "true":   
                valid_error = False
                try:
                    groupname=escapeString(f.get('groupname',''))
                except:
                    valid_error = True   
                    
                if groupname == "":
                    valid_error = True
                    rctx.error_messages += ["Es wurden nicht alle Felder ausgefuellt."]
                    
                # Pruefen, ob es den Benutzernamen schon gibt
                qry = "SELECT id FROM groups WHERE groupname = '%s'" %(groupname)
                cursor.execute(qry) 
                check_group = cursor.fetchone() 
                if  check_group != None:
                    valid_error = True
                    rctx.error_messages += ["Es gibt bereits einen Benutzer mit diesem Namen."]
                 
                    
                if valid_error == False:


                    # Benutzer in die Datenbank schreiben
                    qry = "INSERT INTO groups (groupname) VALUES('%s')"  %(groupname)
                    cursor.execute(qry) 
                    rctx.success_messages += ["Der Benutzer wurde hinzgefuegt."]


            cursor.close()                
            myconn.close()              
            self.redirect('group_add.y',request,response)
            
        elif action == "change":
            # Benutzer auslesen
            qry = "SELECT * FROM groups ORDER by groupname ASC"
            cursor.execute(qry) 
            rctx.group = cursor.fetchall()  
        

            cursor.close()                
            myconn.close()     
            self.redirect('group_change.y',request,response)     

        elif action == "delete":
            groupid=escapeString(f.get('groupid',''))
            qry = "DELETE FROM groups WHERE id = '%s'" %(groupid)
            cursor.execute(qry) 

        

            cursor.close()                
            myconn.close()     
            rctx.message = "Die Gruppe wurde geloescht."
            self.redirect('show_message.y',request,response)  
            
        elif action == "ajax_change_group":

            groupid=escapeString(f.get('groupid','a'))

            qry = "SELECT groupname FROM groups WHERE id = '%s'" %(int(groupid))
            cursor.execute(qry) 
            result = cursor.fetchone()  
            rctx.groupname = str(result[0])
            rctx.groupid = groupid
            
            cursor.close()                
            myconn.close()     

            self.redirect('ajax_group_change.y',request,response)       
        elif action == "change_group_change":
            
            groupname=escapeString(f.get('groupname','')) 
            groupid=escapeString(f.get('groupid',''))       
            
            # Pruefen, ob es den Benutzernamen bereits gibt
            qry = "SELECT id FROM groups WHERE groupname = '%s' and id != '%s'" %(groupname, groupid)
            cursor.execute(qry) 
            result = cursor.fetchone()    
            if result != None:
                rctx.message = "Es gibt bereits eine Gruppe mit diesen Namen!"
                self.redirect('show_message.y',request,response)  
                return
                        

            qry= "UPDATE groups SET groupname = '%s' WHERE id = '%s'" %(groupname, groupid)
            print qry
            cursor.execute(qry) 
            
            rctx.message = "Die Gruppe wurd bearbeitet"
            
            cursor.close()                
            myconn.close()              

            self.redirect('show_message.y',request,response)                          
        else:
            cursor.close()                
            myconn.close()              
            self.redirect('index.y',request,response)
        