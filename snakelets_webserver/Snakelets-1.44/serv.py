#! /usr/bin/env python

import snakeserver.server
import os,sys,time

HTTPD_PORT = 9080
RUNAS_USER = None # "www"
RUNAS_GROUP = None # "www"

#import psyco
#psyco.full()


# ---enable this to see possible memory leaks---
# import gc
# gc.set_debug(gc.DEBUG_LEAK)

def main(workingdir=None):

    if workingdir:
        os.chdir(workingdir)

    print >>sys.stderr,"%s GMT: serv.py is starting the snakelet server." % time.asctime(time.gmtime())

    snakeserver.server.main(
        HTTPD_PORT=HTTPD_PORT,
        bindname=None,
        externalPort=HTTPD_PORT,
        serverURLprefix='',
        debugRequests=False,
        precompileYPages=True,
        writePageSource=False,
        serverRootDir=None,
        runAsUser=RUNAS_USER,
        runAsGroup=RUNAS_GROUP
        )

if __name__=="__main__":
    main()

