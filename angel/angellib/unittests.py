#!/usr/bin/env python3
import os, sys

print(sys.platform)
if os.name != "posix":
    isWindows = True
    appData = os.environ.get('APPDATA', '')
else:
    isWindows = False
    envHome = os.environ.get('HOME', '')

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
    """Function to check for asset files that Angel needs to run correctly
    """

    assetFiles = ["angel.ico", "angel.png", "default.png", "downvote.png", "imagelink.png", "link.png", "mask.png", "reddit.png", "text.png", "upvote.png"]
    for file in assetFiles:
        if isWindows:
            assert os.path.exists("{0}/Angel/{1}".format(appData, file))
        else:
            assert os.path.exists("/opt/angel-reddit/{}".format(file))
