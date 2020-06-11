from PyQt5.QtWidgets import *
# Create a custom widget class with an implementation of a unique identifier for the submission widgets
class IDWidget(QCommandLinkButton):
    def __init__(self, id=None, *args, **kwargs):
        super(IDWidget, self).__init__(*args, **kwargs)
        self.id = id

    def setID(self, id):
        self.id = id

    def getID(self):
        return self.id
