#!/usr/bin/python3
# Import required libraries
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

# Define global variable for environment
# Check if on Windows or UNIX-Like (Darwin or Linux)
if os.name != "posix":
    isWindows = True
else:
    isWindows = False

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
if isWindows:
    app.setWindowIcon(QIcon('{}\\Angel\\angel.ico'.format(appData)))
else:
    app.setWindowIcon(QIcon('/opt/angel-reddit/angel.ico'))


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


# Create a class as a child of QMainWindow for the main window of the app
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        submissionImage = None
        self.resize(1080, 640)
        label = QLabel()
        self.setWindowTitle('Angel v0.5-beta')
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
                        self.redditIcon = QIcon("{}\\Angel\\reddit.png".format(appData))
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
                    # Qt5 connect syntax is object.valueThatIsConnected.connect(func.toConnectTo)
                    self.enter.clicked.connect(self.initAnonReddit)
                    self.login.clicked.connect(self.initReddit)
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
                    # Qt5 connect syntax is object.valueThatIsConnected.connect(func.toConnectTo)
                    self.enter.clicked.connect(self.initAnonReddit)
                    self.login.clicked.connect(self.initReddit)
                    # Set selected widget to be central, taking up the whole
                    # window by default
                    self.mainWidget.setLayout(loginBox)
                    self.setCentralWidget(self.mainWidget)

    def onButtonPress(self, s):
        print('click', s)

    def openAuthUrl(self):
        webbrowser.open(self.reddit.auth.url(["identity"], "...", "permanent"))

    # Define a function to open a web socket to receive the access token from OAuth
    def receiveConnection(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("localhost", 8080))
        server.listen(1)
        client = server.accept()[0]
        server.close()
        return client

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
        else:
            if isWindows:
                image = Image.open('{}\\Angel\\default.png'.format(appData))
            else:
                image = Image.open('/opt/angel-reddit/default.png')
        output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)
        if isWindows:
            output.save('{}\\Angel\\temp\\.subimg.png'.format(appData))
            return '{}\\Angel\\temp\\.subimg.png'.format(appData)
        else:
            output.save('/opt/angel-reddit/temp/.subimg.png')
            return '/opt/angel-reddit/temp/.subimg.png'

    def setSubMeta(self, sub):
        imgPath = self.getSubIcon(sub)
        self.subIconPixmap = QPixmap(imgPath)
        self.subIcon.setPixmap(self.subIconPixmap)
        self.subIcon.show()
        self.subHeader.setText(' r/' + sub.display_name)
        return

    def view(self):
        print('[DBG] Started view function')
        print(self.sender())
        widgetNum = self.sender().getID()
        self.mainLayout.removeWidget(self.viewWidget)
        self.viewWidget.deleteLater()
        self.viewWidget = None
        self.scroll.takeWidget()
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
        self.submissionTitle.setText(self.submissionTitleList[widgetNum])
        self.submissionTitle.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        print('[DBG] Created submission title widget')
        self.submissionAuthor = QLabel()
        self.submissionAuthor.setStyleSheet('font-size: 30px; font-style: italic;')
        self.submissionAuthor.setText('u/' + self.submissionAuthorList[widgetNum])
        self.submissionAuthor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        print('[DBG] Created submission author widget')
        self.submissionBody = QLabel()
        self.submissionBody.setWordWrap(True)
        self.submissionBody.setStyleSheet('font-size: 20px;')
        self.submissionBody.setText(self.submissionDescList[widgetNum])
        self.submissionBody.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        print('[DBG] Created submission body widget')
        if 'i.redd.it' in self.submissionImageUrl[widgetNum] or 'imgur.com' in self.submissionImageUrl[widgetNum]:
            submissionImage = QLabel()
            preimg = QPixmap(self.fetchImage(self.submissionImageUrl[widgetNum]))
            img = preimg.scaledToWidth(500)
            submissionImage.setPixmap(img)
            print('[DBG] Created pixmap for image')
        elif 'reddit.com' not in self.submissionImageUrl[widgetNum]:
            submissionImage = QLabel('<a href="{0}" >{0}</a>'.format(self.submissionImageUrl[widgetNum]))
            submissionImage.setOpenExternalLinks(True)
            submissionImage.setStyleSheet('font-size: 26px; color: skyblue;')
        else:
            submissionImage = None
            print('[DBG] Set submissionImage to None')
        self.submissionUrl = QLabel()
        self.submissionUrl.setWordWrap(True)
        self.submissionUrl.setStyleSheet('font-size: 18px;')
        self.submissionUrl.setText('<a href=\"{}\">Link</a>'.format(self.submissionImageUrl[widgetNum]))
        self.submissionUrl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        print('[DBG] Created submission URL widget')
        #self.submissionScore = QWidget()

        # Set up Score (Combined up- and downvotes) widget, to be able to view upvotes
        #self.scoreLabel = QLabel()
        #self.scorePixmap = QPixmap("/opt/angel-reddit/upvote.png")
        #self.scoreLabel.setPixmap(self.scorePixmap)
        #self.scoreLayout = QHBoxLayout()
        #self.scre = QLabel()
        #self.scre.setText("<b>{}</b>".format(self.submissionScoreList[widgetNum]))
        #self.scoreLayout.addWidget(self.scoreLabel)
        #self.scoreLayout.addWidget(self.scre)
        #self.scoreLabel.setLayout(self.scoreLayout)
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
        #self.viewLayout.addWidget(self.score)
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
    def switchSub(self):
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
            self.subScroll.setFixedWidth(480)
            self.subScroll.setFixedWidth(500)
            self.subScroll.setWidget(self.subredditBar)
            self.subScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.subScroll.setWidgetResizable(True)
            self.subWidgetList[self.i].show()
            time.sleep(0.01)
        self.status.setText('/u/' + str(self.redditUname))



    # Define function to instantiate an anonymous instance of the PRAW Reddit class
    def initAnonReddit(self):
        # Instantiate Reddit object
        loggedIn = False
        self.title.setText('Attempting to connect to reddit')
        self.reddit = praw.Reddit(redirect_uri="http://localhost:8080", client_id="Jq0BiuUeIrsr3A", client_secret=None, user_agent="Angel for Reddit v0.5 (by /u/Starkiller645)")
        print(self.reddit)
        print(self.reddit.auth.url(["identity", "read", "mysubreddits", "history"], "...", "permanent"))
        self.initUI()



    # Define fuction to instantiate the PRAW Reddit class
    def initReddit(self):

        # Instantiate Reddit class with basic values
        self.reddit = praw.Reddit(redirect_uri="http://localhost:8080", client_id="Jq0BiuUeIrsr3A", client_secret=None, user_agent="Angel for Reddit v0.5 (by /u/Starkiller645)")

        # Open webpage to authorisation URL
        webbrowser.open(self.reddit.auth.url(["identity", "read", "mysubreddits", "history"], "...", "permanent"))

        # Receive data connection on localhost:8080
        self.client = self.receiveConnection()
        data = self.client.recv(1024).decode("utf-8")
        param_tokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
        params = {
        key: value for (key, value) in [token.split("=") for token in param_tokens]
        }

        # Authorise to Reddit and assign to variable
        self.code = self.reddit.auth.authorize(params["code"])
        print(self.code)

        # Add refresh token to praw.ini
        if isWindows:
            with open("{}\\Angel\\praw.ini".format(appData), "a") as prawini:
                prawini.write('\nrefresh_token={}'.format(self.code))
        else:
            with open("{}/.config/praw.ini".format(envHome), "a") as prawini:
                prawini.write('\nrefresh_token={}'.format(self.code))

        # Initilise UI and assign value to redditUname
        self.redditUname = self.reddit.user.me()
        self.initUI()



    # Function call to initialise the main UI of the program
    def initUI(self):
        # Begin to set up toolbar
        self.searchSubs = QLineEdit(placeholderText="r/subreddit")
        self.searchButton = QPushButton('Go')
        self.searchSubs.setMaximumWidth(500)
        self.searchSubs.setMinimumWidth(500)
        self.searchButton.setMaximumWidth(40)
        self.toolbar = QToolBar()

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

        # Finish setting up toolbar
        self.spacer1 = QWidget()
        self.spacer2 = QWidget()
        self.spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.spacer2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.subIcon = QLabel()
        if isWindows:
            self.subIconPixmap = QPixmap('{}\\Angel\\default.png'.format(appData))
        else:
            self.subIconPixmap = QPixmap('/opt/angel-reddit/default.png')
        self.subIcon.setPixmap(self.subIconPixmap)
        self.subIcon.show()
        self.subHeader = QLabel('r/none')
        self.subHeader.setStyleSheet('font-weight: bold; font-size: 30px;')
        self.status.setAlignment(Qt.AlignCenter)
        self.addToolBar(self.toolbar)

        # Add widgets to toolbar
        self.toolbar.addWidget(self.searchSubs)
        self.toolbar.addWidget(self.searchButton)
        self.toolbar.addWidget(self.spacer1)
        self.toolbar.addWidget(self.subIcon)
        self.toolbar.addWidget(self.subHeader)
        self.toolbar.addWidget(self.spacer2)
        self.toolbar.addWidget(self.status)

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


# Add window widgets
window = MainWindow()
window.show()

# Start event loop
app.exec_()
