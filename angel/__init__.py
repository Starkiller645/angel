#!/usr/bin/env python3
# Import required libraries

import pytest
import sys
import time
import praw
import prawcore
import os
import webbrowser
import socket
import json
import requests
import io
import ffmpeg
import importlib

try:
    importlib.reload(angellib)
    from angellib import mainwindow
    from angellib import *
    from angellib.helpers import modprawini
except NameError:
    from angellib import mainwindow
    from angellib import *
    from angellib.helpers import modprawini

from wget import *
from PIL import Image, ImageOps

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngine import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

from test import *
try:
    import pkg_resources.py2_warn
except ImportError:
    pass

try:
    sys.stdout.write("\n")
    sys.stdout.flush()
except:
    class dummyStream:
        ''' dummyStream behaves like a stream but does nothing. '''
        def __init__(self): pass
        def write(self,data): pass
        def read(self,data): pass
        def flush(self): pass
        def close(self): pass
    # and now redirect all default streams to this dummyStream:
    sys.stdout = dummyStream()
    sys.stderr = dummyStream()
    sys.stdin = dummyStream()
    sys.__stdout__ = dummyStream()
    sys.__stderr__ = dummyStream()
    sys.__stdin__ = dummyStream()

if os.environ.get('DEBUG', '') == 'true':
    debug = True
else:
    debug = False
# Define global variable for environment
# Check if on Windows or UNIX-Like (Darwin or Linux)
if os.name != "posix":
    isWindows = True
else:
    isWindows = False
if debug:
    print(sys.platform)

if isWindows:
    envHome = os.environ.get('CSIDL_MYDOCUMENTS', '')
    if debug:
        print('[DBG] User home is {envHome}')

# Check if running headless for CI workflow
if os.environ.get("CI", "") == 'true':
    ci = True
else:
    ci = False

def receiveConnection():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 8080))
    server.listen(1)
    client = server.accept()[0]
    server.close()
    return client

# Get OS-specific env variables
envHome = os.environ.get("HOME", "")
appData = os.environ.get("APPDATA", "").replace("\\", "/")

# Initialise praw.ini file if it does not exist
if os.path.exists("{}/.config/praw.ini".format(envHome)) or os.path.exists("{}/praw.ini".format(appData)):
    if isWindows:
        with open("{}/praw.ini".format(appData)) as prawini:
            if "[DEFAULT]" in prawini.read():
                prawini.close()
                os.remove("{}/praw.ini".format(appData))
                modprawini.initPrawINI()
            else:
                prawiniExists = True
    else:
        with open("{}/.config/praw.ini".format(envHome)) as prawini:
            if "[DEFAULT]" in prawini.read():
                prawini.close()
                os.remove("{}/.config/praw.ini".format(envHome))
                modprawini.initPrawINI()
            else:
                prawiniExists = True
else:
    modprawini.initPrawINI()


# Start QApplication instance
app = QApplication(sys.argv)
app.setStyle('Fusion')
if isWindows:
    app.setWindowIcon(QIcon('{}/Angel/angel.ico'.format(appData)))
else:
    app.setWindowIcon(QIcon('/opt/angel-reddit/angel.ico'))

# Create error classes to handle timeout or 404 exceptions, etc.
class RequestTimeOut(QWidget):
    def __init__(self, *args, **kwargs):
        super(RequestTimeOut, self).__init__()
        self.mainLayout = QVBoxLayout()
        self.subLayout = QHBoxLayout()
        self.imageWidget = QLabel()
        self.headerWidget = QLabel()
        self.headerWidget.setStyleSheet('font-size: 40px;')
        self.headerWidget.setText('<b>Error</b> Request timed out')
        if isWindows:
            self.image = QPixmap('{}/Angel/error408'.format(appData))
        else:
            self.image = QPixmap('/opt/angel-reddit/error408')
        self.imageWidget.setPixmap(self.image)



# Add window widgets
mainThread = QCoreApplication.instance().thread()
window = mainwindow.MainWindow()
with open('/opt/angel-reddit/dark-theme.qss', "r") as stylesheet:
    window.setStyleSheet(stylesheet.read())
window.show()

# Start event loop
app.exec_()
