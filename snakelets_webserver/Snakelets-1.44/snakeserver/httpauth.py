#############################################################################
#
#	$Id: httpauth.py,v 1.1 2007/11/25 05:37:47 streapy Exp $
#	HTTP authentication logic
#
#	This is part of "Snakelets" - Python Web Application Server
#	which is (c) Irmen de Jong - irmen@users.sourceforge.net
#
#############################################################################

import md5
import sys

class AuthError(Exception): pass
class WrongPassword(AuthError): pass

#
#   Perform HTTP authentication.
#    params:
#   request, response: snakelet request, response objects.
#   authorizeUserPasswordFunc: callback function func(method, url, username, passwd, request)
#       that must return True or False indicating if the user+passwd is correct.
#   authMethod: authentication method to use. "httpbasic" or "httpdigest"
#       (only "httpbasic" is implemented right now)
#   authRealm: optional 'realm' string to use in the password dialog.
#
#   AUTH OK --> returns (authorized user name, password, set-of-privileges)
#   AUTH FAILED --> has prepared the response for HTTP authentication headers,
#           and raises AuthError
#
def HTTPauthenticate(request, response, url, authorizeUserPasswordFunc, authMethod="httpbasic", authRealm=None):
    try:
        # first try and see if the browser sent us some authorization headers,
        # if so, process these to try to authorize the user.
        auth=request.getAuth() # 'Authorization' header from http request
        if not auth:
            raise AuthError('browser needs to supply authentication information for this URL')  # no auth provided.
        
        (scheme, digest) = auth.split(' ',1)
        if scheme.lower()=='basic':     # Basic authentication 
            try:
                (username, password)=digest.decode('base-64').split(':')
                try:
                    privileges = authorizeUserPasswordFunc("httpbasic", url, username, password, request)
                    if privileges is not None:
                        return username,password,privileges  # successful authentication!!!
                except Exception,x:
                    print >>sys.stderr, "error during passwd check:",x
                    # raise AuthError("error during passwd check: "+str(x))
                    raise
                raise WrongPassword('invalid username or password')
            except ValueError:
                raise AuthError('invalid digest string')

        elif scheme.lower()=='digest':
            raise NotImplementedError("digest auth method not yet supported")
            # XXX the code below is unfinished and also BROKEN!!!
            digest=[d.strip() for d in digest.split(',')]
            dig={}
            for digestitem in digest:
                (name,value) = digestitem.split('=')
                if value.startswith('"') and value.endswith('"'):
                    value=value[1:-1]
                dig[name.lower()]=value
            # print dig
            
            if dig.get('algorithm') in (None, 'md5', 'MD5'):
                hA1=md5.new(dig['username']+":"+dig['realm']+":"+"password").hexdigest()
            elif dig['algorithm'].lower() == 'md5-sess':
                hA1=md5.new(hA1+":"+dig['nonce']+":"+dig['cnonce']).hexdigest()
            else:
                raise AuthError('invalid algorithm: '+dig['algorithm'])
            if dig.get('qop') in (None, 'auth','Auth'):
                hA2=md5.new(request.getMethod()+ ":" + dig['uri']).hexdigest()
            else:
                raise AuthError('non-supported QOP: '+dig['qop'])
            if dig['qop'].lower() == "auth":
                computed_request_digest  = md5.new( hA1+dig['nonce']+':'+dig['nc']+':'+dig['cnonce']+':'+dig['qop']+':'+hA2 ).hexdigest()
            else:
                computed_request_digest  = md5.new( hA1+dig['nonce']+":"+hA2 ).hexdigest()
            # print "computed_request_digest=",computed_request_digest
            if computed_request_digest!=dig['response']:
                raise AuthError("Invalid Authentication") # invalid user/password/whatever...
            try:
                privileges = authorizeUserPasswordFunc("httpdigest", url, username, password, request)
                if privileges is not None:
                    return dig['username'],computed_request_digest,privileges # Successful authentication
            except Exception,x:
                print >>sys.stderr, "error during passwd check:",x
                # raise AuthError("error during passwd check: "+str(x))
                raise
            raise WrongPassword("Invalid Authentication") # invalid user/password/whatever...
        else:
            raise AuthError('unsupport auth method: '+scheme) # not supported....

    except AuthError,x:
        # Something went wrong with authenticating the user.
        # Send HTTP authentication headers.
        if authMethod=="httpbasic":         # Basic authentication
            name = authRealm or request.getWebApp().getName()[1] or "Web application"
            response.setHeader("WWW-Authenticate","Basic realm=\""+name+"\"")
            response.sendError(401) # AUTHORIZATION REQUIRED
            raise
        elif authMethod=="httpdigest":      # Digest authentication
            raise NotImplementedError("digest auth method not yet supported")
            # XXX not yet implemented...
            # --- Digest auth, not correctly supported by all browsers
            #     also the server implementation above is still broken... :(
            #domain = authDomain or "/" # XXX ???
            #realm = (request.getWebApp().getName()[1] or "Web Application") + " @ "+request.getServerName()
            #nonce= "dcd98b7102dd2f0e8b11d0f600bfb0c093"
            #algorithm="MD5"
            #qop = "auth"
            #details = "Digest realm=\"%s\", domain=\"%s\", nonce=\"%s\", algorithm=\"%s\", qop=\"%s\"" % \
            #           (realm, domain, nonce, algorithm, qop)
            #response.setHeader("WWW-Authenticate", details)
            #response.sendError(401)    # AUTHORIZATION REQUIRED
        else:
            raise ValueError("unknown auth method "+authMethod)
            
    assert False, "should not reach this"

