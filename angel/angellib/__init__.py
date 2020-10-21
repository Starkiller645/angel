#!/usr/bin/env python3
"""Library for functions used throughout the Angel reddit client

Classes:
    VideoWorker (str): Child of QRunnable which gets a video from Reddit and
        performs processing to merge sound and video streams. Takes the URL of
        the JSON data for a Reddit page ("https://reddit.com/comment/example-json.json").
        See videoworker.py

    ThreadSignals: Child of QObject which contains common Qt Signals
        used in the other classes in this library.
        See threadsignals.py

    ImageWorker (str): Child of QRunnable which gets an image from a direct
        URL. Takes a direct URL for an image to download.
        See imageworker.py

    MainWindow: Child of QMainWindow. Contains most of the application code that does
        not need to be run asynchronously, except the code contained in the Helpers class,
        and in the other classes in this library.
        See mainwindow.py

    IDWidget (str): Child of QCommandLinkButton with an implementation of a
        unique identifier, to assist with viewing a specific widget in a list.
        See idwidget.py

    WebPageView (str): Child of QWebEngineView. Easy to use - simply pass a URL
        to the constructor and the class will render it as a widget.
        See webpage.py

    AuthorisationWorker: Child of QRunnable which sets up basic authentication with
        Reddit and then emits a signals containing an authcode and praw.Reddit
        instance associated with it.
        See authorisationworker.py
"""


__all__ = ["videoworker", "threadsignals", "imageworker",  "idwidget", "webpage", "unittests", "authorisationworker", "collapse"]
