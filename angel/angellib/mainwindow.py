#!/usr/bin/env python3

import praw, prawcore
import time

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
import importlib

try:
    importlib.reload(angellib)
    from angellib import *
    from angellib.helpers import *
except NameError:
    from angellib import *
    from angellib.helpers import *

import os
import sys
import gc


class MainWindow(QMainWindow):
    """Child class of QMainWindow that contains most of the application's GUI code.
    It should contain only code that relies directly on the PyQt5 libraries, PRAW,
    and the standard python libraries, such as os and sys.
    All other code should be placed in files inside the angellib/helpers directory
    """
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        unittests._test_assets()
        unittests._test_prawini()
        self.viewWindow = QWidget()
        self.viewWindowLayout = QVBoxLayout()
        self.viewWindow.setLayout(self.viewWindowLayout)
        self.sideBar = QWidget()
        self.sideBarLayout = QVBoxLayout()
        self.sideBar.setStyleSheet('background-color: #00ff00;')
        self.sideBar.setLayout(self.sideBarLayout)
        self.loadingWidget = QLabel()
        if os.name != "posix":
            self.runtimePrefix = "{}/Angel".format(os.environ.get('APPDATA', '').replace('\\', '/'))
        else:
            self.runtimePrefix = "/opt/angel-reddit"
        self.initProgram()

    def setVideoPath(self, videoPath):
        """Internal function to set the media path from a PyQt5 slot.
        Args:
            videoPath (str): The fully qualified path to a video file
        """

        self.mediaPath = videoPath

    def runConnect(self):
        """Function to setup the login window. Starts threads and opens QWebEngineView window.
        """

        print('[DBG] Running runConnect')
        self.receiveThread = QThread()
        self.receive = AuthorisationWorker()
        self.receive.moveToThread(self.receiveThread)
        self.receiveThread.finished.connect(self.initUI)
        self.receiveThread.started.connect(self.receive.receiveRedditConnection)
        print('[DBG] Starting receiveThread')
        self.receiveThread.start()
        print('[DBG] Started receiveThread')
        self.webpage = webpage.WebPageView(self.worker.reddit.auth.url(["identity", "vote", "read", "mysubreddits", "history"], "...", "permanent"))

    def startLoadAnimation(self):
        """Function to show and start a loading GIF. Used mainly to connect to PyQt5 signals.
        """
        if os.environ.get("DEBUG", "") == 'true':
            print(self.loadingWidget)
        self.loadingWidget.show()
        self.loadingGif.start()



    def connectToReddit(self, authCode, Reddit):
        """Follow-on function triggered by runConnect. Authenticates to Reddit with the token from receiveRedditConnection.

        Args:
            authCode (str): A valid Reddit authorisation code
            Reddit (praw.Reddit): A praw.Reddit instance to authenticate with

        """

        # Assign praw.Reddit instance to a class object and authorise with authCode
        if authCode == "failedwithkeyerror":
            self.worker = None
            self.worker = authorisationworker.AuthorisationWorker()
            self.worker.__init__()
            self.webpage = None
            self.worker.signals.passReddit.connect(self.openLoginPage)
            self.worker.signals.passCode.connect(self.connectToReddit)
            return
        self.reddit = Reddit
        self.code = self.reddit.auth.authorize(authCode)

        # Assign Reddit uname to a class object. Handle a raised RequestException gracefully, and finally delete the login window
        try:
            self.redditUname = self.reddit.user.me()
        except prawcore.exceptions.RequestException:
            self.errorWidget = QWidget()
            self.ohno = QLabel('Oh No!')
            self.ohno.setStyleSheet()
            self.errorWidget.addWidget()
        if os.environ.get("DEBUG", "") == 'true':
            print("[DBG] AuthCode = " + self.code)
        self.webpage = None

        # Write the authentication token to a praw.ini file, for future use
        if os.name != "posix":
            with open("{}/praw.ini".format(os.environ.get("APPDATA", "")), "a") as prawini:
                prawini.write('\nrefresh_token={}'.format(self.code))
        else:
            with open("{}/.config/praw.ini".format(os.environ.get("HOME", "")), "a") as prawini:
                prawini.write('\nrefresh_token={}'.format(self.code))

        # Call the initUI function which will set up the main interface
        self.initNewUI()



    def openLoginPage(self, redditInstance):
        """Function to open a login page, for better flow when signing in to Reddit

        Args:
            redditInstance (praw.Reddit): A praw.Reddit instance for which to open the authorisation URL

        """
        self.webpage = webpage.WebPageView(redditInstance.auth.url(["identity", "vote", "read", "mysubreddits", "history"], "...", "permanent"))



    def initProgram(self):
        if os.name != "posix":
            appData = os.environ.get('APPDATA', '')
            envHome = os.environ.get('CSIDL_MYDOCUMENTS', '')
        else:
            envHome = os.environ.get('HOME')
            appData = None
        self.loadingWidget = QLabel()
        submissionImage = None
        self.resize(1080, 640)
        label = QLabel()
        self.setWindowTitle('Angel v0.8')
        self.mainWidget = QWidget()

        # Find directory of running script, and set the window icon
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon('{}/angel.ico'.format(self.runtimePrefix)))

        # Create login box layout
        loginBox = QVBoxLayout()
        loginBox.width = 300

        # Create angel pixmap
        pixmap = QPixmap('{}/angel.png'.format(self.runtimePrefix))
        pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio)
        label.setPixmap(pixmap)
        label.resize(300, 300)

        # Set alignment to center
        label.setAlignment(Qt.AlignCenter)

        # Add to loginBox
        loginBox.addWidget(label)
        loginBox.setAlignment(Qt.AlignCenter)

        # Check if praw.ini already exists. If it is the default, or if it does not exist, remove it, and then call initPrawINI
        if os.path.exists("{}/.config/praw.ini".format(envHome)) or os.path.exists("{}/praw.ini".format(appData)):
            if "Angel" in self.runtimePrefix:
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
                        os.remove("{}/.config/praw.ini".format(envHome))
                        prawini.close()
                        modprawini.initPrawINI()
                    else:
                        prawiniExists = True
        else:
            modprawini.initPrawINI()

        # Create login fields and enter button
        self.title = QLabel('Logging in...')
        if os.name != "posix":
            prawini = open('{}/praw.ini'.format(appData))
        else:
            prawini = open('{}/.config/praw.ini'.format(envHome))

        if "refresh_token" in prawini.read():
            self.reddit = praw.Reddit("angel")
            self.redditUname = self.reddit.user.me()
            prawini.close()
            self.initNewUI()
        else:
            if os.environ.get("DEBUG", "") == 'true':
                print('[DBG] Setting up login UI')

            # This chunk of code is for setting up all of the widgets for login
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
            self.redditIcon = QIcon("{}/reddit.png".format(self.runtimePrefix))
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
            self.loadingGif = QMovie('{}/loading.gif'.format(self.runtimePrefix))
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
            self.worker = authorisationworker.AuthorisationWorker()
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
            if os.environ.get("CI", "") == 'true':
                print('[CI] Initialising anonymous praw.Reddit instance')
                self.initAnonReddit()

    def saveFile(self):
        filename = QFileDialog.getSaveFileName('Open file', envHome, 'Media files (*.jpg *.png *.mp4 *.jpeg *.gif)')
        input = self.mediaPath
        if os.environ.get("DEBUG", "") == 'true':
            print(filename)
            print(input)
        with open(input, 'rb') as inputFile:
            file = open(filename[0], 'wb')
            fileContents = inputFile.read()
            file.write(fileContents)
            file.close()

    def fetchImage(self, url):
        image = requests.get(url)
        imageBytes = io.BytesIO(image.content)
        image = Image.open(imageBytes)
        image.save('{0}/temp/.img.{1}'.format(self.runtimePrefix, image.format.lower()))
        return '{0}/temp/.img.{1}'.format(self.runtimePrefix, image.format.lower())

    def resourcePath(self, relative):
        return os.path.join(os.environ.get("_MEIPASS2", os.pathdef))

    def clearLayout(self, layout):
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()

    def getSubIcon(self, sub):
        mask = Image.open('{}/mask.png'.format(self.runtimePrefix)).convert('L')
        if 'http' in sub.icon_img:
            image = requests.get(sub.icon_img)
            imageBytes = io.BytesIO(image.content)
            image = Image.open(imageBytes)
            image = image.convert('RGBA')
            if os.environ.get("DEBUG", "") == 'true':
                print(image.mode)
        else:
            image = Image.open('{}/default.png'.format(self.runtimePrefix))
        output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
        output = output.convert('RGBA')
        output.putalpha(mask)
        unittests._test_tempfiles()
        try:
            output.save('{0}/temp/.subimg.{1}'.format(self.runtimePrefix, 'png'))
        except OSError:
            image = Image.open('{}/default.png'.format(self.runtimePrefix, 'png'))
            output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
            output = output.convert('RGBA')
            output.putalpha(mask)
            output.save('{0}/temp/.subimg.{1}'.format(self.runtimePrefix, 'png'))
            return '{0}/temp/.subimg.{1}'.format(self.runtimePrefix, 'png')
        else:
            return '{0}/temp/.subimg.{1}'.format(self.runtimePrefix, 'png')

    def setSubMeta(self, sub):
        imgPath = subicon.getSubIcon(sub)
        self.subIconPixmap = QPixmap(imgPath)
        self.subIcon.setPixmap(self.subIconPixmap)
        self.subIcon.show()
        self.subHeader.setText(' r/' + sub.display_name)
        self.subBarHeader.setText(' r/' + sub.display_name)
        return

    def giveUpvote(self, post):
        if self.hasDownVoted == True:
            post.clear_vote()
            self.scre.setText('<b>{}</b>'.format(str(self.submissionScoreList[self.widgetNum])))
            self.scre.setStyleSheet('color: #0f0f0f; font-weight: bold')
            self.hasDownVoted = False
            self.hasUpVoted = False
            return 0
        if self.hasUpVoted == True:
            return 0
        else:
            post.upvote()
            self.scre.setText(str(int(self.submissionScoreList[self.widgetNum]) + 1))
            self.scre.setStyleSheet('color: #ff4500; font-weight: bold;')
            self.hasUpVoted = True

    def giveDownvote(self, post):
        if self.hasUpVoted == True:
            post.clear_vote()
            self.scre.setText(str(self.submissionScoreList[self.widgetNum]))
            self.scre.setStyleSheet('color: #0f0f0f; font-weight: bold;')
            self.hasUpVoted = False
            self.hasDownVoted = False
            return 0
        if self.hasDownVoted == True:
            return 0
        else:
            post.downvote()
            self.scre.setText(str(int(self.submissionScoreList[self.widgetNum]) - 1))
            self.scre.setStyleSheet('color: #0079d3; font-weight: bold;')
            self.hasDownVoted = True

    def playVideo(self, videoPath):
        """Adds a video widget from a given video path

        Args:
            videoPath (str): The local path of the video file
        """
        self.submissionVideo = QVideoWidget()
        self.mediaPath = videoPath
        self.media = QMediaPlayer()
        self.media.setMedia(QMediaContent(QUrl.fromLocalFile(videoPath)))
        self.media.setVideoOutput(self.submissionVideo)
        self.mainBody.setSizeConstraint(QLayout.SetNoConstraint)
        self.mainBodyWidget.setMaximumWidth(self.width() - 600)
        self.mainBodyWidget.setFixedHeight(self.height() - 140)
        self.mainBodyWidget.setStyleSheet("padding-left: 0px;")
        self.submissionVideo.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.submissionVideo.setMinimumHeight(120)
        self.submissionVideo.setFixedWidth(self.mainBodyWidget.width())
        self.submissionVideo.setFixedHeight(self.mainBodyWidget.height() - 200)
        self.mainBody.addWidget(self.submissionVideo)
        self.media.play()
        self.mainBody.addWidget(self.submissionVideo)
        self.mainBody.update()

    def setVideoPath(self, path):
        self.mediaPath = path

    def viewImage(self, imagePath):
        self.submissionImage = QLabel()
        self.mediaPath = imagePath
        preimg = QPixmap(self.mediaPath)
        self.mainBodyWidget.setFixedHeight(self.height() - 140)
        print(self.mainBodyWidget.height())
        img = preimg.scaledToHeight(self.mainBodyWidget.height() - 150)
        self.submissionImage.setPixmap(img)
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Created pixmap for image')
        self.submissionVideo = None
        self.mainBody.addWidget(self.submissionImage)
        self.submissionImage.show()

    def view(self, id=False):

        self.hasDownVoted = False
        self.hasUpVoted = False
        if id != False:
            self.widgetNum = id
        else:
            self.widgetNum = self.sender().getID()
        for i in self.subWidgetList:
            i.setBorderNone()
        self.subWidgetList[self.widgetNum].setBorderOrange()
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Started view function')
            print(self.sender())
        if os.environ.get("DEBUG", "") == 'true':
            print("[DBG] Func arg ID is " + str(id))
            print("[DBG] self.widgetNum is " + str(self.widgetNum))
        #if self.viewWidget is not None:
            #self.viewWidget.deleteLater()
        #self.viewWidget = None
        try:
            if self.scroll is not None:
                self.scroll.takeWidget()
        except RuntimeError:
            self.viewWidget = QWidget()
            self.viewLayout = QVBoxLayout()
            self.scroll = QScrollArea()
            self.scroll.setWidget(self.viewWidget)
            self.scroll.takeWidget()
            self.viewWindowLayout.addWidget(self.scroll)
        self.viewWidget = QWidget()
        self.viewLayout = QVBoxLayout()
        self.mainBody = QVBoxLayout()
        self.mainBodyWidget = QWidget()
        self.mainBodyWidget.setMinimumWidth(self.width() - 600)
        self.urlLayout = QHBoxLayout()
        self.urlBar = QWidget()
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Created viewWidget and layout and scroll widget')
        self.submissionTitle = QLabel()
        self.submissionTitle.setWordWrap(True)
        self.submissionTitle.setStyleSheet('font-size: 42px; font-weight: bold;')
        self.submissionTitle.setText(self.submissionTitleList[self.widgetNum])
        self.submissionTitle.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Created submission title widget')
        self.submissionAuthor = QLabel()
        self.submissionAuthor.setStyleSheet('font-size: 30px; font-style: italic;')
        self.submissionAuthor.setText('u/' + self.submissionAuthorList[self.widgetNum])
        self.submissionAuthor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Created submission author widget')
        self.submissionBody = QLabel()
        self.submissionBody.setWordWrap(True)
        self.submissionBody.setStyleSheet('font-size: 20px;')
        self.mdtext = markdownparse.MarkdownText(self.submissionDescList[self.widgetNum])
        self.htmltext = self.mdtext.parse()
        self.submissionBody.setText(self.htmltext)
        self.submissionBody.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.submissionBody.setOpenExternalLinks(True)
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Created submission body widget')
        if 'i.redd.it' in self.submissionImageUrl[self.widgetNum] or 'imgur.com' in self.submissionImageUrl[self.widgetNum]:
            self.threadpool = QThreadPool()
            self.submissionImage = QLabel()
            self.worker = imageworker.ImageWorker(self.submissionImageUrl[self.widgetNum])
            self.threadpool.start(self.worker)
            self.worker.signals.returnImageLocation.connect(self.viewImage)

        elif 'v.redd.it' in self.submissionImageUrl[self.widgetNum]:
            self.frame = QLabel()
            jsonUrl = self.submissionImageUrl[self.widgetNum]

            # More threading here
            self.threadpool = QThreadPool()

            # Create a QRunnable
            self.worker = videoworker.VideoWorker(jsonUrl)

            # Start the thread running
            self.threadpool.start(self.worker)

            # Make a new local event loop to run while the video is processing, and start it
            self.localEventLoop = QEventLoop()
            if os.environ.get("DEBUG", "") == 'true':
                print('[DBG] Starting new local event loop')
            #self.localEventLoop.exec()

            # Wait asynchronously for the video worker to stop.
            # When it is done, stop the local event loop
            self.worker.signals.done.connect(self.localEventLoop.quit)
            self.worker.signals.addVideoWidget.connect(self.playVideo)

            # Set the video path from a signal
            self.worker.signals.videoPath.connect(self.setVideoPath)

        elif 'youtube.com' in self.submissionImageUrl[self.widgetNum] or 'youtu.be' in self.submissionImageUrl[self.widgetNum]:
            self.submissionVideo = None
            self.submissionVideo = QWebEngineView()
            self.submissionVideo.page().settings().setAttribute(QWebEngineSettings.ShowScrollBars, False)
            if 'youtu.be' in self.submissionImageUrl[self.widgetNum]:
                ytEmbedUrl = self.submissionImageUrl[self.widgetNum][self.submissionImageUrl[self.widgetNum].rfind('/'):]
                ytEmbedUrl = ytEmbedUrl[1:]
            else:
                try:
                    ytEmbedUrl = self.submissionImageUrl[self.widgetNum].split("?v=")[1]
                except IndexError:
                    ytEmbedUrl = self.submissionImageUrl[self.widgetNum][self.submissionImageUrl[self.widgetNum].rfind('/'):]
                    ytEmbedUrl = ytEmbedUrl[1:]
            print(ytEmbedUrl)
            ytEmbedUrl = ytEmbedUrl.split('&')[0]
            print(ytEmbedUrl)
            self.submissionVideo.setHtml("<!DOCTYPE html><html><head><style type=\"text/css\">body {{margin: 0}}</style></head><body><iframe id=\"ytplayer\" type=\"text/html\" width=\"636\" height=\"480\" src=\"https://youtube.com/embed/{}\"></body></html>".format(ytEmbedUrl))
            self.submissionVideo.setFixedWidth(648)
            self.submissionVideo.setFixedHeight(488)
            self.submissionVideo.show()
            print('[DBG] Showing YT Video')
            self.submissionImage = None
        elif 'reddit.com' not in self.submissionImageUrl[self.widgetNum]:
            self.submissionImage = webpage.WebPageView(self.submissionImageUrl[self.widgetNum])
            self.submissionImage.setFixedWidth(self.mainBodyWidget.width())
            self.submissionVideo = None
        else:
            self.submissionImage = None
            self.submissionVideo = None
            if os.environ.get("DEBUG", "") == 'true':
                print('[DBG] Set submissionImage to None')
        self.submissionUrl = QLabel()
        self.submissionUrl.setWordWrap(True)
        self.submissionUrl.setStyleSheet('font-size: 18px;')
        self.submissionUrl.setText('<a href=\"{}\">Link</a>'.format(self.submissionImageUrl[self.widgetNum]))
        self.submissionUrl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Submission image url is {}'.format(self.submissionImageUrl[self.widgetNum]))
            print('[DBG] Created submission URL widget')
        self.submissionScore = QWidget()

        self.saveWidget = QPushButton('Save File')
        self.saveWidget.setStyleSheet('color: #0f0f0f;')
        self.saveWidget.clicked.connect(lambda null: self.saveFile())

        # Set up Score (Combined up- and downvotes) widget, to be able to view upvotes
        self.upvoteLabel = QToolButton()
        self.downvoteLabel = QToolButton()
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Creating score label')
        self.upvotePixmap = QIcon("{}/upvote.png".format(self.runtimePrefix))
        self.downvotePixmap = QIcon("{}/downvote.png".format(self.runtimePrefix))
        self.upvoteLabel.setIcon(self.upvotePixmap)
        self.downvoteLabel.setIcon(self.downvotePixmap)
        self.currentPost = praw.models.Submission(self.reddit, id=self.submissionIDList[self.widgetNum])
        self.upvoteLabel.clicked.connect(lambda null, sm=self.currentPost: self.giveUpvote(sm))
        self.downvoteLabel.clicked.connect(lambda null, sm=self.currentPost: self.giveDownvote(sm))
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Set pixmap')
        self.scoreLayout = QHBoxLayout()
        self.scre = QLabel()
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Created score widget')
        self.scre.setText("<b>{}</b>".format(self.submissionScoreList[self.widgetNum]))
        self.scre.setStyleSheet('color: #0f0f0f;')
        self.scre.setAlignment(Qt.AlignCenter)
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Set text of score widget')
        self.scoreLayout.addWidget(self.upvoteLabel)
        self.scoreLayout.addWidget(self.scre)
        self.scoreLayout.addWidget(self.downvoteLabel)
        self.scoreLayout.addWidget(self.saveWidget)
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Added widgets to score layout')
        self.submissionScore.setLayout(self.scoreLayout)
        self.submissionScore.setMaximumHeight(75)
        self.submissionScore.setMaximumWidth(200)
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Created score widget')


        self.submissionUrl.setOpenExternalLinks(True)
        self.mainBody.addWidget(self.submissionTitle)
        self.mainBody.addWidget(self.submissionAuthor)
        self.mainBodyWidget.setLayout(self.mainBody)
        if 'youtube.com' in self.submissionImageUrl[self.widgetNum] or 'youtu.be' in self.submissionImageUrl[self.widgetNum]:
            self.mainBody.addWidget(self.submissionVideo)
        print(self.submissionImage)
        if 'reddit.com' not in self.submissionImageUrl[self.widgetNum]:
            self.mainBody.addWidget(self.submissionImage)
            if os.environ.get("DEBUG", "") == 'true':
                print(self.mainBodyWidget.height())
                print(self.submissionTitle.height())
                print(self.submissionAuthor.height())
        self.submissionImage.setFixedHeight(self.mainBodyWidget.height())

        self.mainBody.addWidget(self.submissionBody)
        self.scroll.setWidget(self.mainBodyWidget)
        self.urlLayout.addWidget(self.submissionUrl)
        self.urlBar.setLayout(self.urlLayout)
        for i in reversed(range(self.viewLayout.count())):
            self.viewLayout.itemAt(i).widget().deleteLater()
        self.viewLayout.addWidget(self.scroll)
        self.viewLayout.addWidget(self.submissionScore)
        self.viewWidget.setLayout(self.viewLayout)
        self.viewWindowLayout.addWidget(self.viewWidget)
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Added widgets to mainLayout and viewWidget')
        self.viewWidget.show()
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Showing viewWidget')

    def showSubDesc(self):
        if self.sub.display_name == "all":
            self.descWidget = QLabel("<h1>Frontpage</h1><br/><i>Welcome to the front page of the Internet!</i>")
        else:
            self.descWidget = QLabel(self.sub.description_html)
        self.descWidget.setStyleSheet('background-color: #f0f0f0; color: #0f0f0f; margin: 0px 0px;')
        self.descWidget.setTextFormat(Qt.RichText)
        self.descWidget.setOpenExternalLinks(True)
        self.scroll = QScrollArea()
        self.scroll.setStyleSheet('background-color: #f0f0f0; color: #0f0f0f; margin: 0px 0px;')
        self.viewLayout = QVBoxLayout()
        self.scroll.setWidget(self.descWidget)
        self.viewWidget.setStyleSheet('background-color: #f0f0f0; color: #0f0f0f; margin: 0px 0px;')
        self.viewLayout.addWidget(self.scroll)
        self.viewWidget.setLayout(self.viewLayout)
        self.viewWidgetLayout.addWidget(self.viewWidget)
        self.viewWindowLayout.setAlignment(Qt.AlignLeft)
        self.mainLayout.addWidget(self.viewWindow)
        self.viewWidget.show()



    # Define function to switch between subreddits
    def switchSub(self, subreddit=None):
        if os.environ.get("DEBUG", "") == 'true':
            print(subreddit)
        time.sleep(0.5)
        self.collapsedSearch.connect_button_to_slot(self.switchSub)
        # Set up icons for the various post types
        self.linkIcon = QIcon('{}/link.png'.format(self.runtimePrefix))
        self.textIcon = QIcon('{}/text.png'.format(self.runtimePrefix))
        self.imageIcon = QIcon('{}/imagelink.png'.format(self.runtimePrefix))
        self.videoIcon = QIcon('{}/video-mp4.png'.format(self.runtimePrefix))
        self.ytIcon = QIcon('{}/video-yt.png'.format(self.runtimePrefix))
        if self.centralWidget() != self.window:
            self.setCentralWidget(self.window)
        self.clearLayout(self.subList)
        self.subList = QVBoxLayout()
        self.subredditBar = QWidget()
        self.subredditBar.setStyleSheet('background-color: #0f0f0f')
        if os.environ.get("DEBUG", "") == 'true':
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
                    self.subWidgetList.append(idwidget.IDWidget(submission.title[:70] + '...', parent=self.subredditBar))
                else:
                    self.subWidgetList.append(idwidget.IDWidget(submission.title))
                if os.environ.get("DEBUG", "") == 'true':
                    print()
                self.i += 1

        except prawcore.exceptions.RequestException:
            self.wowSuchEmpty.setText('An error occurred - Read\noperation timed out')
        self.setSubMeta(self.sub)
        self.showSubDesc()
        if os.environ.get("DEBUG", "") == 'true':
            print(self.subWidgetList)
        for self.i in range(len(self.submissionIDList)):
            mdtext = markdownparse.MarkdownText(str(self.submissionDescList[self.i]))
            htmltext = markdownparse.MarkdownText(mdtext.parse())
            rawtext = htmltext.toRawText()
            if len(rawtext) > 100:
                working = self.subWidgetList[self.i]
                self.subWidgetList[self.i].setDescription(rawtext[:100] + '...')
                if os.environ.get("DEBUG", "") == 'true':
                    print('Getting submission #' + self.submissionIDList[self.i] + ': ' + self.submissionTitleList[self.i])
                    print('Set description of submission')
            else:
                if os.environ.get("DEBUG", "") == 'true':
                    print('Getting submission #' + self.submissionIDList[self.i] + ': ' + self.submissionTitleList[self.i])
                self.subWidgetList[self.i].setDescription(rawtext)
                if os.environ.get("DEBUG", "") == 'true':
                    print('Set description of submission')
            self.subWidgetList[self.i].setID(id=self.i)
            self.subWidgetList[self.i].setText(self.submissionTitleList[self.i])
            if os.environ.get("DEBUG", "") == 'true':
                print('Set text of submission')
            self.subWidgetList[self.i].clicked.connect(self.view)
            self.subList.addWidget(self.subWidgetList[self.i])
            self.subWidgetList[self.i].show()
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
            if os.environ.get("DEBUG", "") == 'true':
                print(self.subWidgetList[self.i].id)
            self.subredditBar.setLayout(self.subList)
            self.subWidgetList[self.i].setFixedHeight(100)
            self.subWidgetList[self.i].setFixedWidth(460)
            self.subScroll.setFixedWidth(500)
            self.barsWidget.setFixedWidth(540)
            self.barsLayout.setSpacing(0)
            self.barsLayout.setContentsMargins(0,0,0,0)
            self.barsWidget.setStyleSheet("padding: 0; margin: 0;")
            self.subScroll.setWidget(self.subredditBar)
            self.subScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.subScroll.setWidgetResizable(True)
            time.sleep(0.01)


    # Define function to instantiate an anonymous instance of the PRAW Reddit class
    def initAnonReddit(self):
        # Instantiate Reddit object
        loggedIn = False
        self.title.setText('Attempting to connect to reddit')
        self.reddit = praw.Reddit(redirect_uri="http://localhost:8080", client_id="Jq0BiuUeIrsr3A", client_secret=None, user_agent="Angel for Reddit v0.5 (by /u/Starkiller645)")
        if os.environ.get("DEBUG", "") == 'true':
            print(self.reddit)
            print(self.reddit.auth.url(["identity", "vote", "read", "mysubreddits", "history"], "...", "permanent"))
        self.initNewUI()


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
            if os.environ.get("DEBUG", "") == 'true':
                print("[DBG] " + subreddit.display_name)
        if os.environ.get("DEBUG", "") == 'true':
            print(self.subredditList)
        i = 0
        for currentSub in self.subredditList:
            self.subMenu.addAction(currentSub)
            if os.environ.get("DEBUG", "") == 'true':
                print(self.subMenu.actions()[i])
                print(self.subredditList[i])
                print(currentSub)
            self.subMenu.actions()[i].triggered.connect(lambda null, s=currentSub: self.switchSub(s))
            i += 1
            if os.environ.get("DEBUG", "") == 'true':
                print(i)



    # Function for logging out of the program
    def logOut(self):
        try:
            if os.name != "posix":
                os.remove("{}/praw.ini".format(os.environ.get("APPDATA", "")))
            else:
                os.remove("{}/.config/praw.ini".format(os.environ.get("HOME", "")))
        except OSError:
            if os.environ.get("DEBUG", "") == 'true':
                print("[ERR] praw.ini does not exist, so cannot be deleted\n[ERR] Please check ~/.config/ on POSIX OSes or\n[ERR] %APPDATA%/ on Win10")
        finally:
            self.toolbar.close()
            self.toolbar.deleteLater()
            self.subBar.close()
            self.subBar.deleteLater()
            self.initProgram()


    def widgetUp(self):
        self.widgetNum += 1
        self.view(self.widgetNum)

    def widgetDown(self):
        self.widgetNum -= 1
        self.view(self.widgetNum)

    def initNewUI(self):
        self.webpage = None
        self.searchSubs = QLineEdit(placeholderText="Search: r/subreddit")

        # Set up main window layout
        self.window = QWidget()
        self.window.setStyleSheet("padding: 0;")
        self.windowLayout = QVBoxLayout()
        self.windowLayout.setSpacing(0)
        self.window.setLayout(self.windowLayout)
        self.primaryWidget = QWidget()
        self.primaryWidget.setContentsMargins(0,0,0,0)
        self.primaryWidget.setStyleSheet("background-color: #66ff66; padding: 0;")
        self.mainLayout = QHBoxLayout()
        self.mainLayout.setSpacing(0)
        self.primaryWidget.setLayout(self.mainLayout)

        # Toolbar widget to go in the top-right, displaying submission title etc.
        self.toolbarWidget = QWidget()
        self.toolbar = QHBoxLayout()
        self.toolbar.addWidget(QLabel("self.toolbar"))
        self.toolbarWidget.setLayout(self.toolbar)
        self.toolbarWidget.setFixedHeight(200)

        # Subreddit bar widget in top-left; shows subreddit info
        self.subBarWidget = QWidget()
        self.subBar = QHBoxLayout()
        self.subBar.addWidget(QLabel("self.subBar"))
        self.subBarWidget.setStyleSheet("background-color: #0f0f0f; color: #f0f0f0;")
        self.subBarWidget.setLayout(self.subBar)
        self.subBarWidget.setFixedHeight(200)

        # Top widget; contains the two widgets above and wraps into one toolbar
        self.topWidget = QWidget()
        self.topWidgetLayout = QHBoxLayout()
        self.topWidgetLayout.setSpacing(0)
        self.topWidgetLayout.addWidget(self.subBarWidget)
        self.topWidgetLayout.addWidget(self.toolbarWidget)
        self.topWidget.setLayout(self.topWidgetLayout)
        self.topWidget.setStyleSheet("padding: 0; margin: 0; background-color: #0000ff;")
        self.topWidget.setMaximumHeight(80)

        # Set up a widget to hold the subreddit bar and the sidebar
        self.barsWidget = QWidget()
        self.barsLayout = QHBoxLayout()
        self.barsLayout.setSpacing(0)
        self.barsWidget.setLayout(self.barsLayout)
        self.barsWidget.setStyleSheet("padding: 0; margin: 0; background-color: #ff0000;")

        # Setup sidebar widgets
        self.sideBar = QVBoxLayout()
        self.sideBarWidget = QWidget(self.barsWidget)
        self.collapsedSearch = collapse.CollapsibleDialog('search')
        self.collapsedSubreddits = collapse.CollapsibleDialog('subs')
        self.collapsedSearch.installEventFilter(self)
        self.collapsedSearch.get_button().clicked.connect(self.resizeSideBar)
        self.sideBar.addWidget(self.collapsedSearch)
        self.sideBar.addWidget(self.collapsedSubreddits)
        self.sideBarWidget.setLayout(self.sideBar)
        self.sideBarWidget.setStyleSheet("padding: 0; background-color: #262626;")
        self.barsLayout.addWidget(self.sideBarWidget)
        self.barsWidget.setStyleSheet("padding: 0; background-color: #f0f0f0")

        # Setup top bar widgets
        self.menuButton = QPushButton()
        self.menuButtonIcon = QIcon.fromTheme('application-menu')
        self.menuButton.setText("Menu")
        self.spacer = QWidget()
        self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.menu = QMenu()
        self.menuEntryArray = ["Logout", "Website"]
        self.createMenu(self.menuEntryArray, self.menu)
        self.menuButton.setMenu(self.menu)
        self.toolbar.addWidget(self.spacer)
        self.toolbar.addWidget(self.menuButton)
        self.menuButton.show()
        self.menu.actions()[0].triggered.connect(self.logOut)
        self.menu.actions()[1].triggered.connect(lambda null, page="https://github.com/Starkiller645/angel": webbrowser.open(page))
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Set up right side of toolbar')

        self.spacer1 = QWidget()
        self.spacer2 = QWidget()
        self.spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.spacer2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.subIcon = QLabel()
        self.subIconPixmap = QPixmap()
        self.subHeader = QLabel('r/none')
        self.subHeader.setStyleSheet('font-weight: bold; font-size: 30px;')
        self.subBarHeader = QLabel('r/none')
        self.subBarHeader.setStyleSheet('font-weight: bold; font-size: 30px;')

        self.subList = QVBoxLayout()
        self.subredditBarContainer = QWidget()
        self.subredditBarContainerLayout = QVBoxLayout()
        self.subredditBarContainer.setLayout(self.subredditBarContainerLayout)
        self.subredditBarContainer.setStyleSheet('background-color: #0f0f0f; padding: 0;')
        self.subredditBar = QWidget()
        self.subredditBar.setLayout(self.subList)
        self.subScroll = QScrollArea()
        self.subScroll.setWidget(self.subredditBar)
        self.subScroll.widgetResizable = True
        self.subList.addWidget(QLabel("<b>self.subredditBar</b>"))
        self.subredditBarContainerLayout.addWidget(self.subScroll)
        self.barsLayout.addWidget(self.subredditBarContainer)
        self.mainLayout.addWidget(self.barsWidget)
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Set main layout')

        # Add main UI widgets
        self.windowLayout.addWidget(self.topWidget)
        self.windowLayout.addWidget(self.primaryWidget)

        # Set up left-side scroll area for the submission list
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Setting up scroll area')
        self.subScroll.setStyleSheet('background-color: #0f0f0f;')
        self.viewWidgetLayout = QVBoxLayout()
        self.viewWidget = QWidget()
        self.viewWidget.setLayout(self.viewWidgetLayout)
        self.viewWidget.setStyleSheet('background-color: #ff4500;')
        self.viewWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.mainLayout.addWidget(self.viewWidget)
        self.window.setStyleSheet('background-color: #f0f0f0; padding: 0px 0px;')

        self.setCentralWidget(self.window)
        self.switchSub("all")

    def resizeSideBar(self):
        # Set up sidebar animation
        self.sideBarAnimation = QPropertyAnimation(self.sideBarWidget, b"geometry")
        self.subScrollAnimation = QPropertyAnimation(self.subredditBarContainer, b"geometry")
        self.sideBarAnimationReverse = QPropertyAnimation(self.sideBarWidget, b"geometry")
        self.subScrollAnimationReverse = QPropertyAnimation(self.subredditBarContainer, b"geometry")
        self.subScrollOriginalGeo = self.subredditBarContainer.geometry()
        self.sideBarOriginalGeo = self.sideBarWidget.geometry()
        self.sideBarWidgetGeometry = self.sideBarWidget.geometry().getRect()
        self.subScrollWidgetGeometry = self.subredditBarContainer.geometry().getRect()
        self.sideGeoList = list(self.sideBarWidgetGeometry)
        self.sideGeoList[2] += 470
        self.sideBarAnimation.setEndValue(QRect(self.sideGeoList[0], self.sideGeoList[1], 540, self.sideGeoList[3]))
        self.subGeoList = list(self.subScrollWidgetGeometry)
        self.subGeoList[2] = 2
        self.subScrollAnimation.setEndValue(QRect(540, self.subGeoList[1], self.subGeoList[2], self.subGeoList[3]))
        #self.sideBarWidget.setFixedWidth(500)
        #self.subredditBarContainer.setFixedWidth(0)
        self.subScrollAnimation.start()
        self.sideBarAnimation.start()
        #self.sideBar.setFixedWidth(540)
        try:
            self.collapsedSearch.get_button().clicked.disconnect()
        except TypeError:
            pass
        self.collapsedSearch.reconnect_slots()
        self.collapsedSearch.get_button().clicked.connect(self.resizeSubBar)

    def resizeSubBar(self):
        self.sideBarAnimationReverse = QPropertyAnimation(self.sideBarWidget, b"geometry")
        self.subScrollAnimationReverse = QPropertyAnimation(self.subredditBarContainer, b"geometry")
        self.sideBarAnimation.setEndValue(self.sideBarOriginalGeo)
        self.subGeoList = list(self.subScrollWidgetGeometry)
        self.sideBarWidgetGeometry = self.sideBarWidget.geometry().getRect()
        self.subScrollWidgetGeometry = self.subredditBarContainer.geometry().getRect()
        self.sideGeoList = list(self.sideBarWidgetGeometry)
        self.sideGeoList[2] -= 470
        self.sideBarAnimationReverse.setEndValue(QRect(self.sideGeoList[0], self.sideGeoList[1], 64, self.sideGeoList[3]))
        self.subGeoList = list(self.subScrollWidgetGeometry)
        self.subGeoList[2] = 500
        self.subScrollAnimationReverse.setEndValue(QRect(64, self.subGeoList[1], self.subGeoList[2], self.subGeoList[3]))
        self.sideBarWidget.raise_()
        self.subScrollAnimationReverse.start()
        self.sideBarAnimationReverse.start()
        #self.sideBar.setFixedWidth(540)
        try:
            self.collapsedSearch.get_button().clicked.disconnect()
        except TypeError:
            pass
        self.collapsedSearch.reconnect_slots()
        self.collapsedSearch.get_button().clicked.connect(self.resizeSideBar)


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
                if os.environ.get("DEBUG", "") == 'true':
                    print('[DBG] Added list of subs')
        except AttributeError:
            pass
        self.searchButton = QPushButton('Go')
        self.searchButton.setShortcut("Return")
        self.searchSubs.setMaximumWidth(340)
        self.searchSubs.setMinimumWidth(280)
        self.searchButton.setMaximumWidth(40)
        self.toolbar = QToolBar()
        self.collapsedSearch = collapse.CollapsibleDialog()
        self.subBar = QToolBar()
        self.hasUpVoted = False
        self.hasDownVoted = False
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Set the left side of toolbar up')

        # Create null buttons for UP and DOWN keys
        self.widgetNum = 0
        self.nullUp = QPushButton()
        self.nullDown = QPushButton()
        self.nullUp.clicked.connect(self.widgetUp)
        self.nullDown.clicked.connect(self.widgetDown)
        self.nullUp.setShortcut("Up")
        self.nullDown.setShortcut("Down")

        # Set up menu button
        self.menuButton = QPushButton("Menu")
        self.menu = QMenu()
        self.menuEntryArray = ["Logout", "Website"]
        self.createMenu(self.menuEntryArray, self.menu)
        self.menuButton.setMenu(self.menu)
        self.menu.actions()[0].triggered.connect(self.logOut)
        self.menu.actions()[1].triggered.connect(lambda null, page="https://github.com/Starkiller645/angel": webbrowser.open(page))
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Set up right side of toolbar')

        # Finish setting up toolbar
        self.spacer1 = QWidget()
        self.spacer2 = QWidget()
        self.spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.spacer2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.subIcon = QLabel()
        self.subIconPixmap = QPixmap()
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Set pixmaps')
        #self.subIcon.setPixmap(self.subIconPixmap)
        #self.subIcon.show()
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Showing pixmaps')
        self.subHeader = QLabel('r/none')
        self.subHeader.setStyleSheet('font-weight: bold; font-size: 30px;')
        self.subBarHeader = QLabel('r/none')
        self.subBarHeader.setStyleSheet('font-weight: bold; font-size: 30px;')
        self.subBar.setFixedWidth(540)
        self.subBar.addWidget(self.subIcon)
        self.subBar.addWidget(self.subBarHeader)
        self.funcBar = QToolBar()
        self.funcBar.addWidget(QLabel('TEST 1'))
        self.funcBar.addWidget(QLabel('TEST 2'))
        self.addToolBar(self.subBar)
        self.toolbar.setStyleSheet('background-color: #f0f0f0')
        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)
        self.funcBar.setStyleSheet('background-color: #cccccc')
        self.addToolBar(self.toolbar)
        #self.addToolBar(Qt.LeftToolBarArea, self.funcBar)
        if os.environ.get("DEBUG", "") == 'true':
            print(self.toolbar.objectName())
            print('[DBG] Added toolbar')

        # Add widgets to toolbar
        self.toolbar.addWidget(self.searchSubs)
        self.toolbar.addWidget(self.searchButton)
        self.toolbar.addWidget(self.collapsedSearch)
        try:
            if self.redditUname is not None:
                self.toolbar.addWidget(self.subListButton)
        except AttributeError:
            pass
        self.toolbar.addWidget(self.spacer1)
        self.toolbar.addWidget(self.subHeader)
        self.toolbar.addWidget(self.spacer2)
        self.toolbar.addWidget(self.menuButton)
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Toolbar done!')

        # Set main layout
        self.mainLayout = QHBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.wowSuchEmpty = QLabel('Wow, such empty!')
        self.wowSuchEmpty.setAlignment(Qt.AlignCenter)
        self.window = QWidget()
        self.window.setStyleSheet('background-color: #f0f0f0;')
        self.subList = QVBoxLayout()
        self.subredditBarContainer = QWidget()
        self.subredditBarContainerLayout = QVBoxLayout()
        self.subredditBarContainer.setLayout(self.subredditBarContainerLayout)
        self.subredditBarContainer.setStyleSheet('background-color: #0f0f0f;')
        self.subredditBar = QWidget()
        self.subredditBar.setMaximumWidth(540)
        self.subredditBar.setMinimumWidth(540)
        self.subredditBar.setLayout(self.subList)
        self.subScroll = QScrollArea()
        self.subScroll.setWidget(self.subredditBar)
        self.subScroll.widgetResizable = True
        self.subredditBarContainerLayout.addWidget(self.subScroll)
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Set main layout')

        # Set up left-side scroll area for the submission list
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Setting up scroll area')
        self.scroll = QScrollArea()
        self.viewWidget = QLabel('Wow, such empty!')
        self.scroll.setWidget(self.subredditBar)
        self.subScroll.setStyleSheet('background-color: #0f0f0f;')
        self.sideBarLayout = QVBoxLayout()
        self.sideBarLayout.addWidget(self.subScroll)
        self.sideBar = QWidget()
        self.sideBar.setLayout(self.sideBarLayout)
        self.sideBar.setStyleSheet('background-color: #0f0f0f;')
        self.mainLayout.addWidget(self.sideBar)
        self.window.setStyleSheet('background-color: #f0f0f0; padding: 0px 0px;')
        self.window.setLayout(self.mainLayout)
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Setting central widget as window')
        self.setCentralWidget(self.window)
        if os.environ.get("DEBUG", "") == 'true':
            print('[DBG] Set central widget as window')

        # Connect searchButton with subreddit switching function
        self.searchButton.clicked.connect(self.switchSub)
        if os.name != "posix":
            return
        if os.environ.get("CI", "") == 'true':
            print('[CI] Triggering switchSub...')
            self.switchSub('announcements')
            print('[CI] Switched sub\n[CI] Triggering view...')
            self.view(id=1)
            time.sleep(10)
            print('[CI] Integration tests complete\n[CI] Stand by to exit...')
            time.sleep(0.5)
            os._exit(0)
