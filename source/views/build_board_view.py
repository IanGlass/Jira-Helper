
# GUI
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from datetime import timedelta
from datetime import datetime
# Used to truncate and convert string to datetime Obj
from dateutil import parser
from jira import JIRA
from PyQt5.QtCore import QDate, QTime, Qt
import threading

from database_model import database_model
from main_view import main_view
from jira_model import jira_model

BOARD_SIZE = 20


# TODO use setStyleSheet() instead of setFont

class BuildBoardView(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.build_board_widget = QtWidgets.QWidget()  # Create the widget to contain the build board layout
        self.build_board_layout = QtWidgets.QGridLayout()  # Layout for build board
        self.build_board_widget.setLayout(self.build_board_layout)

        # Create a page title
        title = QtWidgets.QLabel()
        title_font = QtGui.QFont("Times", 20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setText('Build Queue')
        self.build_board_layout.addWidget(title, 0, 0, 1, 0, QtCore.Qt.AlignCenter)

        # Create column headers
        header_font = QtGui.QFont("Times", 12)
        header_font.setBold(True)

        dev_title = QtWidgets.QLabel()
        dev_title.setFixedHeight(20)
        dev_title.setText('In Dev')
        dev_title.setFont(header_font)
        self.build_board_layout.addWidget(dev_title, 1, 0, QtCore.Qt.AlignCenter)

        design_title = QtWidgets.QLabel()
        design_title.setFixedHeight(20)
        design_title.setText('In Design')
        design_title.setFont(header_font)
        self.build_board_layout.addWidget(design_title, 1, 1, QtCore.Qt.AlignCenter)

        test_title = QtWidgets.QLabel()
        test_title.setFixedHeight(20)
        test_title.setText('In Test')
        test_title.setFont(header_font)
        self.build_board_layout.addWidget(test_title, 1, 2, QtCore.Qt.AlignCenter)

        # Global var to contain ticket numbers in build queue
        self.progress_key = list()

        # Build a matrix of progress bars for ticket status
        text_font = QtGui.QFont("Times", 12)
        self.progress = list()
        for i in range(0, BOARD_SIZE):
            self.progress.append(QtWidgets.QProgressBar())
            self.progress[i].setRange(0, 6)
            self.progress[i].setTextVisible(False)
            self.progress_key.append(QtWidgets.QLabel())
            self.progress_key[i].setFont(text_font)
            self.build_board_layout.addWidget(self.progress[i], i + 2, 0, 2, 0)

    # Removes tickets from board when they are done or change position
    def clean_board(self):
        for i in range(0, BOARD_SIZE):
            self.progress[i].setValue(0)
            self.build_board_layout.removeWidget(self.progress_key[i])

    def update_board(self):
        self.clean_board()
        # Counter for filling board
        count = 0
        for ticket in jira_model.build_tickets:
            # Prevent overflow
            if count < BOARD_SIZE:
                if (ticket.raw['fields']['status']['name'].lower() == database_model.settings['dev_status']):
                    self.progress[count].setValue(1)  # Set the progress bar level
                    self.build_board_layout.addWidget(self.progress_key[count], count + 2, 0, QtCore.Qt.AlignCenter)  # Add the ticket under its relevant title
                elif (ticket.raw['fields']['status']['name'].lower() == database_model.settings['design_status']):
                    self.progress[count].setValue(3)  # Set the progress bar level
                    self.build_board_layout.addWidget(self.progress_key[count], count + 2, 1, QtCore.Qt.AlignCenter)  # Add the ticket under its relevant title
                elif (ticket.raw['fields']['status']['name'].lower() == database_model.settings['test_status']):
                    self.progress[count].setValue(5)  # Set the progress bar level
                    self.build_board_layout.addWidget(self.progress_key[count], count + 2, 2, QtCore.Qt.AlignCenter)  # Add the ticket under its relevant title
                self.progress_key[count].setText(str(ticket.raw['key']))  # Add the ticket key to the bar
                count = count + 1


if __name__ == 'build_board_view':
    print('Instantiating build_board_view')
    build_board_view = BuildBoardView()
    # Add the ticket board widget/layout to the main window widget
    main_view.window.addWidget(build_board_view.build_board_widget)
