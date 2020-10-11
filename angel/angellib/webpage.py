#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtWebEngine import *
from PyQt5.QtWebEngineWidgets import QWebEngineView

class WebPageView(QWebEngineView):
    def __init__(self, url):
        super().__init__()
        self.load(QUrl(url))
        self.show()
