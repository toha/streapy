#############################################################################
#
#	$Id: user.py,v 1.1 2007/11/25 05:37:47 streapy Exp $
#	User management (authenticated users, roles).
#
#	This is part of "Snakelets" - Python Web Application Server
#	which is (c) Irmen de Jong - irmen@users.sourceforge.net
#
#############################################################################

#
# Notice that the user id is set once (when creating the user object) and cannot
# be changed, and that the password itself is not stored but its secure hash instead.
#
# Privileges are stored and returned as a Set.
#

import sha, sets, time

# Set the secure hash module to sha.
# This can be changed, you can set this to md5 module for instance
# (for <1.44 compatibility)
securehash=sha

class LoginUser(object):
    def getuserid(self): return self.__userid
    def getname(self): return self.__name
    def setname(self, name): self.__name=name
    def setpassword(self,passwd):
        if passwd:
            string = self.userid+passwd
            if type(string) is unicode:
                string=string.encode("UTF-8")
            self.__passwordhash=securehash.new(string).digest()
        else:
            self.__passwordhash=None
    def getpassword(self): return self.__passwordhash
    def getprivileges(self): return self.__privileges
    def setprivileges(self, privs): self.__privileges=sets.Set(privs)
    def delprivileges(self): self.__privileges=sets.Set()
    
    userid=property(getuserid, None, None, "unique id")
    name=property(getname, setname, None, "descriptive name")
    password=property(getpassword, setpassword, None, "secret password. Only the secure hash is stored, not the pw itself")
    privileges=property(getprivileges, setprivileges, delprivileges, "set of the privileges this user has")
    
    def __init__(self, userid, password=None, name=None, privileges=None, passwordhash=None):
        self.__userid=userid
        self.name=name
        if passwordhash:
            # To initialize the password hash from an external source
            # for instance when you're loading user data from a database
            self.__passwordhash = passwordhash    
        else:
            self.password=password
        self.privileges=privileges or []

    def checkPassword(self, password):
        string = self.userid+password
        if type(string) is unicode:
            string=string.encode("UTF-8")
        return securehash.new(string).digest() == self.__passwordhash
    
    def hasPrivileges(self, privileges):
        # does this user have ALL of the asked privileges?
        return sets.Set(privileges).issubset(self.privileges)
    
    def hasAnyPrivilege(self, privileges):
        # does this user have any of the asked privileges?
        return len(sets.Set(privileges) & self.privileges)>0   # intersection

    def hasPrivilege(self, privilege):
        # does this user have the given privilege?
        return privilege in self.privileges

    def __repr__(self):
        return "<%s.%s object '%s' at 0x%08lx>" % (self.__module__, self.__class__.__name__, self.userid, id(self))



# the following class can be used as a base class for Ypages.
# note that the form fields must be called "login" and "password"
# They can occur both on the request form (examined first) and on the request context.
from YpageEngine import Ypage
import httpauth


class LoginPage(object):
    def attemptLogin(self, fallbackReturnpage=None, successfulLoginFunc=None):
        ctx=self.Request.getContext()
        if self.requiresSession() == self.SESSION_NOT_NEEDED:
            raise Ypage.PageAbortError("session type may not be 'no' for login pages")
        login = self.Request.getParameter("login") or getattr(ctx, "login", None)
        if login:
            # a login attempt is made. Check for returnpage on the session
            returnpage_session = getattr(self.Request.getSessionContext(),"_SNKLOGIN_RETURNPAGE",None)
            MAINPAGE = getattr(ctx,"_SNKLOGIN_RETURNPAGE",None) or returnpage_session or fallbackReturnpage
        else:
            # no login attempt (probably just entering the login page for the first time)
            # don't get a returnpage from the session!
            MAINPAGE = getattr(ctx,"_SNKLOGIN_RETURNPAGE",None) or fallbackReturnpage
        
        if not MAINPAGE:
            raise Ypage.PageAbortError("no RETURNPAGE")
        self.Request.getSessionContext()._SNKLOGIN_RETURNPAGE=MAINPAGE
        
        # check if we are already logged in.
        # in that case, go directly to the main page.
        if self.User:
            del self.Request.getSessionContext()._SNKLOGIN_RETURNPAGE
            self.Yhttpredirect(MAINPAGE)
        else:
            login = self.Request.getParameter("login") or getattr(ctx, "login", None)
            password = self.Request.getParameter("password") or getattr(ctx, "password", None)

            if not self.WebApp.authorizeUser:
                raise httpauth.AuthError("no http user authenticator defined in webapp")
            if login:
                auth = self.WebApp.authorizeUser("loginpage", self.getURL(), login, password, self.Request)
                if auth is None:
                    time.sleep(2)  # to thwart brute-force password attacks
                else:
                    if isinstance(auth,LoginUser):
                        userobject = auth
                    else:
                        userobject = LoginUser(login,privileges=auth)
                    # user is okay! log in and go to the returnpage.
                    self.Request.getSession().loginUser(userobject)
                    del self.Request.getSessionContext()._SNKLOGIN_RETURNPAGE
                    if successfulLoginFunc:
                        successfulLoginFunc(userobject)
                    self.Yhttpredirect(MAINPAGE)
 