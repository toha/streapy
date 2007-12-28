#!/usr/bin/env python

"""Snakelets setup script"""

from distutils.core import setup
import sys,os

def main():
    if sys.argv[1].startswith("install"):
        print "There's nothing to install :-)"
        print "Just start the 'serv.py' script from this directory."
        print "(you can edit 'serv.py' for hostname/port settings)"
        print "On Unix? Have a look at monitor.py to run as a daemon."
        raise SystemExit

    setup(name="Snakelets",
            license="MIT",
            version="1.44",
            description = "Simple Python web application server with Snakelets and Python Server Pages",
            author = "Irmen de Jong",
            author_email="irmen@users.sourceforge.net",
            url = "http://snakelets.sourceforge.net/",
            long_description = """A simple to use Python web application server.  Provides web server, Python Server Pages and Snakelets (very similar to Java JSP/servlets).""",
            packages=['snakeserver','webapps'],
            scripts = ['serv.py'],
            platforms='any'
        )

if __name__=="__main__":
    main()
