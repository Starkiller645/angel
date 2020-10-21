#!/usr/bin/env python3

import sys
from PyQt5.QtWidgets import (QWidget, QPushButton, QDialog, QTreeWidget,
                             QTreeWidgetItem, QVBoxLayout,
                             QHBoxLayout, QFrame, QLabel,
                             QApplication, QLineEdit, QSizePolicy)

class SectionExpandButton(QPushButton):
    """a QPushbutton that can expand or collapse its section
    """
    def __init__(self, item, text = "", parent = None):
        super().__init__(text, parent)
        self.section = item
        self.clicked.connect(self.on_clicked)

    def on_clicked(self):
        """toggle expand/collapse of section by clicking
        """
        if self.section.isExpanded():
            self.section.setExpanded(False)
        else:
            self.section.setExpanded(True)


class CollapsibleDialog(QDialog):
    """a dialog to which collapsible sections can be added;
    subclass and reimplement define_sections() to define sections and
        add them as (title, widget) tuples to self.sections
    """
    def __init__(self, type="search"):
        super().__init__()
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.type = type
        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        self.setLayout(layout)
        self.tree.setIndentation(0)
        self.interactiveWidgets = []
        self.sections = []
        self.define_sections()
        self.add_sections()

    def add_sections(self):
        """adds a collapsible sections for every
        (title, widget) tuple in self.sections
        """
        for (title, widget) in self.sections:
            button1 = self.add_button(title)
            section1 = self.add_widget(button1, widget)
            button1.addChild(section1)

    def connect_button_to_slot(self, obj):
        self.goButton.clicked.connect(lambda null: obj(self.lineEdit.text()[2:]))

    def define_sections(self):
        """reimplement this to define all your sections
        and add them as (title, widget) tuples to self.sections
        """
        widget = QFrame(self.tree)
        layout = QVBoxLayout(widget)
        if self.type == "search":
            self.combinedSearchWidget = QWidget()
            self.combinedSearchLayout = QHBoxLayout()
            self.lineEdit = QLineEdit(placeholderText="r/subreddit")
            self.goButton = QPushButton()
            self.goButton.setText("Go")
            self.combinedSearchWidget.setLayout(self.combinedSearchLayout)
            self.combinedSearchLayout.addWidget(self.lineEdit)
            self.lineEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.combinedSearchLayout.addWidget(self.goButton)
            layout.addWidget(self.combinedSearchWidget)
            layout.addWidget(QLabel("SUGGESTIONS"))
            layout.addWidget(QPushButton("r/memes"))
            layout.addWidget(QPushButton("r/linux"))
        title = "Search"
        self.sections.append((title, widget))

    def add_button(self, title):
        """creates a QTreeWidgetItem containing a button
        to expand or collapse its section
        """
        item = QTreeWidgetItem()
        self.tree.addTopLevelItem(item)
        self.button = SectionExpandButton(item, text = title)
        self.tree.setItemWidget(item, 0, self.button)
        return item

    def reconnect_slots(self):
        self.button.clicked.connect(self.button.on_clicked)

    def add_widget(self, button, widget):
        """creates a QWidgetItem containing the widget,
        as child of the button-QWidgetItem
        """
        section = QTreeWidgetItem(button)
        section.setDisabled(True)
        self.tree.setItemWidget(section, 0, widget)
        return section

    def get_button(self):
        return self.button
