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
from PIL import Image, ImageOps
import requests
import io
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from test import *
try:
    import pkg_resources.py2_warn
except ImportError:
    pass

assert 1 == 1
# Define global variable for environment
# Check if on Windows or UNIX-Like (Darwin or Linux)
if os.name != "posix":
    isWindows = True
else:
    isWindows = False
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
        prawini = open("{}\\Angel\\praw.ini".format(os.environ.get("APPDATA", "")))
    else:
        prawini = open("{}/.config/praw.ini".format(envHome), "w+")
    prawini.write('[angel]\n')
    prawini.write('client_id=Jq0BiuUeIrsr3A\nclient_secret=None\nredirect_uri=http://localhost:8080\nuser_agent=Angel for Reddit (by /u/Starkiller645)')
    prawini.close()
    prawiniExists = True

# Get OS-specific env variables
envHome = os.environ.get("HOME", "")
appData = os.environ.get("APPDATA", "")

# Initialise praw.ini file if it does not exist
if os.path.exists("{}/.config/praw.ini".format(envHome)) or os.path.exists("{}\Angel\\\praw.ini".format(appData)):
    if isWindows:
        with open("{}\\Angel\\praw.ini".format(appData)) as prawini:
            if "[DEFAULT]" in prawini.read():
                prawini.close()
                os.remove("{}\\Angel\\praw.ini".format(appData))
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
    app.setWindowIcon(QIcon('{}\\Angel\\angel.ico'.format(appData)))
else:
    app.setWindowIcon(QIcon('/opt/angel-reddit/angel.ico'))


class AuthorisationWorker(QObject):
    done = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

    def initReddit(self):

        print(window.loadingWidget)
        window.loadingWidget.show()
        window.loadingGif.start()

        # Threading debug code
        print('\n[THREAD] Started authorisation worker')

        # Instantiate Reddit class with basic values
        MainWindow.reddit = praw.Reddit(redirect_uri="http://localhost:8080", client_id="Jq0BiuUeIrsr3A", client_secret=None, user_agent="Angel for Reddit v0.5 (by /u/Starkiller645)")

        # Open webpage to authorisation URL
        webbrowser.open(MainWindow.reddit.auth.url(["identity", "vote", "read", "mysubreddits", "history"], "...", "permanent"))

        # Receive data connection on localhost:8080
        MainWindow.client = receiveConnection()
        data = MainWindow.client.recv(1024).decode("utf-8")
        param_tokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
        params = {
        key: value for (key, value) in [token.split("=") for token in param_tokens]
        }

        # Authorise to Reddit and initRedditassign to variable
        MainWindow.code = MainWindow.reddit.auth.authorize(params["code"])
        print(MainWindow.code)

        # Add refresh token to praw.ini
        if isWindows:
            with open("{}\\Angel\\praw.ini".format(appData), "a") as prawini:
                prawini.write('\nrefresh_token={}'.format(MainWindow.code))
        else:
            with open("{}/.config/praw.ini".format(envHome), "a") as prawini:
                prawini.write('\nrefresh_token={}'.format(MainWindow.code))

        # Initilise UI and assign value to redditUname
        MainWindow.redditUname = MainWindow.reddit.user.me()
        self.done.emit(['one', 'two', 'three'])
        print('[THREAD] Done!\n')
        window.initUI()

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
            self.image = QPixmap('{}\\Angel\\error408'.format(appData))
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
    assert os.path.exists("{}/.config/praw.ini".format(envHome)) == True

def _test_tempfiles():
    assert os.path.exists("/opt/angel-reddit/temp/") == True

def _test_assets():
    assetFiles = ["angel.ico", "angel.png", "default.png", "downvote.png", "imagelink.png", "link.png", "mask.png", "reddit.png", "text.png", "upvote.png"]
    for file in assetFiles:
        assert os.path.exists("/opt/angel-reddit/{}".format(file))

# Create a class as a child of QMainWindow for the main window of the app
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        _test_assets()
        _test_prawini()
        self.loadingWidget = QLabel()
        self.initProgram()

    def initProgram(self):
        submissionImage = None
        self.resize(1080, 640)
        label = QLabel()
        self.setWindowTitle('Angel v0.6.3-beta')
        self.mainWidget = QWidget()

        # Setup
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        if isWindows:
            self.setWindowIcon(QIcon('{}\\Angel\\angel.ico'.format(appData)))
        else:
            self.setWindowIcon(QIcon('/opt/angel-reddit/angel.ico'))

        # Create login boxes
        loginBox = QVBoxLayout()

        loginBox.width = 300

        # Create angel pixmap
        if isWindows:
            pixmap = QPixmap('{}\\Angel\\angel.png'.format(appData))
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

        if os.path.exists("{}/.config/praw.ini".format(envHome)) or os.path.exists("{}\Angel\\\praw.ini".format(appData)):
            if isWindows:
                with open("{}\\Angel\\praw.ini".format(appData)) as prawini:
                    if "[DEFAULT]" in prawini.read():
                        prawini.close()
                        os.remove("{}\\Angel\\praw.ini".format(appData))
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
                        self.redditIcon = QIcon("{}\Angel\reddit.png".format(appData))
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
                    print(self.loadingWidget)
                    loginBox.addWidget(self.loadingWidget)
                    # Qt5 connect syntax is object.valueThatIsConnected.connect(func.toConnectTo)
                    self.enter.clicked.connect(self.initAnonReddit)
                    self.authThread = QThread(self)
                    self.worker = AuthorisationWorker()
                    self.worker.moveToThread(self.authThread)
                    self.worker.done.connect(self.initUI)
                    self.authThread.started.connect(self.worker.initReddit)
                    self.login.clicked.connect(self.authThread.start)
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
                    loginBox.addWidget(self.loadingWidget)
                    # Qt5 connect syntax is object.valueThatIsConnected.connect(func.toConnectTo)
                    self.enter.clicked.connect(self.initAnonReddit)
                    self.authThread = QThread(self)
                    print('[THREAD] Started auth thread')
                    self.worker = AuthorisationWorker()
                    self.worker.moveToThread(self.authThread)
                    self.worker.done.connect(self.initUI)
                    self.authThread.started.connect(self.worker.initReddit)
                    print('[THREAD] Waiting for start signal...')
                    self.login.clicked.connect(startAuth)
                    # Set selected widget to be central, taking up the whole
                    # window by default
                    self.mainWidget.setLayout(loginBox)
                    self.setCentralWidget(self.mainWidget)
                    if ci:
                        print('[CI] Initialising anonymous praw.Reddit instance')
                        self.initAnonReddit()

    def onButtonPress(self, s):
        print('click', s)

    def openAuthUrl(self):
        webbrowser.open(self.reddit.auth.url(["identity"], "...", "permanent"))

    # Define a function to open a web socket to receive the access token from OAuth

    def fetchImage(self, url):
        image = requests.get(url)
        imageBytes = io.BytesIO(image.content)
        image = Image.open(imageBytes)
        if isWindows:
            image.save('{0}\\Angel\\temp\\.img.{1}'.format(appData, image.format.lower()))
            return '{0}\\Angel\\temp\\.img.{1}'.format(appData, image.format.lower())
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
            image.save('{0}\\Angel\\temp\\.img.{1}'.format(appData, image.format.lower()))
            return '{0}\\Angel\\temp\\.img.{1}'.format(appData, (image.format).abspath("."), relative)
        else:
            image.save('/opt/angel-reddit/temp/.img.{}'.format(image.format))
            return '/opt/angel-reddit/temp/.img.{}'.format((image.format).abspath("."), relative)

    def clearLayout(self, layout):
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()

    def getSubIcon(self, sub):
        if isWindows:
            mask = Image.open('{}\\Angel\\mask.png'.format(appData)).convert('L')
        else:
            mask = Image.open('/opt/angel-reddit/mask.png').convert('L')
        if 'http' in sub.icon_img:
            image = requests.get(sub.icon_img)
            imageBytes = io.BytesIO(image.content)
            image = Image.open(imageBytes)
            image = image.convert('RGBA')
            print(image.mode)
        else:
            if isWindows:
                image = Image.open('{}\\Angel\\default.png'.format(appData))
            else:
                image = Image.open('/opt/angel-reddit/default.png')
        output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
        output = output.convert('RGBA')
        output.putalpha(mask)
        _test_tempfiles()
        if isWindows:
            try:
                output.save('{0}\\Angel\\temp\\.subimg.{1}'.format(appData))
            except OSError:
                image = Image.open('{}\\Angel\\default.png'.format(appData))
                output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
                output = output.convert('RGBA')
                output.putalpha(mask)
                output.save('{0}\\Angel\\temp\\.subimg.{1}'.format(appData))
                return '{0}\\Angel\\temp\\.subimg.{1}'.format(appData)
            else:
                return '{0}\\Angel\\temp\\.subimg.{1}'.format(appData)
        else:
            try:
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


    def view(self, id=False):
        self.hasDownVoted = False
        self.hasUpVoted = False
        print('[DBG] Started view function')
        print(self.sender())
        if id != False:
            self.widgetNum = id
        else:
            self.widgetNum = self.sender().getID()
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
        print('[DBG] Created viewWidget and layout and scroll widget')
        self.submissionTitle = QLabel()
        self.submissionTitle.setWordWrap(True)
        self.submissionTitle.setStyleSheet('font-size: 42px; font-weight: bold;')
        self.submissionTitle.setText(self.submissionTitleList[self.widgetNum])
        self.submissionTitle.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        print('[DBG] Created submission title widget')
        self.submissionAuthor = QLabel()
        self.submissionAuthor.setStyleSheet('font-size: 30px; font-style: italic;')
        self.submissionAuthor.setText('u/' + self.submissionAuthorList[self.widgetNum])
        self.submissionAuthor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        print('[DBG] Created submission author widget')
        self.submissionBody = QLabel()
        self.submissionBody.setWordWrap(True)
        self.submissionBody.setStyleSheet('font-size: 20px;')
        self.submissionBody.setText(self.submissionDescList[self.widgetNum])
        self.submissionBody.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        print('[DBG] Created submission body widget')
        if 'i.redd.it' in self.submissionImageUrl[self.widgetNum] or 'imgur.com' in self.submissionImageUrl[self.widgetNum]:
            submissionImage = QLabel()
            preimg = QPixmap(self.fetchImage(self.submissionImageUrl[self.widgetNum]))
            img = preimg.scaledToWidth(500)
            submissionImage.setPixmap(img)
            print('[DBG] Created pixmap for image')
        elif 'reddit.com' not in self.submissionImageUrl[self.widgetNum]:
            submissionImage = QLabel('<a href="{0}" >{0}</a>'.format(self.submissionImageUrl[self.widgetNum]))
            submissionImage.setOpenExternalLinks(True)
            submissionImage.setStyleSheet('font-size: 26px; color: skyblue;')
        else:
            submissionImage = None
            print('[DBG] Set submissionImage to None')
        self.submissionUrl = QLabel()
        self.submissionUrl.setWordWrap(True)
        self.submissionUrl.setStyleSheet('font-size: 18px;')
        self.submissionUrl.setText('<a href=\"{}\">Link</a>'.format(self.submissionImageUrl[self.widgetNum]))
        self.submissionUrl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        print('[DBG] Created submission URL widget')
        self.submissionScore = QWidget()

        # Set up Score (Combined up- and downvotes) widget, to be able to view upvotes
        self.upvoteLabel = QToolButton()
        self.downvoteLabel = QToolButton()
        print('[DBG] Creating score label')
        self.upvotePixmap = QIcon("/opt/angel-reddit/upvote.png")
        self.downvotePixmap = QIcon("/opt/angel-reddit/downvote.png")
        self.upvoteLabel.setIcon(self.upvotePixmap)
        self.downvoteLabel.setIcon(self.downvotePixmap)
        self.currentPost = praw.models.Submission(self.reddit, id=self.submissionIDList[self.widgetNum])
        self.upvoteLabel.clicked.connect(lambda null, sm=self.currentPost: self.giveUpvote(sm))
        self.downvoteLabel.clicked.connect(lambda null, sm=self.currentPost: self.giveDownvote(sm))
        print('[DBG] Set pixmap')
        self.scoreLayout = QHBoxLayout()
        self.scre = QLabel()
        print('[DBG] Created score widget')
        self.scre.setText("<b>{}</b>".format(self.submissionScoreList[self.widgetNum]))
        self.scre.setAlignment(Qt.AlignCenter)
        print('[DBG] Set text of score widget')
        self.scoreLayout.addWidget(self.upvoteLabel)
        self.scoreLayout.addWidget(self.scre)
        self.scoreLayout.addWidget(self.downvoteLabel)
        print('[DBG] Added widgets to score layout')
        self.submissionScore.setLayout(self.scoreLayout)
        self.submissionScore.setMaximumHeight(75)
        self.submissionScore.setMaximumWidth(200)
        print('[DBG] Created score widget')


        self.submissionUrl.setOpenExternalLinks(True)
        self.mainBody.addWidget(self.submissionTitle)
        self.mainBody.addWidget(self.submissionAuthor)
        if submissionImage is not None:
            self.mainBody.addWidget(submissionImage)
        self.mainBody.addWidget(self.submissionBody)
        self.mainBodyWidget.setLayout(self.mainBody)
        self.scroll.setWidget(self.mainBodyWidget)
        self.urlLayout.addWidget(self.submissionUrl)
        self.urlBar.setLayout(self.urlLayout)
        self.viewLayout.addWidget(self.scroll)
        self.viewLayout.addWidget(self.submissionScore)
        self.viewWidget.setLayout(self.viewLayout)
        self.mainLayout.addWidget(self.viewWidget)
        print('[DBG] Added widgets to mainLayout and viewWidget')
        self.viewWidget.show()
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
        print(subreddit)
        self.status.setText('Retrieving submissions')
        time.sleep(0.5)

        # Set up icons for the various post types
        if isWindows:
            self.textIcon = QIcon('{}\\Angel\\text.png')
            self.linkIcon = QIcon('{}\\Angel\\link.png')
            self.imageIcon = QIcon('{}\\Angel\\imagelink.png')
        else:
            self.textIcon = QIcon('/opt/angel-reddit/text.png')
            self.linkIcon = QIcon('/opt/angel-reddit/link.png')
            self.imageIcon = QIcon('/opt/angel-reddit/imagelink.png')
        if self.centralWidget() != self.window:
            self.setCentralWidget(self.window)
        self.clearLayout(self.subList)
        self.subList = QVBoxLayout()
        self.subredditBar = QWidget()
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
                print()
                self.i += 1

        except prawcore.exceptions.RequestException:
            self.wowSuchEmpty.setText('An error occurred - Read\noperation timed out')
            self.status.setText('Error - Timed out or sub does not exist')
        self.setSubMeta(self.sub)
        self.showSubDesc()
        print(self.subWidgetList)
        for self.i in range(len(self.submissionIDList)):
            if len(self.submissionDescList[self.i]) > 100:
                working = self.subWidgetList[self.i]
                self.subWidgetList[self.i].setDescription(self.submissionDescList[self.i][:100] + '...')
                print('Getting submission #' + self.submissionIDList[self.i] + ': ' + self.submissionTitleList[self.i])
                print('Set description of submission')
            else:
                print('Getting submission #' + self.submissionIDList[self.i] + ': ' + self.submissionTitleList[self.i])
                self.subWidgetList[self.i].setDescription(self.submissionDescList[self.i])
                print('Set description of submission')
            self.subWidgetList[self.i].show()
            self.subWidgetList[self.i].setID(id=self.i)
            self.subWidgetList[self.i].setText(self.submissionTitleList[self.i])
            print('Set text of submission')
            self.subWidgetList[self.i].clicked.connect(self.view)
            self.subList.addWidget(self.subWidgetList[self.i])
            if 'reddit.com' in self.submissionImageUrl[self.i]:
                self.subWidgetList[self.i].setIcon(self.textIcon)
            elif 'i.redd.it' in self.submissionImageUrl[self.i] or 'i.imgur.com' in self.submissionImageUrl[self.i]:
                self.subWidgetList[self.i].setIcon(self.imageIcon)
            else:
                self.subWidgetList[self.i].setIcon(self.linkIcon)
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

    def createSubMenu(self):
        self.subListRaw = list(self.reddit.user.subreddits(limit=None))
        self.subMenu = QMenu()
        self.subredditList = []
        for subreddit in self.subListRaw:
            self.subredditList.append(subreddit.display_name)
            print("[DBG] " + subreddit.display_name)
        print(self.subredditList)
        i = 0
        for currentSub in self.subredditList:
            self.subMenu.addAction(currentSub)
            print(self.subMenu.actions()[i])
            print(self.subredditList[i])
            print(currentSub)
            self.subMenu.actions()[i].triggered.connect(lambda null, s=currentSub: self.switchSub(s))
            i += 1
            print(i)



    # Function for logging out of the program
    def logOut(self):
        try:
            if isWindows:
                os.remove("{}\Angel\praw.ini".format(appData))
            else:
                os.remove("{}/.config/praw.ini".format(envHome))
        except OSError:
            print("[ERR] praw.ini does not exist, so cannot be deleted\n[ERR] Please check /opt/angel-reddit on POSIX OSes or\n[ERR] %APPDATA%\\Angel on Win10")
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
        self.searchSubs = QLineEdit(placeholderText="r/subreddit")
        try:
            if self.redditUname is not None:
                self.subListButton = QPushButton()
                self.subListButton.setMaximumWidth(25)
                self.createSubMenu()
                self.subListButton.setMenu(self.subMenu)
                self.subMenu.setShortcut("Ctrl+S")
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
        self.menu.triggered.connect(self.logOut)

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
        self.subIcon.setPixmap(self.subIconPixmap)
        self.subIcon.show()
        self.subHeader = QLabel('r/none')
        self.subHeader.setStyleSheet('font-weight: bold; font-size: 30px;')
        self.status.setAlignment(Qt.AlignCenter)
        self.addToolBar(self.toolbar)

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

        # Set up left-side scroll area for the submission list
        self.scroll = QScrollArea()
        self.viewWidget = QLabel('Wow, such empty!')
        self.scroll.setWidget(self.subredditBar)
        self.mainLayout.addWidget(self.subScroll)
        self.window.setLayout(self.mainLayout)
        self.window.setStyleSheet('@import url("https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap"); font-family: Lato')
        self.setCentralWidget(self.window)

        # Connect searchButton with subreddit switching function
        self.searchButton.clicked.connect(self.switchSub)
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
window = MainWindow()
window.show()

# Start event loop
app.exec_()
