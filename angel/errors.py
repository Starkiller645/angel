#!/bin/python3
# This is a library file for all of the status messages designed to be shown in the view window
# It currently includes:
# RequestTimeOut class
# Error403 class
# Error404 class


from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class RequestTimeOut(QWidget):
    def __init__(self, *args, **kwargs):
        super(RequestTimeOut, self).__init__()
        self.mainLayout = QVBoxLayout()
        self.subLayout = QHBoxLayout()
        self.imageWidget = QLabel()
        self.headerWidget = QLabel()
        self.headerWidget.setStyleSheet('font-size: 40px;')
        self.headerWidget.setText('<b>Error</b> Request timed out')
        self.image = QPixmap('/opt/angel-reddit/error408')
        self.imageWidget.setPixmap(self.image)
