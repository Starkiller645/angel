#!/usr/bin/env python3
# Class file containing PyQt5 threading signals

from PyQt5.QtCore import *

class ThreadSignals(QObject):
    finished = pyqtSignal()
    passReddit = pyqtSignal(object)
    startLoadAnimation = pyqtSignal()
    passCode = pyqtSignal(str, object)
    videoPath = pyqtSignal(str)
    done = pyqtSignal()
    addVideoWidget = pyqtSignal(str)
