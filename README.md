# Angel
![Build Status](https://travis-ci.com/Starkiller645/angel.svg?branch=master)

Angel - a Reddit client for the Linux desktop, built using PyQt5

![Screenshot of login screen](https://github.com/Starkiller645/angel/raw/master/demo/login-demo.png)

![Screenshot of /r/memes in dark theme](https://github.com/Starkiller645/angel/raw/master/demo/r-memes-demo.png)

![Screenshot of /r/linux in light theme](https://github.com/Starkiller645/angel/raw/master/demo/light-theme-demo.png)

# Features

* Currently has ability to view all subreddits
* Can sign in and authenticate to Reddit, view subscribed subreddits and up/downvote posts

# To Do

* Add the ability to view comments
* Add an integrated webbrowser
* Add functionality to scrape and view Reddit urls (/r/...) from posts

# Installation
I haven't got distro packages working on any level yet, but hopefully that should come soon

1. `git clone https://github.com/Starkiller645/angel.git; cd angel`
2. `make`
3. `sudo make install`

To uninstall:

1. cd to the directory where Angel was cloned, e.g. `cd Documents/angel`
2. `sudo make uninstall`

# Testing

To run Angel with the included continuous integration tests:
1. `export CI=true`
2. `angel` (if make-installed) / `angel/__init__.py` (if running from source)

# Requirements
These should be the same for all distros, but open an issue if there is a difference

* Distro packages: `python3 python3-praw python3-pillow python3-pyqt5 python3-requests python3-setuptools`
