#!/usr/bin/env python3
"""Class file for a QRunnable to fetch Reddit images

This will be run in a QThread for asynced execution and will handle the download of
image files (png, jpg, jpeg, gif, etc.). The run() function should not be called
directly.

    Usage (inside class derived from QMainWindow):

    self.threadpool = QThreadPool()
    self.imageWorker = imageworker.ImageWorker("https://example.com/image.png")
    self.threadpool.start(self.imageWorker)
    self.imageWorker.signals.returnImageLocation.connect(self.someFunction)
"""

import io
import requests
import os
from PIL import Image, ImageOps
from PyQt5.QtCore import *
from angellib.threadsignals import ThreadSignals

class ImageWorker(QRunnable):
    def __init__(self, url):
        super(ImageWorker, self).__init__()
        self.signals = ThreadSignals()
        self.url = url
        print(self)

    @pyqtSlot()
    def run(self, url=None):
        """Function overridden from QRunnable that downloads an image from a remote server

        Args:
            url (str): The url to fetch an image from. Should be a direct image link in
                http:// or https:// format. If running inside a class, self.url should
                be assigned instead of passing the URL as an argument.

        Locals:
            rawImage (requests.Response): Holds a requests object from the http request
            imageInBytes (io.BytesIO): Holds the raw bytes from the rawImage object
            image (PIL.Image): Holds a PIL object for performing PIL operations

        Returns:
            int: Will return 1 if an error occurred, or nothing if no error occurred.

        Signals:
            signals.returnImageLocation (str): Calls the function inside the main class which adds the
                image to the layout of the main body of a submission.
        """

        if url is not None:
            pass
        else:
            url = self.url

        try:
            rawImage = requests.get(self.url)
        except requests.RequestException:
            return 1
        imageInBytes = io.BytesIO(rawImage.content)
        image = Image.open(imageInBytes)
        if os.name != "posix":
            appDataLocation = os.environ.get("APPDATA")
            image.save('{0}/Angel/temp/.img.{1}'.format(appDataLocation, image.format.lower()))
            self.signals.returnImageLocation.emit('{0}/Angel/temp/.img.{1}'.format(appDataLocation, image.format.lower()))
        else:
            image.save('/opt/angel-reddit/temp/.img.{}'.format(image.format.lower()))
            self.signals.returnImageLocation.emit('/opt/angel-reddit/temp/.img.{}'.format(image.format.lower()))
