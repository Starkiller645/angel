# Import required libraries
import sys
import time
import praw
import prawcore
import os
from PIL import Image
import requests
import io
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
try:
    import pkg_resources.py2_warn
except ImportError:
    pass

# Start QApplication instance
app = QApplication(sys.argv)
app.setWindowIcon(QIcon('snootuxwhite.ico'))
from idwidgets import *

# Create a class as a child of QMainWindow for the main window of the app
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        submissionImage = None
        self.resize(1080, 640)
        self.setWindowTitle('ReddiTux v1.0-beta-prerelease')
        label = QLabel('First PyQt5 window! Hello World!')
        self.mainWidget = QWidget()

        # Setup
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(self.resourcePath('snootuxwhite.ico')))

        # Create login boxes
        loginBox = QVBoxLayout()

        loginBox.width = 300

        # Create snootux pixmap
        pixmap = QPixmap(self.resourcePath('snootuxwhite.png'))
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)
        label.setPixmap(pixmap)
        label.resize(100, 100)

        # Set alignment to center
        label.setAlignment(Qt.AlignCenter)

        # Add to loginBox
        loginBox.addWidget(label)
        loginBox.setAlignment(Qt.AlignCenter)

        # Create login fields and enter button
        self.title = QLabel('Login with Reddit credentials')
        self.title.setAlignment(Qt.AlignCenter)
        self.uname = QLineEdit(placeholderText='Username')
        self.uname.setFixedWidth(300)
        self.uname.setAlignment(Qt.AlignCenter)
        self.passwd = QLineEdit(placeholderText='Password')
        self.passwd.setEchoMode(QLineEdit.Password)
        self.passwd.setFixedWidth(300)
        self.passwd.setAlignment(Qt.AlignCenter)
        self.enterBox = QVBoxLayout()
        self.enter = QPushButton('Enter')
        self.enter.setFixedWidth(50)
        self.noLogin = QRadioButton('Browse without login')
        loginBox.addWidget(self.title)
        loginBox.addWidget(self.uname)
        loginBox.addWidget(self.passwd)
        loginBox.addWidget(self.noLogin)
        self.enterBox.addWidget(self.enter)
        self.enterBox.setAlignment(Qt.AlignCenter)
        self.enterWidget = QWidget()
        self.enterWidget.setLayout(self.enterBox)
        loginBox.addWidget(self.enterWidget)
        # Qt5 connect syntax is object.valueThatIsConnected.connect(func.toConnectTo)
        self.enter.clicked.connect(self.initReddit)
        # Set selected widget to be central, taking up the whole
        # window by default
        self.mainWidget.setLayout(loginBox)
        self.setCentralWidget(self.mainWidget)

    def onButtonPress(self, s):
        print('click', s)

    def fetchImage(self, url):
        image = requests.get(url)
        imageBytes = io.BytesIO(image.content)
        image = Image.open(imageBytes)
        image.save('img.{}'.format(image.format))
        return 'img.{}'.format(image.format)

    def resourcePath(self, relative):
        return os.path.join(os.environ.get("_MEIPASS2", os.path.abspath(".")), relative)

    def fetchImageUrl(self, sub):
        return

    def clearLayout(self, layout):
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()

    def view(self):
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
        self.submissionTitle = QLabel()
        self.submissionTitle.setWordWrap(True)
        self.submissionTitle.setStyleSheet('font-size: 42px; font-weight: bold;')
        self.submissionTitle.setText(self.submissionTitleList[widgetNum])
        self.submissionTitle.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.submissionAuthor = QLabel()
        self.submissionAuthor.setStyleSheet('font-size: 30px; font-style: italic;')
        self.submissionAuthor.setText('u/' + self.submissionAuthorList[widgetNum])
        self.submissionAuthor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.submissionBody = QLabel()
        self.submissionBody.setWordWrap(True)
        self.submissionBody.setStyleSheet('font-size: 20px;')
        self.submissionBody.setText(self.submissionDescList[widgetNum])
        self.submissionBody.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        if 'i.redd.it' in self.submissionImageUrl[widgetNum]:
            submissionImage = QLabel()
            img = QPixmap(self.fetchImage(self.submissionImageUrl[widgetNum]))
            submissionImage.setPixmap(img)
        elif 'reddit.com' not in self.submissionImageUrl[widgetNum]:
            submissionImage = QLabel('<a href="{0}" >{0}</a>'.format(self.submissionImageUrl[widgetNum]))
            submissionImage.setOpenExternalLinks(True)
            submissionImage.setStyleSheet('font-size: 26px; color: skyblue;')
        else:
            submissionImage = None
        self.submissionUrl = QLabel()
        self.submissionUrl.setWordWrap(True)
        self.submissionUrl.setStyleSheet('font-size: 18px;')
        self.submissionUrl.setText('<a href=\"{}\">Link</a>'.format(self.submissionImageUrl[widgetNum]))
        self.submissionUrl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
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
        self.viewLayout.addWidget(self.urlBar)
        self.viewWidget.setLayout(self.viewLayout)
        self.mainLayout.addWidget(self.viewWidget)
        self.viewWidget.show()

    def switchSub(self):
        self.textIcon = QIcon(self.resourcePath('text.png'))
        self.linkIcon = QIcon(self.resourcePath('link.png'))
        self.imageIcon = QIcon(self.resourcePath('imagelink.png'))
        if self.centralWidget() == self.wowSuchEmpty:
            self.setCentralWidget(self.window)
        self.clearLayout(self.subList)
        self.status.setText('Retrieving submissions')
        time.sleep(0.5)
        sub = self.reddit.subreddit(self.searchSubs.text()[2:])
        self.submissionIDList, self.submissionTitleList, self.submissionDescList, self.submissionImageUrl, self.subWidgetList, self.submissionAuthorList = [], [], [], [], [], []
        self.i = 0
        try:
            for submission in sub.hot(limit=10):
                self.submissionIDList.append(submission.id)
                self.submissionTitleList.append(submission.title)
                self.submissionDescList.append(submission.selftext)
                self.submissionImageUrl.append(submission.url)
                self.submissionAuthorList.append(submission.author.name)
                if len(submission.title) > 70:
                    self.subWidgetList.append(IDWidget(submission.title[:70] + '...'))
                else:
                    self.subWidgetList.append(IDWidget(submission.title))
                print()
                self.i += 1

        except prawcore.exceptions.RequestException:
            self.wowSuchEmpty.setText('An error occurred - Read\noperation timed out')
            self.status.setText('Error - Timed out or sub does not exist')
        print(self.subWidgetList)
        for self.i in range(len(self.submissionIDList)):
            if len(self.submissionDescList[self.i]) > 100:
                working = self.subWidgetList[self.i]
                working.setDescription(self.submissionDescList[self.i][:100] + '...')
                print('Getting submission #' + self.submissionIDList[self.i] + ': ' + self.submissionTitleList[self.i])
            else:
                print('Getting submission #' + self.submissionIDList[self.i] + ': ' + self.submissionTitleList[self.i])
                working = self.subWidgetList[self.i]
                working.setDescription(self.submissionDescList[self.i])
            self.subList.addWidget(self.subWidgetList[self.i])
            self.subWidgetList[self.i].setID(id=self.i)
            self.subWidgetList[self.i].setText(self.submissionTitleList[self.i])
            self.subWidgetList[self.i].clicked.connect(self.view)
            if 'reddit.com' in self.submissionImageUrl[self.i]:
                self.subWidgetList[self.i].setIcon(self.textIcon)
            elif 'i.redd.it' in self.submissionImageUrl[self.i]:
                self.subWidgetList[self.i].setIcon(self.imageIcon)
            else:
                self.subWidgetList[self.i].setIcon(self.linkIcon)
            print(self.subWidgetList[self.i].id)
        self.status.setText('Connected to Reddit')

    def initReddit(self):
        username = self.uname.text()
        password = self.passwd.text()

        # Instantiate Reddit object
        loggedIn = False
        ready = False
        while not ready:
            if self.noLogin.isChecked():
                self.title.setText('Attempting to connect to reddit')
                self.reddit = praw.Reddit(redirect_uri="http://localhost:8080", client_id="FODiLQuVNlDa3g", client_secret=None, user_agent="RedditTux - A Reddit Client for Linux")
            if self.reddit.subreddit('announcements') is not None:
                self.title.setText('Success! Connected to Reddit')
                ready = True
                break
            else:
                self.title.setText('Failed to connect - program error')
                break
                self.title.setText('Attempting to connect to Reddit')
                self.reddit = praw.Reddit(client_id="FODiLQuVNlDa3g", client_secret=None, redirect_uri="http://localhost:8080", user_agent="ReddiTux - A Reddit Client for Linux", username="{}".format(username), password="{}".format(password))
                print(self.reddit.user.me())
            if self.reddit.user.me() == username:
                self.title.setText('Success! Connected to Reddit')
                loggedIn = True
                ready = True
                break
            else:
                self.title.setText('Failed to connect. Check your details')
                break

        self.searchSubs = QLineEdit(placeholderText="r/subreddit")
        self.searchButton = QPushButton('Go')
        self.searchSubs.setMaximumWidth(500)
        self.searchButton.setMaximumWidth(40)
        self.toolbar = QToolBar()
        self.status = QLabel('Connected to Reddit')
        self.spacer1 = QLabel('           ')
        self.status.setAlignment(Qt.AlignCenter)
        self.addToolBar(self.toolbar)
        self.toolbar.addWidget(self.searchSubs)
        self.toolbar.addWidget(self.searchButton)
        self.toolbar.addWidget(self.spacer1)
        self.toolbar.addWidget(self.status)
        self.mainLayout = QHBoxLayout()
        self.wowSuchEmpty = QLabel('Wow, such empty!')
        self.wowSuchEmpty.setAlignment(Qt.AlignCenter)
        self.window = QWidget()
        self.subredditBar = QWidget()
        self.subList = QVBoxLayout()
        self.subredditBar.setLayout(self.subList)
        self.subredditBar.setMaximumWidth(540)
        self.mainLayout.addWidget(self.subredditBar)
        self.scroll = QScrollArea()
        self.viewWidget = QLabel('Wow, such empty!')
        self.scroll.setWidget(self.viewWidget)
        self.mainLayout.addWidget(self.viewWidget)
        self.window.setLayout(self.mainLayout)
        self.setCentralWidget(self.window)

        self.searchButton.clicked.connect(self.switchSub)


# Add window widgets
window = MainWindow()
window.show()

# Start event loop
app.exec_()
