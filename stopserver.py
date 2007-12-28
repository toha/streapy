#!/usr/bin/python
import os, sys

try:
    pidfile = file(os.getcwd()+"/.streapypid","rt")
    pid = pidfile.read().rstrip("\n")
    pidfile.close()
except:
    print "Could not find the PID! Is streapy running?"
    sys.exit(1)

try:
    os.kill(int(pid),15)
except:
    print "Error while terminating streapy"
    sys.exit(1)