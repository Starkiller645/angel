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
"""


__all__ = ["videoworker", "threadsignals", "imageworker"]
