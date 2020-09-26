#!/usr/bin/python3
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
from PIL import Image, ImageOps
import requests
import io
import ffmpeg
from wget import *
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

def initPrawINI():
    if isWindows:
        prawini = open("{}/praw.ini".format(os.environ.get("APPDATA", "").replace("\\", "/")), "w+")
    else:
        prawini = open("{}/.config/praw.ini".format(envHome), "w+")
    prawini.write('[angel]\n')
    prawini.write('client_id=Jq0BiuUeIrsr3A\nclient_secret=None\nredirect_uri=http://localhost:8080\nuser_agent=Angel for Reddit (by /u/Starkiller645)')
    prawini.close()
    prawiniExists = True

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
                initPrawINI()
            else:
                prawiniExists = True
    else:
        with open("{}/.config/praw.ini".format(envHome)) as prawini:
            if "[DEFAULT]" in prawini.read():
                prawini.close()
                os.remove("{}/.config/praw.ini".format(envHome))
                initPrawINI()
            else:
                prawiniExists = True
else:
    initPrawINI()


# Start QApplication instance
app = QApplication(sys.argv)
if sys.platform == "darwin":
    app.setStyle('Fusion')
if isWindows:
    app.setWindowIcon(QIcon('{}/Angel/angel.ico'.format(appData)))
else:
    app.setWindowIcon(QIcon('/opt/angel-reddit/angel.ico'))



class ThreadSignals(QObject):
    finished = pyqtSignal()
    passReddit = pyqtSignal(object)
    startLoadAnimation = pyqtSignal()
    passCode = pyqtSignal(str, object)
    videoPath = pyqtSignal(str)
    done = pyqtSignal()
    addVideoWidget = pyqtSignal(str)


class AuthorisationWorker(QRunnable):

    def __init__(self):
        super(AuthorisationWorker, self).__init__()
        self.signals = ThreadSignals()

    @pyqtSlot()
    def run(self):
        self.signals.startLoadAnimation.emit()

        # Threading debug code
        if debug:
            print('\n[THREAD] Started authorisation worker')

        # Instantiate Reddit class with basic values
        self.reddit = praw.Reddit(redirect_uri="http://localhost:8080", client_id="Jq0BiuUeIrsr3A", client_secret=None, user_agent="Angel for Reddit v0.5 (by /u/Starkiller645)")
        print('[DBG] Instantiated Reddit class')
        self.signals.passReddit.emit(self.reddit)
        print('[DBG] Quit authThread')
        # Receive data connection on localhost:8080
        print('[DBG] Receiving Reddit data')
        self.client = receiveConnection()
        data = self.client.recv(1024).decode("utf-8")
        param_tokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
        params = {
        key: value for (key, value) in [token.split("=") for token in param_tokens]
        }
        # Authorise to Reddit and initRedditassign to variable
        print('[DBG] Setup data done!')
        if debug:
            print('[DBG] AuthCode = ' + params["code"])

        self.signals.passCode.emit(params["code"], self.reddit)
        if debug:
            print('[THREAD] Done!\n')

class VideoWorker(QRunnable):
    def __init__(self, jsonUrl):
        super(VideoWorker, self).__init__()
        self.signals = ThreadSignals()
        self.jsonUrl = jsonUrl

    @pyqtSlot()
    def run(self):
        if isWindows:
            jsonFile = open('{}/Angel/temp/vid_json.json'.format(appData), 'wb')
        else:
            jsonFile = open('/opt/angel-reddit/temp/vid_json.json', 'wb')
        initRequest = requests.get(self.jsonUrl)
        request = initRequest.url
        request = request[:len(request) - 1]
        request += '.json'
        print(request)
        finalRequest = requests.get(request, headers = {"User-agent" : "Angel for Reddit (by /u/Starkiller645)"})
        jsonFile.write(finalRequest.content)
        jsonFile.close()
        if isWindows:
            jsonFile = open('{}/Angel/temp/vid_json.json'.format(appData), 'r')
        else:
            jsonFile = open('/opt/angel-reddit/temp/vid_json.json', 'r')
        parsedJson = json.loads(jsonFile.read())
        print(jsonFile.read())
        print(parsedJson)
        print(parsedJson[0]["data"]["children"][0]["data"]["secure_media"]["reddit_video"]["fallback_url"])
        rawUrl = parsedJson[0]["data"]["children"][0]["data"]["secure_media"]["reddit_video"]["fallback_url"]
        audioUrl = rawUrl[:rawUrl.rfind('/')] + '/audio'
        print(audioUrl)
        if isWindows:
            with open('{}/Angel/temp/.vid.mp4'.format(appData), 'wb') as video:
                data = requests.get(rawUrl)
                video.write(data.content)
        else:
            with open('/opt/angel-reddit/temp/.vid.mp4', 'wb') as video:
                data = requests.get(rawUrl)
                video.write(data.content)

        if isWindows:
            # FFmpeg is not easily available on windows, so for now there is no support for sound on this platform
            # In a later release we will add a different audio/video backend that supports windows and is installed
            # from PyPi
            self.videoPath = '{}/Angel/temp/.vid.mp4'.format(appData)
            self.signals.videoPath.emit(self.videoPath)
            self.signals.done.emit()
            self.signals.addVideoWidget.emit(self.videoPath)
        else:
            try:
                with open('/opt/angel-reddit/temp/.aud.mp4', 'wb') as audio:
                    data = requests.get(audioUrl, headers = {"User-agent" : "Angel for Reddit (by /u/Starkiller645)"})
                    audio.write(data.content)
            except:
                with open('/opt/angel-reddit/temp/.aud.mp4', 'wb') as audio:
                    audioUrl = rawUrl[:rawUrl.rfind('/')] + '/DASH_audio.mp4'
                    data = requests.get(audioUrl, headers = {"User-agent" : "Angel for Reddit (by /u/Starkiller645)"})
                    audio.write(data.content)
            audio = open('/opt/angel-reddit/temp/.aud.mp4', 'rt')
            try:
                if '?xml' not in audio.read():
                    video = ffmpeg.input('{}/Angel/temp/.vid.mp4'.format(appData))
                    audio = ffmpeg.input('{}/Angel/temp/.aud.mp4'.format(appData))
                    output = ffmpeg.output(video, audio, '{}/Angel/temp/combined.mp4'.format(appData), vcodec='copy', acodec='aac', strict='experimental')
                    self.videoPath = '{}/Angel/temp/combined.mp4'.format(appData)
                    self.signals.videoPath.emit(self.videoPath)
                    self.signals.done.emit()
                    self.signals.addVideoWidget.emit(self.videoPath)
            except:
                video = ffmpeg.input('{}/Angel/temp/.vid.mp4'.format(appData))
                audio = ffmpeg.input('{}/Angel/temp/.aud.mp4'.format(appData))
                output = ffmpeg.output(video, audio, '{}/Angel/temp/combined.mp4'.format(appData), vcodec='copy', acodec='aac', strict='experimental')
                self.videoPath = '{}/Angel/temp/combined.mp4'.format(appData)
                self.signals.videoPath.emit(self.videoPath)
                self.signals.done.emit()
                self.signals.addVideoWidget.emit(self.videoPath)
            audio = open('/opt/angel-reddit/temp/.aud.mp4', 'rt')
            try:
                if '?xml' in audio.read():
                    if debug:
                        print('[DBG] Error downloading audio for video\n[DBG] Trying again with new URL format')
                    raise OSError
                    pass
                else:
                    audio.close()
                    video = ffmpeg.input('/opt/angel-reddit/temp/.vid.mp4')
                    audio = ffmpeg.input('/opt/angel-reddit/temp/.aud.mp4')
                    output = ffmpeg.output(video, audio, '/opt/angel-reddit/temp/combined.mp4', vcodec='copy', acodec='aac', strict='experimental')
                    output.run(overwrite_output=True)
                    self.videoPath = '/opt/angel-reddit/temp/combined.mp4'
                    self.signals.videoPath.emit(self.videoPath)
                    self.signals.done.emit()
                    self.signals.addVideoWidget.emit(self.videoPath)
            except OSError:
                os.remove('/opt/angel-reddit/temp/.aud.mp4')
                audioUrl = rawUrl[:rawUrl.rfind('/')] + '/DASH_audio.mp4'
                if debug:
                    print('[DBG] Trying with new URL scheme\n{}'.format(audioUrl))
                with open('/opt/angel-reddit/temp/.aud.mp4', 'wb') as audio:
                    data = requests.get(audioUrl, headers = {"User-agent" : "Angel for Reddit (by /u/Starkiller645)"})
                    audio.write(data.content)
                    audio.close()
                    audio = open('/opt/angel-reddit/temp/.aud.mp4', 'rt')
                    try:
                        print(audio.read())
                    except UnicodeDecodeError:
                        requestFailed = False
                    else:
                        requestFailed = True
                    if requestFailed:
                        if debug:
                            print('[DBG] Error downloading audio for video')
                        self.videoPath = '/opt/angel-reddit/temp/.vid.mp4'
                        audio.close()
                        self.signals.videoPath.emit(self.videoPath)
                        self.signals.done.emit()
                        self.signals.addVideoWidget.emit(self.videoPath)
                    else:
                        audio.close()
                        video = ffmpeg.input('/opt/angel-reddit/temp/.vid.mp4')
                        audio = ffmpeg.input('/opt/angel-reddit/temp/.aud.mp4')
                        output = ffmpeg.output(video, audio, '/opt/angel-reddit/temp/combined.mp4', vcodec='copy', acodec='aac', strict='experimental')
                        output.run(overwrite_output=True)
                        self.videoPath = '/opt/angel-reddit/temp/combined.mp4'
                        self.signals.videoPath.emit(self.videoPath)
                        self.signals.done.emit()
                        self.signals.addVideoWidget.emit(self.videoPath)
            else:
                audio.close()
                self.videoPath = '/opt/angel-reddit/temp/.vid.mp4'
                self.signals.self.videoPath.emit(self.videoPath)
                self.signals.done.emit()
                self.signals.addVideoWidget.emit(self.videoPath)

class WebPageView(QWebEngineView):
    def __init__(self, url):
        super().__init__()
        self.load(QUrl(url))
        self.show()

# Create a custom widget class with an implementation of a unique identifier for the submission widgets
class IDWidget(QCommandLinkButton):
    def __init__(self, id=None, *args, **kwargs):
        super(IDWidget, self).__init__(*args, **kwargs)
        self.id = id

    def setID(self, id):
        self.id = id

    def getID(self):
        return self.id

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


def startAuth():
    window.loadingWidget.show()
    window.loadingGif.start()
    window.authThread.start()

# Define unit tests to run when building with Travis CI
# These are callable from the MainWindow class and test certain aspects
# of the program at certain times
def _test_prawini():
    if isWindows:
        assert os.path.exists("{}/praw.ini".format(appData)) == True
    else:
        assert os.path.exists("{}/.config/praw.ini".format(envHome)) == True

def _test_tempfiles():
    if isWindows:
        try:
            assert os.path.exists("{}/Angel/temp".format(appData))
        except AssertionError:
            try:
                os.mkdir("{}/Angel/temp".format(appData))
            except:
                raise AssertionError
    else:
        try:
            assert os.path.exists("/opt/angel-reddit/temp/") == True
        except AssertionError:
            try:
                os.mkdir("/opt/angel-reddit/temp/")
            except:
                raise AssertionError

def _test_assets():
    assetFiles = ["angel.ico", "angel.png", "default.png", "downvote.png", "imagelink.png", "link.png", "mask.png", "reddit.png", "text.png", "upvote.png"]
    for file in assetFiles:
        if isWindows:
            assert os.path.exists("{0}/Angel/{1}".format(appData, file))
        else:
            assert os.path.exists("/opt/angel-reddit/{}".format(file))

# Create a class inheriting from QMainWindow for the main window of the app
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        _test_assets()
        _test_prawini()
        self.loadingWidget = QLabel()
        self.initProgram()

    def runConnect(self):
        print('[DBG] Running runConnect')
        self.receiveThread = QThread()
        self.receive = AuthorisationWorker()
        self.receive.moveToThread(self.receiveThread)
        self.receiveThread.finished.connect(self.initUI)
        self.receiveThread.started.connect(self.receive.receiveRedditConnection)
        print('[DBG] Starting receiveThread')
        self.receiveThread.start()
        print('[DBG] Started receiveThread')
        self.webpage = WebPageView(self.worker.reddit.auth.url(["identity", "vote", "read", "mysubreddits", "history"], "...", "permanent"))

    def setVideoPath(self, videoPath):
        self.videoPath = videoPath

    def startLoadAnimation(self):
        if debug:
            print(self.loadingWidget)
        self.loadingWidget.show()
        self.loadingGif.start()

    def connectToReddit(self, authCode, Reddit):
        self.reddit = Reddit
        self.code = self.reddit.auth.authorize(authCode)
        self.redditUname = self.reddit.user.me()
        if debug:
            print("[DBG] AuthCode = " + self.code)
        self.webpage = None
        if isWindows:
            with open("{}/praw.ini".format(appData), "a") as prawini:
                prawini.write('\nrefresh_token={}'.format(self.code))
        else:
            with open("{}/.config/praw.ini".format(envHome), "a") as prawini:
                prawini.write('\nrefresh_token={}'.format(self.code))
        self.initUI()

    def openLoginPage(self, redditInstance):
        self.webpage = WebPageView(redditInstance.auth.url(["identity", "vote", "read", "mysubreddits", "history"], "...", "permanent"))

    def initProgram(self):
        self.loadingWidget = QLabel()
        submissionImage = None
        self.resize(1080, 640)
        label = QLabel()
        self.setWindowTitle('Angel v0.8')
        self.mainWidget = QWidget()

        # Setup
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        if isWindows:
            self.setWindowIcon(QIcon('{}/Angel/angel.ico'.format(appData)))
        else:
            self.setWindowIcon(QIcon('/opt/angel-reddit/angel.ico'))

        # Create login boxes
        loginBox = QVBoxLayout()

        loginBox.width = 300

        # Create angel pixmap
        if isWindows:
            pixmap = QPixmap('{}/Angel/angel.png'.format(appData))
        else:
            pixmap = QPixmap('/opt/angel-reddit/angel.png')
        pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio)
        label.setPixmap(pixmap)
        label.resize(300, 300)

        # Set alignment to center
        label.setAlignment(Qt.AlignCenter)

        # Add to loginBox
        loginBox.addWidget(label)
        loginBox.setAlignment(Qt.AlignCenter)

        if os.path.exists("{}/.config/praw.ini".format(envHome)) or os.path.exists("{}/praw.ini".format(appData)):
            if isWindows:
                with open("{}/praw.ini".format(appData)) as prawini:
                    if "[DEFAULT]" in prawini.read():
                        prawini.close()
                        os.remove("{}/praw.ini".format(appData))
                        initPrawINI()
                    else:
                        prawiniExists = True
            else:
                with open("{}/.config/praw.ini".format(envHome)) as prawini:
                    if "[DEFAULT]" in prawini.read():
                        os.remove("{}/.config/praw.ini".format(envHome))
                        prawini.close()
                        initPrawINI()
                    else:
                        prawiniExists = True
        else:
            initPrawINI()

        # Create login fields and enter button
        self.title = QLabel('Logging in...')
        if isWindows:
            with open("{}/praw.ini".format(appData), "rt") as prawini:
                if "refresh_token" in prawini.read():
                    self.reddit = praw.Reddit("angel")
                    self.redditUname = self.reddit.user.me()
                    prawini.close()
                    self.initUI()
                else:
                    self.title.setAlignment(Qt.AlignCenter)
                    self.uname = QLineEdit(placeholderText='Username')
                    self.uname.setFixedWidth(300)
                    self.uname.setAlignment(Qt.AlignCenter)
                    self.passwd = QLineEdit(placeholderText='Password')
                    self.passwd.setEchoMode(QLineEdit.Password)
                    self.passwd.setFixedWidth(300)
                    self.passwd.setAlignment(Qt.AlignCenter)
                    self.login = QPushButton()
                    self.login.setFixedWidth(300)
                    self.login.setFixedHeight(80)
                    if isWindows:
                        self.redditIcon = QIcon("{}/Angel/reddit.png".format(appData))
                    else:
                        self.redditIcon = QIcon("/opt/angel-reddit/reddit.png")
                    self.login.setIconSize(QSize(300, 85))
                    self.login.setIcon(self.redditIcon)
                    self.enterBox = QVBoxLayout()
                    self.enter = QPushButton('Browse without login')
                    self.enter.setFixedWidth(200)
                    self.noLogin = QRadioButton('Browse without login')
                    loginBox.addWidget(self.title)
                    loginBox.addWidget(self.login)
                    self.enterBox.addWidget(self.enter)
                    self.enterBox.setAlignment(Qt.AlignCenter)
                    self.enterWidget = QWidget()
                    self.enterWidget.setLayout(self.enterBox)
                    loginBox.addWidget(self.enterWidget)
                    self.loadingWidget = QLabel()
                    self.loadingGif = QMovie('/opt/angel-reddit/loading.gif')
                    self.loadingWidget.setMovie(self.loadingGif)
                    #self.loadingWidget.hide()
                    if debug:
                        print(self.loadingWidget)
                    loginBox.addWidget(self.loadingWidget)
                    # Qt5 connect syntax is object.valueThatIsConnected.connect(func.toConnectTo)
                    self.enter.clicked.connect(self.initAnonReddit)

                    # OK, this bit is tricky
                    # First we instantiate a QThreadPool to manage our threads
                    self.threadPool = QThreadPool()

                    # Then, we want to create an auth worker that will run as soon as we click the login button
                    # This should setup the basic Reddit instance, pass it to a lambda, and then listen for a data request
                    self.worker = AuthorisationWorker()

                    # Next we start the QThreadPool running when the login button is clicked
                    self.login.clicked.connect(lambda null: self.threadPool.start(self.worker))

                    # The worker should now be generating a basic reddit object, and will pass it through a signal to our lambda
                    self.worker.signals.passReddit.connect(self.openLoginPage)

                    # Once that is done, the worker should be listening on the correct port for the data from Reddit
                    # When it has received that, it will pass the auth code to a function that closes the webpage and connects to reddit
                    self.worker.signals.passCode.connect(self.connectToReddit)

                    # Hopefully, the connectToReddit function will have called initUI properly

                    # Set selected widget to be central, taking up the whole
                    # window by default
                    self.mainWidget.setLayout(loginBox)
                    self.setCentralWidget(self.mainWidget)
        else:
            with open("{}/.config/praw.ini".format(envHome), "rt") as prawini:
                if "refresh_token" in prawini.read():
                    self.reddit = praw.Reddit("angel")
                    self.redditUname = self.reddit.user.me()
                    prawini.close()
                    self.initUI()
                else:
                    if debug:
                        print('[DBG] Setting up login UI')
                    self.title.setAlignment(Qt.AlignCenter)
                    self.uname = QLineEdit(placeholderText='Username')
                    self.uname.setFixedWidth(300)
                    self.uname.setAlignment(Qt.AlignCenter)
                    self.passwd = QLineEdit(placeholderText='Password')
                    self.passwd.setEchoMode(QLineEdit.Password)
                    self.passwd.setFixedWidth(300)
                    self.passwd.setAlignment(Qt.AlignCenter)
                    self.login = QPushButton()
                    self.login.setFixedWidth(300)
                    self.login.setFixedHeight(80)
                    self.redditIcon = QIcon("/opt/angel-reddit/reddit.png")
                    self.login.setIconSize(QSize(300, 85))
                    self.login.setIcon(self.redditIcon)
                    self.enterBox = QVBoxLayout()
                    self.enter = QPushButton('Browse without login')
                    self.enter.setFixedWidth(200)
                    self.noLogin = QRadioButton('Browse without login')
                    loginBox.addWidget(self.title)
                    loginBox.addWidget(self.login)
                    self.enterBox.addWidget(self.enter)
                    self.enterBox.setAlignment(Qt.AlignCenter)
                    self.enterWidget = QWidget()
                    self.enterWidget.setLayout(self.enterBox)
                    loginBox.addWidget(self.enterWidget)
                    self.loadingGif = QMovie('/opt/angel-reddit/loading.gif')
                    self.loadingWidget.setMovie(self.loadingGif)
                    self.loadingWidget.setAlignment(Qt.AlignCenter)
                    self.loadingWidget.hide()
                    self.loadingGif.start()
                    loginBox.addWidget(self.loadingWidget)
                    # Qt5 connect syntax is object.valueThatIsConnected.connect(func.toConnectTo)
                    self.enter.clicked.connect(self.initAnonReddit)

                    # OK, this bit is tricky
                    # First we instantiate a QThreadPool to manage our threads
                    self.threadPool = QThreadPool()

                    # Then, we want to create an auth worker that will run as soon as we click the login button
                    # This should setup the basic Reddit instance, pass it to a lambda, and then listen for a data request
                    self.worker = AuthorisationWorker()
                    self.worker.__init__()

                    # Next we start the QThreadPool running when the login button is clicked
                    self.login.clicked.connect(lambda null: self.threadPool.start(self.worker))

                    # The worker should now be generating a basic reddit object, and will pass it through a signal to our lambda
                    self.worker.signals.passReddit.connect(self.openLoginPage)

                    # Once that is done, the worker should be listening on the correct port for the data from Reddit
                    # When it has received that, it will pass the auth code to a function that closes the webpage and connects to reddit
                    self.worker.signals.passCode.connect(self.connectToReddit)

                    # Hopefully, the connectToReddit function will have called initUI properly

                    # Set selected widget to be central, taking up the whole
                    # window by default
                    self.mainWidget.setLayout(loginBox)
                    self.setCentralWidget(self.mainWidget)
                    if ci:
                        print('[CI] Initialising anonymous praw.Reddit instance')
                        self.initAnonReddit()

    def openAuthUrl(self):
        webbrowser.open(self.reddit.auth.url(["identity"], "...", "permanent"))

    # Define a function to open a web socket to receive the access token from OAuth

    def fetchImage(self, url):
        image = requests.get(url)
        imageBytes = io.BytesIO(image.content)
        image = Image.open(imageBytes)
        if isWindows:
            image.save('{0}/Angel/temp/.img.{1}'.format(appData, image.format.lower()))
            return '{0}/Angel/temp/.img.{1}'.format(appData, image.format.lower())
        else:
            image.save('/opt/angel-reddit/temp/.img.{}'.format(image.format.lower()))
            return '/opt/angel-reddit/temp/.img.{}'.format(image.format.lower())

    def resourcePath(self, relative):
        return os.path.join(os.environ.get("_MEIPASS2", os.pathdef))

    def fetchImageUrl(self, sub):
        image = requests.get(url)
        imageBytes = io.BytesIO(image.content)
        image = Image.open(imageBytes)
        if isWindows:
            image.save('{0}/Angel/temp/.img.{1}'.format(appData, image.format.lower()))
            return '{0}/Angel/temp/.img.{1}'.format(appData, (image.format).abspath("."), relative)
        else:
            image.save('/opt/angel-reddit/temp/.img.{}'.format(image.format))
            return '/opt/angel-reddit/temp/.img.{}'.format((image.format).abspath("."), relative)

    def clearLayout(self, layout):
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()

    def getSubIcon(self, sub):
        if isWindows:
            mask = Image.open('{}/Angel/mask.png'.format(appData)).convert('L')
        else:
            mask = Image.open('/opt/angel-reddit/mask.png').convert('L')
        if 'http' in sub.icon_img:
            image = requests.get(sub.icon_img)
            imageBytes = io.BytesIO(image.content)
            image = Image.open(imageBytes)
            image = image.convert('RGBA')
            if debug:
                print(image.mode)
        else:
            if isWindows:
                image = Image.open('{}/Angel/default.png'.format(appData))
            else:
                image = Image.open('/opt/angel-reddit/default.png')
        output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
        output = output.convert('RGBA')
        output.putalpha(mask)
        _test_tempfiles()
        if isWindows:
            try:
                output.save('{0}/Angel/temp/.subimg.{1}'.format(appData, 'png'))
            except OSError:
                image = Image.open('{}/Angel/default.png'.format(appData, 'png'))
                output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
                output = output.convert('RGBA')
                output.putalpha(mask)
                output.save('{0}/Angel/temp/.subimg.{1}'.format(appData, 'png'))
                return '{0}/Angel/temp/.subimg.{1}'.format(appData, 'png')
            else:
                return '{0}/Angel/temp/.subimg.{1}'.format(appData, 'png')
        else:
            try:
                if debug:
                    print(output.mode)
                output.save('/opt/angel-reddit/temp/.subimg.png')
                return '/opt/angel-reddit/temp/.subimg.png'
            except OSError:
                image = Image.open('/opt/angel-reddit/default.png')
                output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
                output = output.convert('RGBA')
                output.putalpha(mask)
                _test_tempfiles()
                output.save('/opt/angel-reddit/temp/.subimg.png')
                return '/opt/angel-reddit/temp/.subimg.png'
            else:
                return '/opt/angel-reddit/temp/.subimg.png'

    def setSubMeta(self, sub):
        imgPath = self.getSubIcon(sub)
        self.subIconPixmap = QPixmap(imgPath)
        self.subIcon.setPixmap(self.subIconPixmap)
        self.subIcon.show()
        self.subHeader.setText(' r/' + sub.display_name)
        return

    def giveUpvote(self, post):
        if self.hasDownVoted == True:
            post.clear_vote()
            self.scre.setText(str(self.submissionScoreList[self.widgetNum]))
            self.hasDownVoted = False
            self.hasUpVoted = False
            return 0
        if self.hasUpVoted == True:
            return 0
        else:
            post.upvote()
            self.scre.setText(str(int(self.submissionScoreList[self.widgetNum]) + 1))
            self.hasUpVoted = True

    def giveDownvote(self, post):
        if self.hasUpVoted == True:
            post.clear_vote()
            self.scre.setText(str(self.submissionScoreList[self.widgetNum]))
            self.hasUpVoted = False
            self.hasDownVoted = False
            return 0
        if self.hasDownVoted == True:
            return 0
        else:
            post.downvote()
            self.scre.setText(str(int(self.submissionScoreList[self.widgetNum]) - 1))
            self.hasDownVoted = True

    def playVideo(self, videoPath):
        self.submissionVideo = QVideoWidget()
        self.mediaPath = videoPath
        self.media = QMediaPlayer()
        self.media.setMedia(QMediaContent(QUrl.fromLocalFile(videoPath)))
        self.media.setVideoOutput(self.submissionVideo)
        self.mainBody.setSizeConstraint(QLayout.SetNoConstraint)
        self.mainBodyWidget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.mainBodyWidget.setMinimumHeight(650)
        self.submissionVideo.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.submissionVideo.setMinimumHeight(120)
        self.submissionVideo.setMinimumWidth(200)
        self.mainBody.addWidget(self.submissionVideo)
        self.media.play()
        self.mainBody.addWidget(self.submissionVideo)
        self.mainBody.update()




    def view(self, id=False):
        self.hasDownVoted = False
        self.hasUpVoted = False
        if debug:
            print('[DBG] Started view function')
            print(self.sender())
        if id != False:
            self.widgetNum = id
        else:
            self.widgetNum = self.sender().getID()
        if debug:
            print("[DBG] Func arg ID is " + str(id))
            print("[DBG] self.widgetNum is " + str(self.widgetNum))
        self.mainLayout.removeWidget(self.viewWidget)
        if self.viewWidget is not None:
            self.viewWidget.deleteLater()
        self.viewWidget = None
        if self.scroll is not None:
            self.scroll.takeWidget()
        else:
            self.viewWidget = QWidget()
            self.viewLayout = QVBoxLayout()
            self.scroll = QScrollArea()
            self.scroll.setWidget(self.viewWidget)
            self.scroll.takeWidget()
            self.mainLayout.addWidget(self.scroll)
        self.viewWidget = QWidget()
        self.viewLayout = QVBoxLayout()
        self.mainBody = QVBoxLayout()
        self.mainBodyWidget = QWidget()
        self.urlLayout = QHBoxLayout()
        self.urlBar = QWidget()
        if debug:
            print('[DBG] Created viewWidget and layout and scroll widget')
        self.submissionTitle = QLabel()
        self.submissionTitle.setWordWrap(True)
        self.submissionTitle.setStyleSheet('font-size: 42px; font-weight: bold;')
        self.submissionTitle.setText(self.submissionTitleList[self.widgetNum])
        self.submissionTitle.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        if debug:
            print('[DBG] Created submission title widget')
        self.submissionAuthor = QLabel()
        self.submissionAuthor.setStyleSheet('font-size: 30px; font-style: italic;')
        self.submissionAuthor.setText('u/' + self.submissionAuthorList[self.widgetNum])
        self.submissionAuthor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        if debug:
            print('[DBG] Created submission author widget')
        self.submissionBody = QLabel()
        self.submissionBody.setWordWrap(True)
        self.submissionBody.setStyleSheet('font-size: 20px;')
        self.submissionBody.setText(self.submissionDescList[self.widgetNum])
        self.submissionBody.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        if debug:
            print('[DBG] Created submission body widget')
        if 'i.redd.it' in self.submissionImageUrl[self.widgetNum] or 'imgur.com' in self.submissionImageUrl[self.widgetNum]:
            submissionImage = QLabel()
            preimg = QPixmap(self.fetchImage(self.submissionImageUrl[self.widgetNum]))
            img = preimg.scaledToWidth(500)
            submissionImage.setPixmap(img)
            if debug:
                print('[DBG] Created pixmap for image')
            self.submissionVideo = None
        elif 'v.redd.it' in self.submissionImageUrl[self.widgetNum]:
            self.frame = QLabel()
            jsonUrl = self.submissionImageUrl[self.widgetNum]

            # More threading here
            self.threadpool = QThreadPool()

            # Create a QRunnable
            self.worker = VideoWorker(jsonUrl)

            # Start the thread running
            self.threadpool.start(self.worker)

            # Make a new local event loop to run while the video is processing, and start it
            self.localEventLoop = QEventLoop()
            if debug:
                print('[DBG] Starting new local event loop')
            #self.localEventLoop.exec()

            # Wait asynchronously for the video worker to stop.
            # When it is done, stop the local event loop
            self.worker.signals.done.connect(self.localEventLoop.quit)
            self.worker.signals.addVideoWidget.connect(self.playVideo)

            # Set the video path from a signal
            self.worker.signals.videoPath.connect(self.setVideoPath)
            submissionImage = None

        elif 'youtube.com' in self.submissionImageUrl[self.widgetNum]:
            self.submissionVideo = None
            self.submissionVideo = QWebEngineView()
            self.submissionVideo.page().settings().setAttribute(QWebEngineSettings.ShowScrollBars, False)
            ytEmbedUrl = self.submissionImageUrl[self.widgetNum].split("?v=")[1]
            print(ytEmbedUrl)
            ytEmbedUrl = ytEmbedUrl.split('&')[0]
            print(ytEmbedUrl)
            self.submissionVideo.setHtml("<!DOCTYPE html><html><head><style type=\"text/css\">body {{margin: 0}}</style></head><body><iframe id=\"ytplayer\" type=\"text/html\" width=\"636\" height=\"480\" src=\"https://youtube.com/embed/{}\"></body></html>".format(ytEmbedUrl))
            self.submissionVideo.setFixedWidth(648)
            self.submissionVideo.setFixedHeight(488)
            print('[DBG] Showing YT Video')
            submissionImage = None
        elif 'reddit.com' not in self.submissionImageUrl[self.widgetNum]:
            submissionImage = QLabel('<a href="{0}" >{0}</a>'.format(self.submissionImageUrl[self.widgetNum]))
            submissionImage.setOpenExternalLinks(True)
            submissionImage.setStyleSheet('font-size: 26px; color: skyblue;')
            submissionImage = None
            self.submissionVideo = None
        else:
            submissionImage = None
            self.submissionVideo = None
            if debug:
                print('[DBG] Set submissionImage to None')
        self.submissionUrl = QLabel()
        self.submissionUrl.setWordWrap(True)
        self.submissionUrl.setStyleSheet('font-size: 18px;')
        self.submissionUrl.setText('<a href=\"{}\">Link</a>'.format(self.submissionImageUrl[self.widgetNum]))
        self.submissionUrl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        if debug:
            print('[DBG] Submission image url is {}'.format(self.submissionImageUrl[self.widgetNum]))
            print('[DBG] Created submission URL widget')
        self.submissionScore = QWidget()

        # Set up Score (Combined up- and downvotes) widget, to be able to view upvotes
        self.upvoteLabel = QToolButton()
        self.downvoteLabel = QToolButton()
        if debug:
            print('[DBG] Creating score label')
        if isWindows:
            self.upvotePixmap = QIcon("{}/Angel/upvote.png".format(appData))
            self.downvotePixmap = QIcon("{}/Angel/downvote.png".format(appData))
        else:
            self.upvotePixmap = QIcon("/opt/angel-reddit/upvote.png")
            self.downvotePixmap = QIcon("/opt/angel-reddit/downvote.png")
        self.upvoteLabel.setIcon(self.upvotePixmap)
        self.downvoteLabel.setIcon(self.downvotePixmap)
        self.currentPost = praw.models.Submission(self.reddit, id=self.submissionIDList[self.widgetNum])
        self.upvoteLabel.clicked.connect(lambda null, sm=self.currentPost: self.giveUpvote(sm))
        self.downvoteLabel.clicked.connect(lambda null, sm=self.currentPost: self.giveDownvote(sm))
        if debug:
            print('[DBG] Set pixmap')
        self.scoreLayout = QHBoxLayout()
        self.scre = QLabel()
        if debug:
            print('[DBG] Created score widget')
        self.scre.setText("<b>{}</b>".format(self.submissionScoreList[self.widgetNum]))
        self.scre.setAlignment(Qt.AlignCenter)
        if debug:
            print('[DBG] Set text of score widget')
        self.scoreLayout.addWidget(self.upvoteLabel)
        self.scoreLayout.addWidget(self.scre)
        self.scoreLayout.addWidget(self.downvoteLabel)
        if debug:
            print('[DBG] Added widgets to score layout')
        self.submissionScore.setLayout(self.scoreLayout)
        self.submissionScore.setMaximumHeight(75)
        self.submissionScore.setMaximumWidth(200)
        if debug:
            print('[DBG] Created score widget')


        self.submissionUrl.setOpenExternalLinks(True)
        self.mainBody.addWidget(self.submissionTitle)
        self.mainBody.addWidget(self.submissionAuthor)
        if submissionImage is not None:
            self.mainBody.addWidget(submissionImage)
            submissionImage.show()
        if 'youtube.com' in self.submissionImageUrl[self.widgetNum]:
            self.mainBody.addWidget(self.submissionVideo)
        self.mainBody.addWidget(self.submissionBody)
        self.mainBodyWidget.setLayout(self.mainBody)
        self.scroll.setWidget(self.mainBodyWidget)
        self.urlLayout.addWidget(self.submissionUrl)
        self.urlBar.setLayout(self.urlLayout)
        self.viewLayout.addWidget(self.scroll)
        self.viewLayout.addWidget(self.submissionScore)
        self.viewWidget.setLayout(self.viewLayout)
        self.mainLayout.addWidget(self.viewWidget)
        if debug:
            print('[DBG] Added widgets to mainLayout and viewWidget')
        self.viewWidget.show()
        if debug:
            print('[DBG] Showing viewWidget')

    def showSubDesc(self):
        self.mainLayout.removeWidget(self.viewWidget)
        self.viewWidget.deleteLater()
        self.viewWidget = None
        self.viewWidget = QWidget()
        self.descWidget = QLabel(self.sub.description_html)
        self.descWidget.setTextFormat(Qt.RichText)
        self.descWidget.setOpenExternalLinks(True)
        self.scroll = QScrollArea()
        self.viewLayout = QVBoxLayout()
        self.scroll.setWidget(self.descWidget)
        self.viewLayout.addWidget(self.scroll)
        self.viewWidget.setLayout(self.viewLayout)
        self.mainLayout.addWidget(self.viewWidget)
        self.viewWidget.show()



    # Define function to switch between subreddits
    def switchSub(self, subreddit=None):
        if debug:
            print(subreddit)
        self.status.setText('Retrieving submissions')
        time.sleep(0.5)

        # Set up icons for the various post types
        if isWindows:
            self.textIcon = QIcon('{}/Angel/text.png'.format(appData))
            self.linkIcon = QIcon('{}/Angel/link.png'.format(appData))
            self.imageIcon = QIcon('{}/Angel/imagelink.png'.format(appData))
            self.videoIcon = QIcon('{}/Angel/video-mp4.png'.format(appData))
            self.ytIcon = QIcon('{}/Angel/video-yt.png'.format(appData))
        else:
            self.textIcon = QIcon('/opt/angel-reddit/text.png')
            self.linkIcon = QIcon('/opt/angel-reddit/link.png')
            self.imageIcon = QIcon('/opt/angel-reddit/imagelink.png')
            self.videoIcon = QIcon('/opt/angel-reddit/video-mp4.png')
            self.ytIcon = QIcon('/opt/angel-reddit/video-yt.png')
        if self.centralWidget() != self.window:
            self.setCentralWidget(self.window)
        self.clearLayout(self.subList)
        self.subList = QVBoxLayout()
        self.subredditBar = QWidget()
        if debug:
            print(subreddit)
        if subreddit != None and subreddit != True and subreddit != False:
            self.sub = self.reddit.subreddit(subreddit)
        else:
            self.sub = self.reddit.subreddit(self.searchSubs.text()[2:])
        self.submissionIDList, self.submissionTitleList, self.submissionDescList, self.submissionImageUrl, self.subWidgetList, self.submissionAuthorList, self.submissionScoreList = [], [], [], [], [], [], []
        self.i = 0
        try:
            for submission in self.sub.hot(limit=100):
                self.submissionIDList.append(submission.id)
                self.submissionTitleList.append(submission.title)
                self.submissionDescList.append(submission.selftext)
                self.submissionImageUrl.append(submission.url)
                self.submissionScoreList.append(submission.score)
                if submission.author is not None:
                    self.submissionAuthorList.append(submission.author.name)
                else:
                    self.submissionAuthorList.append('[deleted]')
                if len(submission.title) > 70:
                    self.subWidgetList.append(IDWidget(submission.title[:70] + '...', parent=self.subredditBar))
                else:
                    self.subWidgetList.append(IDWidget(submission.title))
                if debug:
                    print()
                self.i += 1

        except prawcore.exceptions.RequestException:
            self.wowSuchEmpty.setText('An error occurred - Read\noperation timed out')
            self.status.setText('Error - Timed out or sub does not exist')
        self.setSubMeta(self.sub)
        self.showSubDesc()
        if debug:
            print(self.subWidgetList)
        for self.i in range(len(self.submissionIDList)):
            if len(self.submissionDescList[self.i]) > 100:
                working = self.subWidgetList[self.i]
                self.subWidgetList[self.i].setDescription(self.submissionDescList[self.i][:100] + '...')
                if debug:
                    print('Getting submission #' + self.submissionIDList[self.i] + ': ' + self.submissionTitleList[self.i])
                    print('Set description of submission')
            else:
                if debug:
                    print('Getting submission #' + self.submissionIDList[self.i] + ': ' + self.submissionTitleList[self.i])
                self.subWidgetList[self.i].setDescription(self.submissionDescList[self.i])
                if debug:
                    print('Set description of submission')
            self.subWidgetList[self.i].show()
            self.subWidgetList[self.i].setID(id=self.i)
            self.subWidgetList[self.i].setText(self.submissionTitleList[self.i])
            if debug:
                print('Set text of submission')
            self.subWidgetList[self.i].clicked.connect(self.view)
            self.subList.addWidget(self.subWidgetList[self.i])
            if 'reddit.com' in self.submissionImageUrl[self.i]:
                self.subWidgetList[self.i].setIcon(self.textIcon)
            elif 'i.redd.it' in self.submissionImageUrl[self.i] or 'i.imgur.com' in self.submissionImageUrl[self.i]:
                self.subWidgetList[self.i].setIcon(self.imageIcon)
            elif 'v.redd.it' in self.submissionImageUrl[self.i]:
                self.subWidgetList[self.i].setIcon(self.videoIcon)
            elif 'youtube.com' in self.submissionImageUrl[self.i] or 'youtu.be' in self.submissionImageUrl[self.i]:
                self.subWidgetList[self.i].setIcon(self.ytIcon)
            else:
                self.subWidgetList[self.i].setIcon(self.linkIcon)
            if debug:
                print(self.subWidgetList[self.i].id)
            self.subredditBar.setLayout(self.subList)
            self.subWidgetList[self.i].setFixedHeight(100)
            self.subWidgetList[self.i].setFixedWidth(460)
            self.subScroll.setFixedWidth(500)
            self.subScroll.setWidget(self.subredditBar)
            self.subScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.subScroll.setWidgetResizable(True)
            self.subWidgetList[self.i].show()
            time.sleep(0.01)
        try:
            self.status.setText('/u/' + str(self.redditUname))
        except AttributeError:
            self.status.setText('Connected to Reddit')



    # Define function to instantiate an anonymous instance of the PRAW Reddit class
    def initAnonReddit(self):
        # Instantiate Reddit object
        loggedIn = False
        self.title.setText('Attempting to connect to reddit')
        self.reddit = praw.Reddit(redirect_uri="http://localhost:8080", client_id="Jq0BiuUeIrsr3A", client_secret=None, user_agent="Angel for Reddit v0.5 (by /u/Starkiller645)")
        if debug:
            print(self.reddit)
            print(self.reddit.auth.url(["identity", "vote", "read", "mysubreddits", "history"], "...", "permanent"))
        self.initUI()


    def createMenu(self, dictionary, menu):
        if isinstance(dictionary, list):
            for entry in dictionary:
                self.createMenu(entry, menu)
        elif isinstance(dictionary, dict):
            for key, value in dictionary.items():
                subMenu = QMenu(key, menu)
                menu.addMenu(subMenu)
                self.createMenu(value, subMenu)
        else:
            action = menu.addAction(dictionary)
            action.setIconVisibleInMenu(False)
        return 0

    def createSubMenu(self):
        self.subListRaw = list(self.reddit.user.subreddits(limit=None))
        self.subMenu = QMenu()
        self.subredditList = []
        for subreddit in self.subListRaw:
            self.subredditList.append(subreddit.display_name)
            if debug:
                print("[DBG] " + subreddit.display_name)
        if debug:
            print(self.subredditList)
        i = 0
        for currentSub in self.subredditList:
            self.subMenu.addAction(currentSub)
            if debug:
                print(self.subMenu.actions()[i])
                print(self.subredditList[i])
                print(currentSub)
            self.subMenu.actions()[i].triggered.connect(lambda null, s=currentSub: self.switchSub(s))
            i += 1
            if debug:
                print(i)



    # Function for logging out of the program
    def logOut(self):
        try:
            if isWindows:
                os.remove("{}/praw.ini".format(appData))
            else:
                os.remove("{}/.config/praw.ini".format(envHome))
        except OSError:
            if debug:
                print("[ERR] praw.ini does not exist, so cannot be deleted\n[ERR] Please check /opt/angel-reddit on POSIX OSes or\n[ERR] %APPDATA%/Angel on Win10")
        finally:
            self.toolbar.close()
            self.toolbar.deleteLater()
            self.initProgram()


    def widgetUp(self):
        self.widgetNum += 1
        self.view(self.widgetNum)

    def widgetDown(self):
        self.widgetNum -= 1
        self.view(self.widgetNum)


    # Function call to initialise the main UI of the program
    def initUI(self):
        # Begin to set up toolbar
        self.webpage = None
        self.searchSubs = QLineEdit(placeholderText="r/subreddit")
        try:
            if self.redditUname is not None:
                self.subListButton = QPushButton()
                self.subListButton.setMaximumWidth(25)
                self.createSubMenu()
                self.subListButton.setMenu(self.subMenu)
                self.subMenu.setShortcut("Ctrl+S")
                if debug:
                    print('[DBG] Added list of subs')
        except AttributeError:
            pass
        self.searchButton = QPushButton('Go')
        self.searchButton.setShortcut("Return")
        self.searchSubs.setMaximumWidth(500)
        self.searchSubs.setMinimumWidth(500)
        self.searchButton.setMaximumWidth(40)
        self.toolbar = QToolBar()
        self.hasUpVoted = False
        self.hasDownVoted = False
        if debug:
            print('[DBG] Set the left side of toolbar up')

        # Create null buttons for UP and DOWN keys
        self.widgetNum = 0
        self.nullUp = QPushButton()
        self.nullDown = QPushButton()
        self.nullUp.clicked.connect(self.widgetUp)
        self.nullDown.clicked.connect(self.widgetDown)
        self.nullUp.setShortcut("Up")
        self.nullDown.setShortcut("Down")

        # If user is logged in, display uname at top right
        if self.reddit.user.me() is not None:
            self.status = QLineEdit('/u/{}'.format(self.redditUname))
        else:
            self.status = QLineEdit('Connected to Reddit')

        # Set up the main UI box, including subreddit name and icons,
        # header and scroll areas
        # Set up status area
        self.status.setReadOnly(True)
        self.status.setAlignment(Qt.AlignRight)
        self.status.setMaximumWidth(175)
        self.status.setMinimumWidth(175)


        # Set up menu button
        self.menuButton = QPushButton("Menu")
        self.menu = QMenu()
        self.menuEntryArray = ["Logout", "Website"]
        self.createMenu(self.menuEntryArray, self.menu)
        self.menuButton.setMenu(self.menu)
        self.menu.actions()[0].triggered.connect(self.logOut)
        self.menu.actions()[1].triggered.connect(lambda null, page="https://github.com/Starkiller645/angel": webbrowser.open(page))
        if debug:
            print('[DBG] Set up right side of toolbar')

        # Finish setting up toolbar
        self.spacer1 = QWidget()
        self.spacer2 = QWidget()
        self.spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.spacer2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.subIcon = QLabel()
        if isWindows:
            self.subIconPixmap = QPixmap()
        else:
            self.subIconPixmap = QPixmap()
        if debug:
            print('[DBG] Set pixmaps')
        #self.subIcon.setPixmap(self.subIconPixmap)
        #self.subIcon.show()
        if debug:
            print('[DBG] Showing pixmaps')
        self.subHeader = QLabel('r/none')
        self.subHeader.setStyleSheet('font-weight: bold; font-size: 30px;')
        self.status.setAlignment(Qt.AlignCenter)
        self.addToolBar(self.toolbar)
        if debug:
            print('[DBG] Added toolbar')

        # Add widgets to toolbar
        self.toolbar.addWidget(self.searchSubs)
        self.toolbar.addWidget(self.searchButton)
        try:
            if self.redditUname is not None:
                self.toolbar.addWidget(self.subListButton)
        except AttributeError:
            pass
        self.toolbar.addWidget(self.spacer1)
        self.toolbar.addWidget(self.subIcon)
        self.toolbar.addWidget(self.subHeader)
        self.toolbar.addWidget(self.spacer2)
        self.toolbar.addWidget(self.status)
        self.toolbar.addWidget(self.menuButton)
        if debug:
            print('[DBG] Toolbar done!')

        # Set main layout
        self.mainLayout = QHBoxLayout()
        self.wowSuchEmpty = QLabel('Wow, such empty!')
        self.wowSuchEmpty.setAlignment(Qt.AlignCenter)
        self.window = QWidget()
        self.subList = QVBoxLayout()
        self.subredditBar = QWidget()
        self.subredditBar.setMaximumWidth(540)
        self.subredditBar.setMinimumWidth(540)
        self.subredditBar.setLayout(self.subList)
        self.subScroll = QScrollArea()
        self.subScroll.setWidget(self.subredditBar)
        self.subScroll.widgetResizable = True
        if debug:
            print('[DBG] Set main layout')

        # Set up left-side scroll area for the submission list
        if debug:
            print('[DBG] Setting up scroll area')
        self.scroll = QScrollArea()
        self.viewWidget = QLabel('Wow, such empty!')
        self.scroll.setWidget(self.subredditBar)
        self.mainLayout.addWidget(self.subScroll)
        self.window.setLayout(self.mainLayout)
        self.window.setStyleSheet('@import url("https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap"); font-family: Lato')
        if debug:
            print('[DBG] Setting central widget as window')
        self.setCentralWidget(self.window)
        if debug:
            print('[DBG] Set central widget as window')

        # Connect searchButton with subreddit switching function
        self.searchButton.clicked.connect(self.switchSub)
        if isWindows:
            return
        if ci:
            print('[CI] Triggering switchSub...')
            self.switchSub('announcements')
            print('[CI] Switched sub\n[CI] Triggering view...')
            self.view(id=1)
            time.sleep(10)
            print('[CI] Integration tests complete\n[CI] Stand by to exit...')
            time.sleep(0.5)
            os._exit(0)


# Add window widgets
mainThread = QCoreApplication.instance().thread()
window = MainWindow()
window.show()

# Start event loop
app.exec_()
