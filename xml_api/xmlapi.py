# $Log: xmlapi.py,v $
# Revision 1.10  2007/12/08 15:34:44  jeldrik
# Docu added
#
# Revision 1.9  2007/12/01 03:22:47  jeldrik
# try / except added
#
# Revision 1.8  2007/11/30 21:19:14  jeldrik
# Comment changed
#
# Revision 1.7  2007/11/27 20:08:42  jeldrik
# comments added
#
# Revision 1.6  2007/11/27 16:30:58  jeldrik
# The authcoderequest now accepts a user
#
# Revision 1.5  2007/11/25 05:30:49  jeldrik
# getter names changed
#
# Revision 1.4  2007/11/25 03:02:23  jeldrik
# imports changed
#
# Revision 1.3  2007/11/25 03:00:50  jeldrik
# complete rewrite
#
# Revision 1.2  2007/11/24 23:28:09  jeldrik
# Type of content of parameters changed from u' str to str
#
# Revision 1.1  2007/11/24 23:16:33  jeldrik
# first concept
#

import xml.dom.minidom

class XMLAPIError(Exception):
    '''
    Simple class for throwing customized exceptions
    '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class XMLDataHandler(object):
    '''
    This class handels the data sended in xml format.
    The data will be formated for the streaming server
    '''
    def __init__(self, xmldata):
        '''
        Provides all data even the xml data to parse. At
        least it starts the parsing process
        '''
        self.__xmldata     = xmldata
        self.__authuser    = None
        self.__authcode    = None
        self.__authid      = None
        self.__method      = None
        self.__parameters  = None
        self.__authcodereq = False
        self.__parseXML()
    
    def __parseXML(self):
        '''
        This method parses the given xml data.
        The data is given by the __init__
        '''
        dom    = xml.dom.minidom.parseString(self.__xmldata)
        #Go to the first element
        try:
            apireq = dom.getElementsByTagName("stxmlapireq")
        except:
            raise XMLAPIError("Request does not start with <stxmlapireq>")
        
        for req in apireq:
            #Go through all items
            for item in req.childNodes:
                #and subitems
                child = item
                while child != None:
                    #If there are children search for a specific child
                    #and get the data for...
                    if child.nodeName == "auth":
                        #...authentification
                        try:
                            self.__authuser = child.getElementsByTagName("authuser")[0].firstChild.wholeText                    
                            self.__authcode = child.getElementsByTagName("authcode")[0].firstChild.wholeText
                            self.__authid   = child.getElementsByTagName("authid")[0].firstChild.wholeText
                        except:
                            raise XMLAPIError("Could not get all auth data")        
        
                    elif child.nodeName == "request":
                        #...stuff the server should do
                        try:
                            self.__method     = child.getElementsByTagName("method")[0].firstChild.wholeText
                            self.__parameters = {}
                            try:
                                for param in child.getElementsByTagName("param"):
                                    self.__parameters[str(param.getAttribute("name"))] = str(param.firstChild.wholeText)
                            except:
                                pass
                        except:
                            raise XMLAPIError("Could not get method")
                            
                    elif child.nodeName == "authcoderequest":
                        #...or the request for authentication
                        self.__authcodereq = child.firstChild.wholeText
                
                    child = child.firstChild
        
        
    def getAuthUser(self):
        '''
        Returns the username
        '''
        return self.__authuser
    
    def getAuthCode(self):
        '''
        Returns the needed authcode
        '''
        return self.__authcode
    
    def getAuthID(self):
        '''
        Returns the id of the authcode
        '''
        return self.__authid
    
    def getMethod(self):
        '''
        Returns the method to do
        '''
        return self.__method
    
    def getParameters(self):
        '''
        Returns the parameters needed by the method
        '''
        return self.__parameters
    
    def getAuthCodeReq(self):
        '''
        If there is an authrequest it returns the username of the requester
        '''
        return self.__authcodereq

if __name__ == "__main__":
    try:
        #<?xml version="1.0"?><stxmlapireq><auth><authuser>jeldrik</authuser><authcode>Y02Ei5IlHWi29ZfvwLrksusIWeCCIYm1</authcode><authid>1</authid></auth><request><method>reloadShares</method></request></stxmlapireq>
        data = '<?xml version="1.0"?><stxmlapireq><auth><authuser>jeldrik</authuser><authcode>343fggh44345865hjlv24</authcode><authid>345347</authid></auth><request><method>getFileLink</method><param name="file_id">34</param><param name="usecount">5</param></request></stxmlapireq>'
        #data = '<?xml version="1.0"?><stxmlapireq><authcoderequest>Jeto</authcoderequest></stxmlapireq>'
        xml = XMLDataHandler(data)
        print xml.getAuthUser()
        print xml.getAuthCode()
        print xml.getAuthID()
        print xml.getMethod()
        print xml.getParameters()
        print xml.getAuthCodeReq()
    except Exception, e:
        print str(e).replace("'","")
        
        