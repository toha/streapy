# $Log: xmlapi_client.py,v $
# Revision 1.3  2007/12/08 23:21:50  streapy
# -
#
# Revision 1.2  2007/12/08 21:32:15  streapy
# Fehlerkorrekturen
#
# Revision 1.1  2007/12/08 15:36:17  streapy
# initial commit
#

import socket, binascii
import xml.dom.minidom
from Crypto.Cipher import AES
import md5


# constant XML-Strings
XML_AUTHCODEREQ = '<?xml version="1.0"?>\n\
<stxmlapireq>\n\
    <authcoderequest>%s</authcoderequest>\n\
</stxmlapireq>'

XML_APIREQ1 = '<?xml version="1.0"?>\n\
<stxmlapireq>\
    <auth>\
        <authuser>%s</authuser>\
        <authcode>%s</authcode>\
        <authid>%s</authid>\
    </auth>'

XML_APIREQ2 = '<request>\
        <method>%s</method>\
        %s\
    </request>\
</stxmlapireq>'



class XMLAPIError(Exception):
    '''
    Simple class for throwing customized exceptions
    '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class XMLApiClient(object):
    def __init__(self, username, password, server_ip, server_port):
        if username == "" or password == "" or server_ip == "" or server_port == "" or type(server_port) != int:
            raise XMLAPIError, "Attribut values missing"
        self.__username = username
        self.__password = password
        self.__server_ip = server_ip
        self.__server_port = server_port
        
        self.__s = None      

    def getServerIP(self):
        return self.__server_ip
    
    def getPort(self):
        return self.__server_port
  
    def sendRequest(self, request):
        # connecting to the server...
        try:
            self.__s = socket.socket ( socket.AF_INET, socket.SOCK_STREAM ) 
            self.__s.connect ( ( self.__server_ip, self.__server_port ) ) 
        except:
            raise XMLAPIError, "Cannot connect to server"
        
        # sending the request and getting a response     
        response = ""
        res = " "
        try:
            self.__s.send(request)
            while res != None and res != "": 
                res = self.__s.recv( 4096 )
                response += res
                
            self.__s.close()
                
        except:
            raise XMLAPIError, "Error sending request"   
        

        return response        

    def getAuthCode(self):
        
        # building the request...
        xml_str = XML_AUTHCODEREQ %(self.__username)
        response = self.sendRequest(xml_str)          
        
        #Go to the first element
        try:
            dom    = xml.dom.minidom.parseString(response)
            apireq = dom.getElementsByTagName("stxmlapires")[0]
    
            authcode =  apireq.getElementsByTagName("auth")[0].getElementsByTagName("authcode")[0].firstChild.wholeText
            authid =  apireq.getElementsByTagName("auth")[0].getElementsByTagName("authid")[0].firstChild.wholeText  
            salt =  apireq.getElementsByTagName("auth")[0].getElementsByTagName("salt")[0].firstChild.wholeText     

        except:
            raise XMLAPIError("Error reading authcode from response")  
        
        return authcode, authid, salt  

    def processRequest(self, req):
        # Authcode generieren
        auth_info = self.getAuthCode()
        
        
        # Authcode verschluesseln mit eigenem Passwort
            # building password hash
        m = md5.new()
        m.update(self.__password + auth_info[2])
        pw = m.hexdigest()   
        auth =   binascii.a2b_hex(auth_info[0])   
        cryptobj = AES.new(pw)
        authcode = cryptobj.decrypt(auth)

        # Request-Bauen
        request = XML_APIREQ1 %(self.__username, authcode, auth_info[1])
        request += req

        # Request senden
        response = self.sendRequest(request)
        return response
        
    
    def getFileList(self):
        request = XML_APIREQ2 %("getFileList", "")
        response = self.processRequest(request)
        return response
    
    def getFileLink(self, linkid):
        param = '<param name="%s">%s</param>' %("file_id", linkid)
        request = XML_APIREQ2 %("getFileLink", param)

        response = self.processRequest(request) 
        return response        
        
    
    def doServerRestart(self):       
        request = XML_APIREQ2 %("doServerRestart", "")
        response = self.processRequest(request) 
        return response
    
    def reloadShares(self):
        request = XML_APIREQ2 %("reloadShares", "")
        response = self.processRequest(request) 
        return response
    
    
if __name__ == "__main__":
    api_obj = XMLApiClient("jeldrik", "test", "192.168.0.125", 3310)
    print api_obj.doServerRestart()    