#
# $Log: share_file_administration.py,v $
# Revision 1.3  2007/12/08 23:51:20  streapy
# -
#
# Revision 1.2  2007/12/08 23:02:25  streapy
# Login
#
# Revision 1.1  2007/12/08 15:02:54  streapy
# Datei-Freigaben implementiert
#
#

from snakeserver.snakelet import Snakelet

import sqlite3, random, md5

from function import  *

class ShareFileAdministration(Snakelet):
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
        
        if action == "addFileShare":      
            # Alle Benutzer auslesen
            qry = "SELECT id, username FROM users ORDER BY username ASC"
            cursor.execute(qry) 
            rctx.user = cursor.fetchall()              
            
            # Alle Gruppen auslesen    
            qry = "SELECT id, groupname FROM groups ORDER BY groupname ASC"
            cursor.execute(qry) 
            rctx.groups = cursor.fetchall()                 

            send=escapeString(f.get('senden',''))
                
            if send == "true":   
                 filename=escapeString(f.get('filename',''))
                 benutzer=escapeString(f.get('benutzer',''))
                 gruppen=escapeString(f.get('gruppen',''))
                 
                 if filename == "":
                    rctx.error_messages += ["Es wurde nicht alle Felder ausgefuellt"]            

                 # Gucken ob es schon eine Freigabe fuer das Verzeichnis gibt
                 qry = "SELECT filename FROM shared_files WHERE filename = '%s'" %(filename)
                 cursor.execute(qry) 
                 res = cursor.fetchone()  
                 if res == None:
                    # Wenn nicht, hinzufuegen
                    qry = "INSERT INTO shared_files (filename) VALUES('%s')" %(filename)
                    cursor.execute(qry) 
                 else:
                     # Sonst Fehlermeldung
                     rctx.error_messages += ["Es gibt bereits eine Freigabe fuer diese Datei"] 

                 # ID des Folders auslesen
                 qry = "SELECT id FROM shared_files WHERE filename = '%s'" %(filename)
                 cursor.execute(qry) 
                 folderid = cursor.fetchone()[0]
                 
                 for user in benutzer:
                     qry = "INSERT INTO urights_files (user_id, file_id) VALUES('%s', '%s')" %(user, folderid) 
                     cursor.execute(qry) 
                     
                 for group in gruppen:
                     qry = "INSERT INTO grights_files (group_id, file_id) VALUES('%s', '%s')" %(group, folderid) 
                     cursor.execute(qry)                      

            cursor.close()                
            myconn.close()              
            
            self.redirect('share_file_add.y',request,response)

        elif action == "changeFileShare":     
            # Freigaben auslesen
            qry = "SELECT id, filename FROM shared_files"
            cursor.execute(qry) 
            rctx.freigabe = cursor.fetchall() 
            
            send=escapeString(f.get('senden',''))
                
            if send == "true":  
                 freigabe=escapeString(f.get('freigabe',''))
                 benutzer=escapeString(f.get('benutzer',''))
                 gruppen=escapeString(f.get('gruppen',''))   
                 folderid=escapeString(f.get('folderid',''))  

                 # Allte alten Freigabe-User-Beziehungen loeschen
                 # und
                 # Alle alten Freigabe-Group-Beziehungen loeschen 
                 qry = "DELETE FROM urights_files WHERE file_id = '%s'" %(folderid)
                 cursor.execute(qry) 

                 qry = "DELETE FROM grights_files WHERE file_id = '%s'" %(folderid) 
                 cursor.execute(qry) 
                 
                 # Neue Beziehungen hinzufuegen
                 if type(benutzer) == str:
                     benutzer = ([benutzer])                  

                 for user in benutzer:
                     qry = "INSERT INTO urights_files (user_id, file_id) VALUES('%s', '%s')" %(user, folderid)
                     cursor.execute(qry) 

                 if type(benutzer) == str:
                     gruppen = ([gruppen])                  
                  
                 for group in gruppen:
                     qry = "INSERT INTO grights_files (group_id, file_id) VALUES('%s', '%s')" %(group, folderid)
                     cursor.execute(qry)                    


                 # Namen updaten
                 qry = "UPDATE shared_files set filename = '%s' WHERE id = '%s'" %(freigabe, folderid) 
                 cursor.execute(qry)  
                 
                 cursor.close()                
                 myconn.close()                  
                  
            self.redirect('share_file_change.y',request,response)   
        
        elif action == "ajax_change_fileshare":

            # Name auslesen
            folderid = escapeString(f.get('folderid',''))
            rctx.folderid = folderid
            qry = "SELECT filename FROM shared_files WHERE id = '%s'" %(folderid)
            cursor.execute(qry) 
            rctx.freigabe = cursor.fetchone()[0]             
    
            # Alle Benutzer auslesen
            qry = "SELECT id, username FROM users ORDER BY username ASC"
            cursor.execute(qry) 
            rctx.user = cursor.fetchall()     
            print rctx.user        
            
            # Alle Gruppen auslesen    
            qry = "SELECT id, groupname FROM groups ORDER BY groupname ASC"
            cursor.execute(qry) 
            rctx.groups = cursor.fetchall()   
            print rctx.groups
            
            # auslesen, der benutzer-verzeichnis-freigaben fuer dieses verzeichnis
            qry = "SELECT user_id FROM urights_files WHERE file_id = '%s'" %(folderid) 
            cursor.execute(qry) 
            rctx.user_has_share = cursor.fetchall() 
            print rctx.user_has_share     
            
            # das gleiche fuer Gruppen
            qry = "SELECT group_id FROM grights_files WHERE file_id = '%s'" %(folderid) 
            cursor.execute(qry) 
            rctx.group_has_share = cursor.fetchall()   
            
            print rctx.group_has_share           
        
            cursor.close()                
            myconn.close()     
       
            self.redirect('ajax_change_fileshare.y',request,response)              
                  
        elif action == "delete_file_share":
            file_id = escapeString(f.get('file',''))
            qry = "DELETE FROM urights_files WHERE file_id = '%s'" %(file_id)
            qry2 = "DELETE FROM shared_files WHERE id = '%s'" %(file_id)
            cursor.execute(qry) 
            cursor.execute(qry2) 

            cursor.close()                
            myconn.close()                
            
            rctx.message = "Die Freigabe wurde geloescht."
            self.redirect('show_message.y',request,response) 
            
         
        else:
            cursor.close()                
            myconn.close()              
            self.redirect('index.y',request,response)
        