#
# $Log: share_administration.py,v $
# Revision 1.4  2007/12/08 23:02:25  streapy
# Login
#
# Revision 1.3  2007/12/08 15:02:54  streapy
# Datei-Freigaben implementiert
#
# Revision 1.2  2007/12/01 04:12:44  streapy
# fehlerkorrektur beim aendern der gruppe
#
# Revision 1.1  2007/12/01 04:02:49  streapy
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

from snakeserver.snakelet import Snakelet

import sqlite3, random, md5

from function import  *

class ShareAdministration(Snakelet):
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
        
        if action == "addDirShare":      
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
                 dirname=escapeString(f.get('dirname',''))
                 if dirname.startswith('/'):
                  dirname [1:]
                 benutzer=escapeString(f.get('benutzer',''))
                 gruppen=escapeString(f.get('gruppen',''))
                 
                 if dirname == "":
                    rctx.error_messages += ["Es wurde nicht alle Felder ausgefuellt"]            

                 # Gucken ob es schon eine Freigabe fuer das Verzeichnis gibt
                 qry = "SELECT folder FROM shared_folders WHERE folder = '%s'" %(dirname)
                 cursor.execute(qry) 
                 res = cursor.fetchone()  
                 if res == None:
                    # Wenn nicht, hinzufuegen
                    qry = "INSERT INTO shared_folders (folder) VALUES('%s')" %(dirname)
                    cursor.execute(qry) 
                 else:
                     # Sonst Fehlermeldung
                     rctx.error_messages += ["Es gibt bereits eine Freigabe fuer dieses Verzeichnis"] 
                     self.redirect('share_dir_add.y',request,response)

                 # ID des Folders auslesen
                 qry = "SELECT id FROM shared_folders WHERE folder = '%s'" %(dirname)
                 cursor.execute(qry) 
                 folderid = cursor.fetchone()[0]
                 
                 for user in benutzer:
                     qry = "INSERT INTO urights_folder (user_id, folder_id) VALUES('%s', '%s')" %(user, folderid) 
                     cursor.execute(qry) 
                     
                 for group in gruppen:
                     qry = "INSERT INTO grights_folder (group_id, folder_id) VALUES('%s', '%s')" %(group, folderid) 
                     cursor.execute(qry)   
            
                 rctx.success_messages += ["Die Freigabe wurde hinzugefuegt"]               

            cursor.close()                
            myconn.close()              
            
            self.redirect('share_dir_add.y',request,response)

        elif action == "changeDirShare":     
            # Freigaben auslesen
            qry = "SELECT id, folder FROM shared_folders"
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
                 qry = "DElETE FROM urights_folder WHERE folder_id = '%s'" %(folderid)
                 cursor.execute(qry) 

                 qry = "DELETE FROM grights_folder WHERE folder_id = '%s'" %(folderid) 
                 cursor.execute(qry) 
                 
                 # Neue Beziehungen hinzufuegen
                 if type(benutzer) == str:
                     benutzer = ([benutzer])                  

                 for user in benutzer:
                     qry = "INSERT INTO urights_folder (user_id, folder_id) VALUES('%s', '%s')" %(user, folderid)
                     cursor.execute(qry) 

                 if type(benutzer) == str:
                     gruppen = ([gruppen])                  
                  
                 for group in gruppen:
                     qry = "INSERT INTO grights_folder (group_id, folder_id) VALUES('%s', '%s')" %(group, folderid)
                     cursor.execute(qry)         
                     
                 # Namen updaten
                 qry = "UPDATE shared_folders SET folder = '%s' WHERE id = '%s'" %(freigabe, folderid) 
                 cursor.execute(qry)  
                 
                 cursor.close()                
                 myconn.close()                                 

            self.redirect('share_dir_change.y',request,response)   
        
        elif action == "ajax_change_dirshare":

            # Name auslesen
            folderid = escapeString(f.get('folderid',''))
            rctx.folderid = folderid
            qry = "SELECT folder FROM shared_folders WHERE id = '%s'" %(folderid)
            cursor.execute(qry) 
            rctx.freigabe = cursor.fetchone()[0]             
    
            # Alle Benutzer auslesen
            qry = "SELECT id, username FROM users ORDER BY username ASC"
            cursor.execute(qry) 
            rctx.user = cursor.fetchall()              
            
            # Alle Gruppen auslesen    
            qry = "SELECT id, groupname FROM groups ORDER BY groupname ASC"
            cursor.execute(qry) 
            rctx.groups = cursor.fetchall()   
            
            # auslesen, der benutzer-verzeichnis-freigaben fuer dieses verzeichnis
            qry = "SELECT user_id FROM urights_folder WHERE folder_id = '%s'" %(folderid) 
            cursor.execute(qry) 
            rctx.user_has_share = cursor.fetchall()      
            
            # das gleiche fuer Gruppen
            qry = "SELECT group_id FROM grights_folder WHERE folder_id = '%s'" %(folderid) 
            cursor.execute(qry) 
            rctx.group_has_share = cursor.fetchall()              
        
            cursor.close()                
            myconn.close()     
       
            self.redirect('ajax_change_dirshare.y',request,response)              

        elif action == "delete_dir_share":
            file_id = escapeString(f.get('dir',''))
            qry = "DELETE FROM urights_folder WHERE folder_id = '%s'" %(file_id)
            qry2 = "DELETE FROM shared_folders WHERE id = '%s'" %(file_id)
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
        