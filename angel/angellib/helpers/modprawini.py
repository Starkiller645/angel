#!/usr/bin/env python3

import os

def initPrawINI():
    if os.name != "posix":
        prawini = open("{}/praw.ini".format(os.environ.get("APPDATA", "").replace("\\", "/")), "w+")
    else:
        prawini = open("{}/.config/praw.ini".format(os.environ.get("HOME", "")), "w+")
    prawini.write('[angel]\n')
    prawini.write('client_id=Jq0BiuUeIrsr3A\nclient_secret=None\nredirect_uri=http://localhost:8080\nuser_agent=Angel for Reddit (by /u/Starkiller645)')
    prawini.close()
    prawiniExists = True
