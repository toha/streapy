#############################################################################
#
#	$Id: util.py,v 1.1 2007/11/25 05:37:48 streapy Exp $
#	Utility code
#
#	This is part of "Snakelets" - Python Web Application Server
#	which is (c) Irmen de Jong - irmen@users.sourceforge.net
#
#############################################################################

import os


#
#   Utility class used to hold HTTP headers (case insensitive dict)
#   We need this to avoid duplicate headers.
#   Thankfully HTTP header fields are case-insensitive :-)
#
class NormalizedHeaderDict(dict):
    def __init__(self, *args):
        if len(args)==1 and type(args[0]) is dict:
            dict.__init__(self)
            d=args[0]
            for key in d:
                self[key.title()]=d[key]   # Titlecased
        else:
            dict.__init__(self, *args)
    def __contains__(self,key):
        return dict.__contains__(self,key.title())
    def __delitem__(self, item):
        return dict.__delitem__(self, item.title())
    def __getitem__(self,item):
        return dict.__getitem__(self, item.title())
    def __setitem__(self,item,value):
        return dict.__setitem__(self, item.title(), value)
    def get(self,item):
        return dict.get(self,item.title())
    def update(self,d):
        for key in d:
            self[key.title()]=d[key]
    def has_key(self,key):
        return dict.has_key(self,key.title())



#
#   just an empty class to store stuff into, it makes the 'context' storage of a snakelet.
#

class ContextContainer(object):
    pass



# Caching directory lister, outputs (filelist,dirlist) tuple.
# If modification time of the directory is different, re-read directory.
# If it's the same, return cached contents.
# Does not raise errors when the path cannot be found;
# returns empty lists in that case.

# Based upon dircache.py

_listdir_cache = {}

def listdir(path):
    try:
        cached_mtime, files, directories = _listdir_cache[path]
        del _listdir_cache[path]
    except KeyError:
        cached_mtime, files, directories = -1, [], []
    try:
        mtime = os.stat(path).st_mtime
    except os.error:
        return [],[]
    if mtime <> cached_mtime:
        try:
            lizt = os.listdir(path)
        except os.error:
            return [],[]
        files=[]
        directories=[]
        for e in lizt:
            if os.path.isdir(os.path.join(path,e)):
                directories.append(e)
            else:
                files.append(e)
    _listdir_cache[path] = mtime, files, directories
    return files,directories


def getCurrentUserAndGroupId():
    try:
        return os.getuid(), os.getgid()
    except Exception,x:
        return None

def getCurrentUserAndGroupName():
    cur=getCurrentUserAndGroupId()
    try:
        import pwd,grp
    except ImportError:
        return None
    else:
        curUserName = curGroupName = None
        if cur:
            curUserName = pwd.getpwuid(cur[0]).pw_name
            curGroupName = grp.getgrgid(cur[1]).gr_name
        return curUserName, curGroupName

    
def printCurrentUserAndGroupInfo():
    cur=getCurrentUserAndGroupId()
    cur_names=getCurrentUserAndGroupName()
    if cur:
        print "Current user/group: %s / %s" % (cur, cur_names)  
    else:
        print "Could not determine current user/group."

def changeUserAndGroup(userName, groupName):
    if groupName:
        try:
            import grp
        except ImportError:
            print "Your system doesn't support unix user groups."
        else:
            grpid = grp.getgrnam(groupName).gr_gid
            os.setgid(grpid)
    if userName:
        try:
            import pwd
        except ImportError:
            print "Your system doesn't support unix user ids."
        else:
            userid = pwd.getpwnam(userName).pw_uid
            os.setuid(userid)
