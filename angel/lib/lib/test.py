import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ScrolledWidgetList(QWidget):

    def __init__(self, parent= None, layout=QVBoxLayout()):
        super(ScrolledWidgetList, self).__init__()

        #Container Widget
        self.widget = QWidget(self)
        #Layout of Container Widget
        layout = QVBoxLayout(self)
        self.widget.setLayout(layout)

        #Scroll Area Properties
        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

    def setLayout(self, layout):
        self.widget.setLayout(layout)

    def addWidget(self, widget):
        label = widget
        self.widget.layout().addWidget(label)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    dialog = Widget()
    dialog.show()

    app.exec_()
