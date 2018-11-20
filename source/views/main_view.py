# Creates the main window and top row tool panel containing the 'settings' and 'clean queue' button, time and date. Also performs waiting on customer queue cleaning through a background thread which is toggled using the 'clean queue' button

import sys
from PyQt5 import QtCore, QtWidgets, QtGui
# Used to covert and import datetime
from PyQt5.QtCore import QDate, QTime, Qt

from jira import JIRA
import threading
from datetime import datetime
# Used to truncate and convert string to datetime Obj
from dateutil import parser

AUTOMATED_MESSAGE = "Hi Team,\n\nThis is an automated email from the Wherewolf Support System.\n\nIt has been over 7 days since we have received a responce in relation to your support ticket.\n\nCan you please confirm if the ticket/request requires further attention or if it has been resolved and can be closed\n\nPlease respond to this email so we can take appropriate action.\n\nMany thanks,\n\nWherewolf Support"

# TODO make these defined from settings page in db
TRANSITION_PERIOD = 10 * 1000  # (miliseconds) time between page swap
QUEUE_OVERDUE = 60 * 60 * 24 * 7  # (seconds) waiting on customer tickets older than
# this are thrown back into waiting on support with (follow up with client) text added to summary

# TODO
# Place check_queue into own class?
# Silence waiting for customer ticket updates so last_updated is not affected, if possible
# Remove update to customer ticket summary and write an internal comment instead
# Create gui constructor methods for each class
# Remove self. where its not needed


class MainView(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.window = QtWidgets.QStackedWidget()  # Create the main widget for the page

        self.main_window_widget = QtWidgets.QWidget()
        self.main_window_layout = QtWidgets.QGridLayout()
        self.main_window_widget.setLayout(self.main_window_layout)
        self.menu_widget = QtWidgets.QWidget()
        self.menu_layout = QtWidgets.QHBoxLayout()
        self.menu_widget.setLayout(self.menu_layout)
        self.main_window_layout.addWidget(self.menu_widget, 0, 0)
        self.main_window_layout.addWidget(self.window, 1, 0)
        self.setCentralWidget(self.main_window_widget)

        self.settings_submit_button = QtWidgets.QPushButton()
        self.settings_submit_button.setText("Settings")
        self.menu_layout.addWidget(self.settings_submit_button)

        self.date = QtWidgets.QLabel()
        self.date.setStyleSheet('font-size: 40px')
        self.time = QtWidgets.QLabel()
        self.time.setStyleSheet('font-size: 40px')
        self.menu_layout.addWidget(self.date)
        self.menu_layout.addWidget(self.time)

        self.clean_queue_button = QtWidgets.QPushButton()
        self.clean_queue_button.setText("Clean Queue")
        self.clean_queue_button.setCheckable(True)
        self.menu_layout.addWidget(self.clean_queue_button)

    def update_datetime(self):
        Qdate = QDate.currentDate()
        Qtime = QTime.currentTime()
        self.date.setText(Qdate.toString(Qt.DefaultLocaleLongDate))
        self.time.setText(Qtime.toString(Qt.DefaultLocaleLongDate))

    def transition_page(self):
        index_Id = self.window.currentIndex()
        if index_Id < self.window.count() - 1:
            self.window.setCurrentIndex(index_Id + 1)
        else:
            self.window.setCurrentIndex(0)

if __name__ == 'main_view':
    print('Instantiating main_view')
    main_view = MainView()