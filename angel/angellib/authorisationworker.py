#!/usr/bin/env python3

import socket
import praw
import os

from PyQt5.QtCore import QRunnable, pyqtSlot
from angellib import threadsignals

class AuthorisationWorker(QRunnable):

    def __init__(self):
        super(AuthorisationWorker, self).__init__()
        self.signals = threadsignals.ThreadSignals()

    def receiveConnection(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("localhost", 8080))
        server.listen(1)
        client = server.accept()[0]
        server.close()
        return client

    @pyqtSlot()
    def run(self):
        self.signals.startLoadAnimation.emit()

        # Threading debug code
        if os.environ.get("DEBUG", "") == 'true':
            print('\n[THREAD] Started authorisation worker')

        # Instantiate Reddit class with basic values
        self.reddit = praw.Reddit(redirect_uri="http://localhost:8080", client_id="Jq0BiuUeIrsr3A", client_secret=None, user_agent="Angel for Reddit v0.5 (by /u/Starkiller645)")
        print('[DBG] Instantiated Reddit class')
        self.signals.passReddit.emit(self.reddit)
        print('[DBG] Quit authThread')
        # Receive data connection on localhost:8080
        print('[DBG] Receiving Reddit data')
        self.client = self.receiveConnection()
        data = self.client.recv(1024).decode("utf-8")
        param_tokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
        params = {
        key: value for (key, value) in [token.split("=") for token in param_tokens]
        }
        # Authorise to Reddit and initRedditassign to variable
        print('[DBG] Setup data done!')
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] AuthCode = ' + params["code"])

        self.signals.passCode.emit(params["code"], self.reddit)
        if os.environ.get("DEBUG", "") == 'true':
            print('[THREAD] Done!\n')
