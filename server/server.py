# $Log: server.py,v $
# Revision 1.21  2007/12/08 23:24:38  jeldrik
# Comments added
#
# Revision 1.20  2007/12/08 22:34:31  jeldrik
# error in stopServer fixed
#
# Revision 1.19  2007/12/08 22:31:58  jeldrik
# error in streaming fixed
#
# Revision 1.18  2007/12/08 21:30:31  jeldrik
# getFileLink secured
#
# Revision 1.17  2007/12/08 21:14:40  jeldrik
# id -> file_id
#
# Revision 1.16  2007/12/08 21:11:41  jeldrik
# get files by hash
#
# Revision 1.15  2007/12/08 20:52:57  jeldrik
# ident error
#
# Revision 1.14  2007/12/08 20:43:15  jeldrik
# getFileList finished
#
# Revision 1.13  2007/12/04 14:11:14  jeldrik
# reloadShares finished
#
# Revision 1.12  2007/12/04 10:50:01  jeldrik
# reloadShares added
#
# Revision 1.11  2007/12/01 03:20:43  jeldrik
# Comments added and epydoc
#
# Revision 1.10  2007/12/01 02:59:31  jeldrik
# XMLAPI -> doServerRestart
#
# Revision 1.9  2007/12/01 01:54:44  jeldrik
# stopServer updated
#
# Revision 1.8  2007/11/30 23:05:09  jeldrik
# fit to streapy.py
#
# Revision 1.7  2007/11/30 21:19:38  jeldrik
# AuthRequest completed
#
# Revision 1.6  2007/11/27 16:30:02  jeldrik
# DBConnect added
# Receiving pwd on authcoderequest
#
# Revision 1.5  2007/11/25 05:31:22  jeldrik
# first implementation of the xmlparser
#
# Revision 1.4  2007/11/24 22:20:03  jeldrik
# XMLDataHandler removed
#
# Revision 1.3  2007/11/24 22:12:56  jeldrik
# Head changed
#
# Revision 1.2  2007/11/24 22:11:37  jeldrik
# Logging added
#

import sys
import os
import threading
import socket
import time
import stat
import sqlite3
import random
import binascii
import md5
from Crypto.Cipher import AES
try:
    sys.path.append(os.getcwd().rstrip("server"))
    import xml_api.xmlapi as xmlapi
except:
    print "Could not import the xmlapi"
    sys.exit(1)

class StrSrvError(Exception):
    '''
    Simple class for throwing customized exceptions
    '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
    
class DBConnect(object):
    def __init__(self):
        self.__myconn = None
        self.__cursor = None
        


    def connect_db(self):
        try:
            self.__myconn = sqlite3.connect("db/streapy_db", isolation_level = None)
            self.__cursor = self.__myconn.cursor()             
        except Exception, e:
            print "[ERROR]",e 
    
        return self.__myconn, self.__cursor

class StreamServer(threading.Thread):
    '''
    The server handles the requests, sends responses and streams the data
    '''
    def __init__(self, clsock, doc_root, bandwidth_dict, bw_pos, callback):
        '''
        The StreamServer takes four arguments:
            clsock         - (sockobj)    the client socket
            doc_root       - (string)     folder which is the root of the server
            bandwidth_dict - (dictionary) includes the bandwidth of each client
            bw_pos         - (sting)      the position for this client in the bandwidth_dict
            pid            - (int)        the pid of the server
        '''

        #We do not validate the arguments here because it is done in the
        #ConnectionManager allready.
        #If somebody instantiate this class directly we sould
        #not care about due to performance
        self.__DEBUG     = True
        self.__DOC_ROOT  = doc_root
        self.__clsock    = clsock
        self.__band_dict = bandwidth_dict
        self.__bw_pos    = bw_pos
        self.__callBack  = callback

        threading.Thread.__init__(self)

    def __writeDebug(self, msg):
        '''
        Simple method for printing debug messages if self.__DEBUG is true
        '''
        if self.__DEBUG == True:
            print "[DEBUG]",msg

    def __checkFile(self, myfile):
        '''
        This Method checks if the file is really useable for our streaming process.
        It takes exaxtly one argument:
            myfile - (string) the complete path to the file

        Returns: A dictionary inlcudling the follwoing keys: size, last_modified, suffix, code and handler
                 or a string "404", if the file could not be found
        '''
        #If the file exists instantiate a os.stat object else return 404
        try:
            f_stat = os.stat(myfile)
        except:
            self.__writeDebug("%s 404 File Not Found" % (myfile))
            return "404"

        #Get the interessting data
        f_ret_data = {}
        if stat.S_ISREG(f_stat[stat.ST_MODE]):
            f_ret_data["size"]          = f_stat[stat.ST_SIZE]
            f_ret_data["last_modified"] = f_stat[stat.ST_MTIME]
            f_ret_data["suffix"]        = myfile.split(".")[-1]
            f_ret_data["code"]          = "206"
            #Put the filehandler into the dictionary
            try:
                f_ret_data["handler"]   = file(myfile,"rb")
                self.__writeDebug("File is ready: %s" % (str(f_ret_data["handler"])))
            except:
                self.__writeDebug("Error while creating handler!")
                return "404"

            return f_ret_data

    def __processRequest(self, request):
        '''
        This method walks through the request and finds all interessting data.
            TODO: ICY-Data
        Returns: a tupel containing the filename and the requested http version
        '''
        #Check if we really received a GET-Request
        if request.startswith("GET"):
            self.__writeDebug("Parsing the header")
            #Parse the filename and HTTP-Ver from the first line of the request
            try:
                data = request.split("\r\n")[0].split(" ")
                filename = data[1]
                http_ver = data[2]
            except:
                raise StrSrvError("RequestError: Could not understand the HTTP-Request")

            return (filename, http_ver,)
        elif request.startswith("<?xml"):
            self.__writeDebug("Parsing xml")
            #Parse the XML data
            xmldata = xmlapi.XMLDataHandler(request)
            if xmldata.getAuthCodeReq() == False:
                return (xmldata.getAuthUser(), xmldata.getAuthCode(), xmldata.getAuthID(), xmldata.getMethod(), xmldata.getParameters())
            else:
                return xmldata.getAuthCodeReq()          
                    
        else:
            raise StrSrvError("RequestError: Could not understand the Request")

    def __produceResponse(self, http_ver, code, cont_type = "", cont_length = "", last_mod = ""):
        '''
        This method builds and returns a complete response which must be send to the client.
        It takes five arguments:
            http_ver    - (string) HTTP-Version of the following data
            code        - (string) HTTP-Statuscode (206, 400, 404)
            cont_type   - (string) Content-Type (audio/mpeg, video/mpeg, ..)
            cont_length - (string) Length of the following data
            las_mod     - (string) Date when the data was modified
        '''
        self.__writeDebug("Building response")

        #We send a complete error page, if the requested file could not be found
        if code == "404":
            response  = "%s 404 Not Found\r\n" % (http_ver)
            response += "Server: StreaPy_Streaming/0.1\r\n"
            response += "Content-Type: text/html; charset=iso-8859-1\r\n"
            response += "Connection: close\r\n"
            response += "\r\n"
            response += '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">\n'
            response += '<html><head>\n'
            response += '<title>404 Not Found</title>\n</head><body>\n'
            response += '<h1>Not Found</h1>\n<p>The requested URL /bla.avi was not found on this server.</p>\n'
            response += '<hr><address>StreaPy_Streaming/0.1</address>\n</body></html>\n'

        #We also send a complete error page if the request was not right formated
        elif code == "400":
            response  = "%s 400 Bad Request\r\n" % (http_ver)
            response += "Server: StreaPy_Streaming/0.1\r\n"
            response += "Content-Type: text/html; charset=iso-8859-1\r\n"
            response += "Connection: close\r\n"
            response += "\r\n"
            response += '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">\n'
            response += '<html><head>\n'
            response += '<title>400 Bad Request</title>\n</head><body>\n'
            response += '<h1>Bad Request</h1>\n<p>The server was not able to understand the request.</p>\n'
            response += '<hr><address>StreaPy_Streaming/0.1</address>\n</body></html>\n'

        #Else we guess a conetent-type
        else:
            if cont_type == "avi":
                cont_type = "video/x-msvideo"
            elif cont_type == "movie":
                cont_type = "video/x-sgi-movie"
            elif cont_type == "qt" or cont_type == "mov":
                cont_type = "video/quicktime"
            elif cont_type == "mpeg" or cont_type == "mpg" or cont_type == "mpe":
                cont_type = "video/mpeg"
            elif cont_type == "mp3":
                cont_type = "audio/mpeg"
            elif cont_type == "ogg":
                cont_type = "application/ogg"
            elif cont_type == "wav":
                cont_type = "audio/x-wav"
            else:
                cont_type = "*/*"

            #convert the last modified date into the right format
            last_mod = time.strftime("%a, %d %b %Y %H:%M:%S GMT",time.gmtime(last_mod))

            #and build the response
            response  = "%s 206 Partial Content\r\n" % (http_ver)
            response += "Server: StreaPy_Streaming/0.1\r\n"
            response += "Last-Modified: %s\r\n" % (last_mod)
            response += "Content-Type: %s\r\n" % (cont_type)
            response += "Content_Length: %s\r\n" % (str(cont_length))
            response += "Connection: close\r\n"
            response += "\r\n"

        return response
    
    def __cryptAuthCode(self, key):
        '''
        Generate a crypted AuthCode to send it to the client
        Accepts:
            key - (string) MD5 hash of the users pw from the database
        '''
        #Generate a list with numbers for the sample method
        numbers = []
        for i in range(47,122):
            #0-9
            if i >= 48 and i <= 57:
                numbers.append(i)
            #A-Z
            elif i >= 65 and i <= 90:
                numbers.append(i)
            #a-z
            elif i >= 97 and i <= 122:
                numbers.append(i)
        
        #Generate a Authcode
        plain = ""
        for i in range(32):
            plain += chr(random.sample(numbers,1)[0])
                 
        cryptobj = AES.new(key)
        
        #encrypt the authcode and return a list with plain and encrpted authcode
        return [plain,cryptobj.encrypt(plain)]
    
    def __checkAuthCode(self, id, authcode, user):
        '''
        Validate the Authcode from the user
        Accepts:
            id           - (int)     ID of the User
            authcode     - (string)  decrypted authcode
            user         - (string) Username
        '''
        try:
            id = int(id)
        except:
            raise StrSrvError("ID must be an integer")
        
        try:
            dbcon  = DBConnect()
            myconn, cursor = dbcon.connect_db()
            #Select the generated authcode
            qry = "SELECT plain FROM authrequests WHERE id='%i' and username='%s'" % (id,user)
            cursor.execute(qry)
            plain = cursor.fetchone()[0]
            #delete the auscode
            qry = "DELETE FROM authrequests WHERE id='%i'" % (id)
            cursor.execute(qry)
            #check if the authcode was right
            if plain == authcode:
                return True
            else:
                return False
        except:
            False     
            
    def __reloadShares(self):
        '''
        Reload the shares if it is requested.
        Walk trough all sahres and add new files to the database
        '''
        #This part is for adding new files into the database
        #The DOC_ROOT has no id
        shares = [(0,self.__DOC_ROOT)]
        dbcon  = DBConnect()
        myconn, cursor = dbcon.connect_db()
        qry = "SELECT * FROM shared_folders"
        cursor.execute(qry)
        #Add the shares from database
        shares += cursor.fetchall()
        #Walk through all configured shares
        for dir in shares:
            #We have to make a difference between the DOC_ROOT and other shares
            #DOC_ROOT
            if dir[0] == 0:
                #All files
                for file in os.listdir(dir[1]):
                    #If the found data is a file add if it doesnt exist
                    if os.path.isfile(os.path.join(dir[1],file)):
                        qry = "SELECT id FROM shared_files WHERE filename='%s' and folder_id='%s'" % (file,dir[0])
                        cursor.execute(qry)
                        id = cursor.fetchone()
                        if str(type(id)) == "<type 'NoneType'>":
                            qry = "INSERT INTO shared_files (filename,folder_id) VALUES('%s', '%s')" % (file, dir[0])
                            cursor.execute(qry)
                            self.__writeDebug(str(file)+" was added to DOC_ROOT")
            #Other Shares
            else:
                #Check if the path really exists
                if os.path.exists(os.path.join(self.__DOC_ROOT,dir[1])):
                    #All files
                    for file in os.listdir(os.path.join(self.__DOC_ROOT,dir[1])):
                        #If the found data is a file add if it doesnt exist
                        if os.path.isfile(os.path.join(self.__DOC_ROOT,dir[1],file)):
                            qry = "SELECT id FROM shared_files WHERE filename='%s' and folder_id='%s'" % (file,dir[0])
                            cursor.execute(qry)
                            id = cursor.fetchone()
                            if str(type(id)) == "<type 'NoneType'>":
                                qry = "INSERT INTO shared_files (filename,folder_id) VALUES('%s', '%s')" % (file, dir[0])
                                cursor.execute(qry)
                                self.__writeDebug(str(file)+" was added to "+str(dir[1])+"("+str(dir[0])+")")
                                
        #Delete files from the database if they dont exist anymore
        qry = "SELECT * FROM shared_files"
        cursor.execute(qry)
        #Fetch all files from the database
        files = cursor.fetchall()
        for onefile in files:
            #Look for deletes files in the DOC_ROOT
            if onefile[2] == 0:
                if not(os.path.isfile(os.path.join(self.__DOC_ROOT,onefile[1]))):
                    qry = "DELETE FROM shared_files WHERE id='%s'" % (onefile[0])
                    cursor.execute(qry)
                    self.__writeDebug(onefile[1]+" was delete from DOC_ROOT")                     
            else:
                #Select the folder of the file and test for its existance
                qry = "SELECT folder FROM shared_folders WHERE id='%s'" % (onefile[2])
                cursor.execute(qry)
                folder = cursor.fetchone()[0]
                if not(os.path.isfile(os.path.join(self.__DOC_ROOT,folder,onefile[1]))):
                    qry = "DELETE FROM shared_files WHERE id='%s'" % (onefile[0])
                    cursor.execute(qry)
                    self.__writeDebug(onefile[1]+" was delete from "+folder) 
            
        cursor.close()
        myconn.close()
              
    def run(self):
        '''
        The method name is needed by the threading interface. In our case it runs all needed methods
        and sends the data in pieces of 1024 bytes
        '''
        #Get the request and parse it. If we cannot parse it, it is very very bad ;-)
        request = self.__clsock.recv(2048)
        try:
            prcdrequest = self.__processRequest(request)

            
            if type(prcdrequest) == tuple and len(prcdrequest) == 2:
                try:
                    (filehash, http_ver) = prcdrequest

                    #Connect to database
                    dbcon  = DBConnect()
                    myconn, cursor = dbcon.connect_db()
                    #translate hash to real file
                    qry = "SELECT shared_files.filename, shared_files.folder_id FROM shared_files, file_requests WHERE shared_files.id = file_requests.file_id and file_requests.hash = '%s'" % (filehash.replace("/",""))
                    cursor.execute(qry)
                    data = cursor.fetchone()
                    filename = data[0]
                    folder_id = str(data[1])
                    
                    if folder_id == "0":
                        foldername = ""
                    else:
                        qry = "SELECT folder FROM shared_folders WHERE id='%s'" % (folder_id)
                        cursor.execute(qry)
                        foldername = cursor.fetchone()[0]

                    #delte the hash from database
                    qry = "DELETE FROM file_requests WHERE hash='%s'" % (filehash.lstrip("/"))
                    cursor.execute(qry)
                except Exception, e:
                    print e
                    self.__writeDebug("400 Bad Request")
                    response = self.__produceResponse("HTTP/1.0", "400")
                    self.__clsock.send(response)
                    self.__clsock.close()
                    return
                                   
                #Check if the file is ok
                file_data = self.__checkFile(os.path.join(self.__DOC_ROOT,foldername,filename))
                if type(file_data) == dict:
                    #Call the produceResponse method, send the response
                    response = self.__produceResponse(http_ver, file_data["code"], file_data["suffix"], file_data["size"], file_data["last_modified"])
                    self.__clsock.send(response)
                    self.__writeDebug("Sendprocess started")
                    try:
                        #and finally send the data
                        while True:
                            #Just send if there is enough bandwidth for us
                            if self.__band_dict[self.__bw_pos] > 0:
                                #reduce the left bandwidth
                                self.__band_dict[self.__bw_pos] -= 1
                                send_data = file_data["handler"].read(1024)
                                if not send_data:
                                    break
                                self.__clsock.send(send_data)
                            else:
                                time.sleep(0.005)
                        #Delete our bandwidth, if we have finished sending
                        del self.__band_dict[self.__bw_pos]
                        self.__writeDebug("Sendprocess completed")
                    except:
                        del self.__band_dict[self.__bw_pos]
                        self.__writeDebug("Sendprocess aborted")
                        try:
                            self.__clsock.close()
                        except:
                            pass
                else:
                    #If the returned file_data is not a dictionary but a string we produce the 404 Not Found response
                    response = self.__produceResponse(http_ver, file_data)
                    self.__clsock.send(response)
                    self.__clsock.close()
    
            elif type(prcdrequest) == tuple and len(prcdrequest) == 5:
                    self.__writeDebug("Request by "+prcdrequest[0])
                    #devide the parameters
                    (authuser, authcode, authid, method, parameters) = prcdrequest
                    #connect to the databsse
                    dbcon  = DBConnect()
                    myconn, cursor = dbcon.connect_db()
                    #check if teh user is admin
                    try:
                        qry = "SELECT admin FROM users WHERE username='%s'" % (authuser)
                        cursor.execute(qry)
                        admin = int(cursor.fetchone()[0])
                    except:
                        raise StrSrvError("Could not read the admin field")
                        admin = 0
                        
                    #check if he passed the authentification
                    authokay = self.__checkAuthCode(authid, authcode, authuser)
                                  
                    if method == "doServerRestart":
                        #calls the callback method in the connectionmanager
                        if admin and authokay:
                            self.__clsock.close()
                            self.__callBack(True)
                        else:
                            self.__clsock.send('<?xml version="1.0"?><stxmlapires><error>The password was wrong or you are no admin! (Did you request an AuthCode?)</error></stxmlapires>')
                    
                    elif method == "reloadShares":
                        #calls the reloadshares method from above
                        if admin and authokay:
                            self.__reloadShares()
                        else:
                            self.__clsock.send('<?xml version="1.0"?><stxmlapires><error>The password was wrong or you are no admin! (Did you request an AuthCode?)</error></stxmlapires>')
                            
                    elif method == "getFileList":
                        if authokay:
                            self.__writeDebug("Generating a list of files and folders as requested")
                            try:
                                #Get the ID of the user
                                qry = "SELECT id FROM users WHERE username='%s'" % (authuser)
                                cursor.execute(qry)
                                uid = cursor.fetchone()[0]
                                #Get all folders available to the user
                                qry = "SELECT shared_folders.id, shared_folders.folder FROM shared_folders, users, urights_folder WHERE shared_folders.id = urights_folder.folder_id and users.id = urights_folder.user_id and users.id = '%s'" % (uid)
                                cursor.execute(qry)
                                folders = cursor.fetchall()
                                #Get all group ids of the groups of the user
                                qry = "SELECT group_id FROM user_groups WHERE user_id='%s'" % (uid)
                                cursor.execute(qry)
                                groups = cursor.fetchall()
                                #Get all folders available to the groups of the user
                                #dict for all files
                                files = {}
                                #|/ are files out of a folder
                                files["|/"] = []
                                for group in groups:
                                    #Get the folders
                                    qry = "SELECT shared_folders.id, shared_folders.folder FROM shared_folders, groups, grights_folder WHERE shared_folders.id = grights_folder.folder_id and groups.id = grights_folder.group_id and groups.id = '%s'" % (group[0])
                                    cursor.execute(qry)
                                    folders += cursor.fetchall()
                                    #and single files and put them into the dict
                                    qry = "SELECT shared_files.id, shared_files.filename FROM shared_files, groups, grights_files WHERE shared_files.id = grights_files.file_id and groups.id = grights_files.group_id and groups.id = '%s'" % (group[0])
                                    cursor.execute(qry)
                                    files["|/"] += cursor.fetchall()
                                
                                #get all files of the available folders
                                for folder in folders:
                                    qry = "SELECT id, filename FROM shared_files WHERE folder_id='%s'" % (folder[0])
                                    cursor.execute(qry)
                                    files[folder[1]] = cursor.fetchall()
                                    
                                #select single files
                                qry = "SELECT shared_files.id, shared_files.filename FROM shared_files, users, urights_files WHERE shared_files.id = urights_files.file_id and users.id = urights_files.user_id and users.id = '%s'" % (uid)
                                cursor.execute(qry)
                                files["|/"] += cursor.fetchall()
                                
                                #Delete doubled entries
                                for slf in files["|/"]:
                                    for k in files.keys():
                                        if slf in files[k] and k != "|/":
                                            try:
                                                while files["|/"].count(slf):
                                                    idx = files["|/"].index(slf)
                                                    del files["|/"][idx]
                                            except:
                                                pass
                                            
                                #generate a proper response for the clients
                                response = '<?xml version="1.0"?><stxmlapires>'
                                for k in files.keys():
                                    if k != "|/":
                                        #files with folder bining
                                        response += '<folder name="%s">' % (k)
                                        for myfile in files[k]:
                                            response += '<file name="%s" id="%s"></file>' % (myfile[1], myfile[0])
                                        response += '</folder>'
                                    else:
                                        #and without
                                        response += '<folder>'
                                        for myfile in files["|/"]:
                                            response += '<file name="%s" id="%s"></file>' % (myfile[1], myfile[0])
                                        response += '</folder>'
                                response += '</stxmlapires>'
                                            
                                self.__clsock.send(response)
                            
                            except:
                                response = '<?xml version="1.0"?><stxmlapires><error>Error while walking through the database</error></stxmlapires>'
                                raise StrSrvError("Error while walking through the database")
                              
                        else:
                            response = '<?xml version="1.0"?><stxmlapires><error>The password was wrong or you are no admin! (Did you request an AuthCode?)</error></stxmlapires>'
                            self.__clsock.send(response)
                            
                    elif method == "getFileLink":
                        if authokay:
                            #check for the right parameter
                            try:
                                id = int(parameters["file_id"])
                            except:
                                response = '<?xml version="1.0"?><stxmlapires><error>wrong id!</error></stxmlapires>'
                                self.__clsock.send(response)
                                raise StrSrvError("Wrong ID for file link!")
                            
                            try:
                                #select the filename
                                qry = "SELECT id,filename FROM shared_files WHERE id='%s'" % (id)
                                cursor.execute(qry)
                                id, filename = cursor.fetchone()
                                #generate a random number
                                salt = str(random.randint(1000,1000000))
                                #generate a unique hash (name+id+salt)
                                filehash = md5.new(filename+str(id)+salt).hexdigest()
                                self.__writeDebug("Linkhash for %s is %s" % (id, filehash))
                                qry = "INSERT INTO file_requests (hash, file_id) VALUES('%s', '%s')" % (filehash, id)
                                cursor.execute(qry)
                                #and send a response
                                response = '<?xml version="1.0"?><stxmlapires><linkhash>%s</linkhash></stxmlapires>' % (filehash)
                                self.__clsock.send(response)
                            except:
                                response = '<?xml version="1.0"?><stxmlapires><error>Error while generating link!</error></stxmlapires>'
                                self.__clsock.send(response)
                                raise StrSrvError("Error while generating link!")
                            
                        else:
                            response = '<?xml version="1.0"?><stxmlapires><error>The password was wrong or you are no admin! (Did you request an AuthCode?)</error></stxmlapires>'
                            self.__clsock.send(response)                                                             
                                                                     
                    #close all connections
                    cursor.close()        
                    myconn.close()
                    self.__clsock.close()
            else:
                   self.__writeDebug("CodeRequest: "+str(prcdrequest))
                   #DB Connection
                   try:
                       dbcon  = DBConnect()
                       myconn, cursor = dbcon.connect_db()
                       #Get the salt and the MD5-Hash of the users passwd
                       qry = "SELECT password, salt FROM users WHERE username='%s'" % (prcdrequest)
                       cursor.execute(qry)
                       passwd, salt = cursor.fetchone() 
           
                       #Insert the AuthCode and get the ID
                       plain, authcode = self.__cryptAuthCode(passwd)
                       authcode = binascii.b2a_hex(authcode)
                       qry = "INSERT INTO authrequests (authcode, plain, username) VALUES('%s', '%s', '%s')" % (authcode, plain, prcdrequest)
                       cursor.execute(qry)
                       qry = "SELECT id FROM authrequests WHERE authcode = '%s'" % (authcode)
                       cursor.execute(qry)
                       aid = cursor.fetchone()[0]     
        
                       #Send the Response to the client
                       xmlresponse = '<?xml version="1.0"?><stxmlapires><auth><authcode>%s</authcode><authid>%s</authid><salt>%s</salt></auth></stxmlapires>' % (authcode, aid, salt)
                       self.__clsock.send(xmlresponse)
                       self.__writeDebug("Plain: "+plain)
                       cursor.close()
                       myconn.close()
                   except:
                       raise StrSrvError("Error while AuthCodeRequest!") 
                    
                   self.__clsock.close()
               
        except Exception, e:
            print e
            self.__clsock.close()

class BandwidthManager(threading.Thread):
    '''
    The bandwidth manager controls the bandwidthflow for each client
    Exp.:
    bwmng = BandwidthManager(bandwidth_dict, int(max_band))
    bwmng.start()
    '''
    def __init__(self, bandwidth_dict, max_band):
        '''
        The BandwidthManager takes two arguments:
            The first argument is a dictionary which includes the amount of bandwidth for each client
            and the second argument is an integer which defines the maximum of bandwidth for each client
        '''

        #We donot validate the max_band argument, because it is done in the ConnectionManager
        self.__max_band = max_band
        
        #Run attribute
        self.__run = True

        #Validate the arguments
        if type(bandwidth_dict) == dict:
            self.__bandwidth_dict = bandwidth_dict
        else:
            raise StrSrvError("BandwidthError: Invalid BandwidthContainer (must be a dictionary)")

        threading.Thread.__init__(self)

    def __refillBandwidth(self):
        '''
        Refills the bandwidth dictionary with the givin maximum every second
        '''
        for key in self.__bandwidth_dict.keys():
            self.__bandwidth_dict[key] = self.__max_band/10
    
    def stopBandwidthManager(self):
        '''
        Stop the BandwidthManager
        '''
        self.__run = False
        
    def run(self):
        '''
        Needed method for threading
        '''
        while self.__run:
            time.sleep(0.1)
            self.__refillBandwidth()

class ConnectionManager(object):
    '''
    The connection manager gets the connection and loads them to a thread
    '''
    def __init__(self, doc_root, ip = "127.0.0.1", port = "3310", max_con = "100", max_band = "350"):
        '''
        The connection Manager takes five arguments:
            doc_root  - (string) directory which is the root of the server
            ip        - (string) listen hostname or ip (*)
            port      - (string) listen port (*)
            max_con   - (string) maximum amount of connections the server will accept (*)
            max_band  - (string) maximum bandwidth for each client (*)
                (*) Optional
        '''
        self.__DEBUG = True
        self.__stop  = False

        #We do not validate the ip because it could be a hostname, too. If somebody gives crap here,
        #the server won't be able to bind the socket and raise an exception
        self.__ip = ip
        
        #PID of the Server
        self.__pid = 0
        
        #Socket attributes
        self.__srvsock = None
        self.__clientsock = None

        #Validate the arguments
        self.__max_con  = 0
        self.__PORT     = 0
        self.__max_band = 0
        self.__DOC_ROOT = None
        try:
            self.__max_con = int(max_con)
            if self.__max_con <= 0:
                self.__max_con = 100
        except:
            raise StrSrvError("MaxConError: Invalid format")

        try:
            self.__PORT = int(port)
            if self.__PORT <= 1023 or self.__PORT >= 65535:
                raise StrSrvError("PortError: Too high or low")
        except:
            raise StrSrvError("PortError: Must be an integer")

        try:
            self.__max_band = int(max_band)
            if self.__max_band == 0:
                self.__max_band = 350
        except:
            raise StrSrvError("BandwidthError: Invalid Value")

        if os.access(doc_root, os.F_OK | os.R_OK):
            self.__DOC_ROOT = doc_root
        else:
            raise StrSrvError("DocRootError: Can not find or access the directory")

    def __writeDebug(self, msg):
        '''
        Simple method for printing debug messages if self.__DEBUG is true
        '''
        if self.__DEBUG == True:
            print "[DEBUG]",msg

    def stopServer(self, stop=True):
        '''
        Will tell the loop to exit and hold the server
        '''
        if stop == True:
            self.__stop = True
            s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            s.connect ( ( self.__ip, self.__PORT ) )
            s.close()

    def startServer(self):
        '''
        This method binds the socket, accepts connections and manages the threads.
        Two kinds of threads are important:
            The BandwidthManager to ensure the data flow
            The StreamServer which is the main part of this program
        '''
        #Try to bind the socket to the given IP/hostname and port
        try:
            self.__srvsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__srvsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__pid = os.getpid()
            self.__writeDebug("Server started: %s:%i with PID %i" % (self.__ip, self.__PORT, self.__pid))
            self.__srvsock.bind((self.__ip, self.__PORT))
            self.__srvsock.listen(1)
        except Exception, e:
            print e[1]
            raise StrSrvError("SocketError: Could not bind the socket")
        
        try:
            pidfile = file(os.getcwd().rstrip("server")+"/.streapypid","wt")
            pidfile.write(str(self.__pid))
            pidfile.close()
        except:
            raise StrSrvError("Could not write PID file")

        #Set up an empty dictionary for the BandwidthManager and start a new thread for it
        try:
            bandwidth_dict = {}
            bndmng = BandwidthManager(bandwidth_dict, self.__max_band)
            bndmng.start()
        except Exception, e:
            print e

        #Let the Server serve for ever
        while True:
            #Accept new connections
            (self.__clientsock, address)  = self.__srvsock.accept()
            if self.__stop == True:
                self.__clientsock.close()
                bndmng.stopBandwidthManager()
                break
            self.__writeDebug("New connection from %s" % (str(address[0])))
            #Push the new connection into a thread or block it, if there are too many connections
            #(all threads - (1 thread: server himself + 1 thread: BandwidthManager) = all clients)
            if self.__max_con > (threading.activeCount()-2):
                #Create a new bandwidth entry
                bandwidth_dict[str(len(bandwidth_dict))] = self.__max_band
                #Start the proper server
                strsrv = StreamServer(self.__clientsock, self.__DOC_ROOT, bandwidth_dict, str(len(bandwidth_dict)-1), self.stopServer)
                strsrv.start()
                self.__writeDebug("We have %i active threads now" % (threading.activeCount()-1))
            else:
                self.__writeDebug("Connection blocked: Limit reached")
                self.__clientsock.close()

        try:
            self.__writeDebug("Closing Server-Socket")
            self.__srvsock.close()
        except:
            pass
