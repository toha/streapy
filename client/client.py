# -*- coding: iso-8859-15 -*- 
# $Log: client.py,v $
# Revision 1.4  2007/12/08 23:51:41  streapy
# test
#
# Revision 1.3  2007/12/08 23:12:53  streapy
# -
#
# Revision 1.2  2007/12/08 21:42:56  streapy
# -
#

import wx,sys, os, re
import xml.dom.minidom

import xmlapi_client as xmlapi_client

ID_FRAME = wx.NewId()


class LogFrame(wx.Frame):

    def __init__(self):    

        wx.Frame.__init__(self, None, ID_FRAME, 'StreaPy Client', wx.DefaultPosition, wx.Size(220, 600),
                        style = wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.CLOSE_BOX |wx.SYSTEM_MENU | wx.CAPTION)        
        
        self.__treectrl = wx.TreeCtrl(self, id = -1, style = wx.TR_DEFAULT_STYLE)
        self.root = self.__treectrl.AddRoot("Freigaben")
        self.__treectrl.Bind(wx.EVT_LEFT_DCLICK, self.onDoubeClick)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.__treectrl)
        
        self.tree_akt_element = None
        
        
        bla = LoginDialog(self)
        bla.ShowModal()
    

    def OnSelChanged(self, event):
        el = event.GetItem() 
        text = self.__treectrl.GetItemText(el)  
        try:
            # ID Extrahieren
            r = re.compile("\((\d+)\)")
            self.tree_akt_element = int(r.findall(text)[0])
        except:
            self.tree_akt_element = None    
        
          

    def onDoubeClick(self, event):
        if self.tree_akt_element == None:
            #self.showDialog("Der Link fuer diese Datei konnte nicht ermittelt werden.")
            return
        link_xml = self.api_obj.getFileLink(self.tree_akt_element)
        if self.testingIfResponseIsErrorMessage(link_xml)[0] == True:
            self.showDialog("Der Server hat folgenden Fehler gesendet: %s" %(self.testingIfResponseIsErrorMessage(link_xml)[1]))   
            return
        
        fehler = False
        #Link Extrahieren
        try:
            dom  = xml.dom.minidom.parseString(link_xml)
            req = dom.getElementsByTagName("stxmlapires")[0]
            linkhash = req.childNodes[0].firstChild.wholeText
        except:
            self.showDialog("Der Link fuer diese Datei konnte nicht ermittelt werden.")
            fehler = True
            
            
        if not fehler:
            link = "http://%s:%s/%s" %(self.api_obj.getServerIP(), self.api_obj.getPort(), linkhash)
        
            # Link im Mediaplayer aufrufen
            os.system("%s %s" %(self.mediaplayer,link))
        
        
    def testingIfResponseIsErrorMessage(self, response):
        try:
            dom  = xml.dom.minidom.parseString(response)
            req = dom.getElementsByTagName("stxmlapires")[0]
            name =  req.childNodes[0].nodeName
            if name == "error":
                return True, req.childNodes[0].firstChild.wholeText  
            else:
                return False, ""
        except:
            return True, "No Error-Message"     
        
    def getFiles(self):
        try:
            files_xml = self.api_obj.getFileList()
        except:
            self.showDialog("Verbindung zum Server fehlgeschlagen. Benutzername/Passwort falsch?!")
        if self.testingIfResponseIsErrorMessage(files_xml)[0] == True:
            self.showDialog("Der Server hat folgenden Fehler gesendet: %s" %(self.testingIfResponseIsErrorMessage(files_xml)[1]))    
            return
        try:
            
            dom    = xml.dom.minidom.parseString(files_xml)
            
            req = dom.getElementsByTagName("stxmlapires")[0]
            for folder in req.childNodes:
                #and subitems
                folder_name = folder.getAttribute("name").rstrip('/')
                if folder_name == "":
                    folder_tree = self.__treectrl.AppendItem(self.root, "Nicht Zugeordnet")
                    for datei in folder.childNodes:
                        datei_name = datei.getAttribute("name")
                        datei_id = datei.getAttribute("id")
                        self.__treectrl.AppendItem(folder_tree, "%s (%s)" %(datei_name, datei_id))
                else:
                    folder_tree = self.__treectrl.AppendItem(self.root, folder_name)
                    # Dateien auslesen
                    for datei in folder.childNodes:
                        datei_name = datei.getAttribute("name")
                        datei_id = datei.getAttribute("id")
                        self.__treectrl.AppendItem(folder_tree, "%s (%s)" %(datei_name, datei_id))
        except:
            self.showDialog("Es konnte keine Verbindung zum Server hergestellt werden")
                    
    def showDialog(self, msg):
            dlg = wx.MessageDialog(self, msg,'Fehler',wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()        


class LoginDialog(wx.Dialog):
    def __init__(self, parent, ID=-1, title="Verbinden", size=wx.Size(285,250), pos=wx.DefaultPosition, style=wx.DEFAULT_DIALOG_STYLE):
        wx.Dialog.__init__(self, parent, ID, title, wx.DefaultPosition, size, style = style)
        self.parent = parent
        
        wx.StaticText(self, -1, "IP/Port", pos=wx.Point(10,20))
        wx.StaticText(self, -1, "Benutzername", pos=wx.Point(10,60))
        wx.StaticText(self, -1, "Passwort", pos=wx.Point(10,100))
        wx.StaticText(self, -1, "Mediaplayer\n(Pfad)", pos=wx.Point(10,140))

        # Read Values from file
        try:
            # Write values in txt-file
            filehandle = file("settings.txt", "rt")
            data = filehandle.read()
            splitted = data.split(';')
            ip = splitted[0]
            username = splitted[2]
            port = splitted[1]
            mediaplayer = splitted[3]                
            filehandle.close()
        except:
            ip = ""
            username = ""
            port = ""
            mediaplayer = ""        
        
       
        self.ip_txtctrl = wx.TextCtrl(self, -1, ip, size=(80, -1), pos=wx.Point(130,20))
        self.port_txtctrl = wx.TextCtrl(self, -1, port, size=(50, -1), pos=wx.Point(220,20))
        self.username_txtctrl = wx.TextCtrl(self, -1, username, size=(140, -1), pos=wx.Point(130,60))
        self.password_txtctrl = wx.TextCtrl(self, -1, "", size=(140, -1), pos=wx.Point(130,100), style=wx.TE_PASSWORD)
        self.media_txtctrl = wx.TextCtrl(self, -1, mediaplayer, size=(140, -1), pos=wx.Point(130,140))
        
        self.__connect_btn = wx.Button(self, -1, "Verbinden", pos=wx.Point(100,180))
        self.__connect_btn.Bind(wx.EVT_BUTTON, self.onConnect)
        
        
    
    
        
    def onConnect(self, event):
        mistake = False
        ip = self.ip_txtctrl.GetValue()
        port = self.port_txtctrl.GetValue()
        try:
            port=  int(port)
        except:
            mistake = True
        
        username = self.username_txtctrl.GetValue()
        password = self.password_txtctrl.GetValue()
        mediaplayer = self.media_txtctrl.GetValue()
        
        if ip == "" or port < 0 or port > 65000 or username == "" or password == "" or mediaplayer == "":
            mistake = True
            
        if mistake:
            dlg = wx.MessageDialog(self, 'Es wurden nicht alle Felder korrekt ausgefuellt','Fehler',wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
    
        else:
            try:
                # Write values in txt-file
                filehandle = file("settings.txt", "wt")
                filehandle.write("%s;%s;%s;%s" %(ip, port, username, mediaplayer))
                filehandle.close()
            except:
                pass
            self.parent.api_obj = xmlapi_client.XMLApiClient(username, password, ip, port)
            self.parent.mediaplayer = mediaplayer
            
        self.Destroy()
        self.parent.getFiles()
        


class LogApp(wx.App):
    def OnInit(self):
        splash = LogFrame()
        splash.Show()

        return True

#-----------------------------------------------------------------------------------------
# das Hauptprogramm / der Rahmen

if (__name__ == '__main__'):
    app = LogApp(False)       # Anwendung instantiieren
    app.MainLoop()
