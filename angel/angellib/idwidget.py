#!/usr/bin/env python3

from PyQt5.QtWidgets import QCommandLinkButton
from PyQt5.QtCore import *

class IDWidget(QCommandLinkButton):
    """Child class of QCommandLinkButton with an implementation of a unique ID,
    to aid in the identification of a specific widget within a list.

    Args:
        id (str): the ID with which to construct the ID
    """
    def __init__(self, id=None, *args, **kwargs):
        super(IDWidget, self).__init__(*args, **kwargs)
        self.id = id
        self.setAttribute(Qt.WA_Hover, True)
        self.clicked.connect(self.setBorderOrange)

    def setID(self, id):
        self.id = id

    def getID(self):
        return self.id

    def setBorderOrange(self, event=None):
        self.setStyleSheet('border-left: 3px solid #ff4500;')

    def setBorderNone(self, event=None):
        self.setStyleSheet('border-left: none;')
