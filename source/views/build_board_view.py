# Creates a view with numerous progress loading bars denoting the progress of a build ticket. Only checks tickets with '-1' suffix

import sys
from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QProgressBar

from main_view import main_view
from jira_service import jira_service
from settings_model import Base, SettingsModel

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BOARD_SIZE = 20


class BuildBoardView(QWidget):
    def __init__(self):
        super(BuildBoardView, self).__init__()
        engine = create_engine('sqlite:///jira_helper.db')
        Base.metadata.bind = engine
        self.DBSession = sessionmaker(bind=engine)

        self.build_board_layout = QGridLayout()  # Layout for build board
        self.setLayout(self.build_board_layout)

        # Create a page title
        title = QLabel()
        title_font = QFont("Times", 20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setText('Build Queue')
        self.build_board_layout.addWidget(title, 0, 0, 1, 0, QtCore.Qt.AlignCenter)

        # Create column headers
        header_font = QFont("Times", 12)
        header_font.setBold(True)

        dev_title = QLabel()
        dev_title.setFixedHeight(20)
        dev_title.setText('In Dev')
        dev_title.setFont(header_font)
        self.build_board_layout.addWidget(dev_title, 1, 0, QtCore.Qt.AlignCenter)

        design_title = QLabel()
        design_title.setFixedHeight(20)
        design_title.setText('In Design')
        design_title.setFont(header_font)
        self.build_board_layout.addWidget(design_title, 1, 1, QtCore.Qt.AlignCenter)

        test_title = QLabel()
        test_title.setFixedHeight(20)
        test_title.setText('In Test')
        test_title.setFont(header_font)
        self.build_board_layout.addWidget(test_title, 1, 2, QtCore.Qt.AlignCenter)

        # Global var to contain ticket numbers in build queue
        self.progress_key = list()

        # Build a matrix of progress bars for ticket status
        text_font = QFont("Times", 12)
        self.progress = list()
        for i in range(0, BOARD_SIZE):
            self.progress.append(QProgressBar())
            self.progress[i].setRange(0, 6)
            self.progress[i].setTextVisible(False)
            self.progress_key.append(QLabel())
            self.progress_key[i].setFont(text_font)
            self.build_board_layout.addWidget(self.progress[i], i + 2, 0, 2, 0)

    # Removes tickets from board when they are done or change position
    def clean_board(self):
        for i in range(0, BOARD_SIZE):
            self.progress[i].setValue(0)
            self.build_board_layout.removeWidget(self.progress_key[i])

    def update_board(self):
        session = self.DBSession()
        settings = session.query(SettingsModel).first()
        # Close the session for this thread OR FACE ERRORS!
        session.close()
        self.clean_board()
        # Counter for filling board
        count = 0
        for ticket in jira_service.build_tickets:
            # Prevent overflow
            if count < BOARD_SIZE:
                if (ticket.raw['fields']['status']['name'].lower() == settings.dev_status):
                    self.progress[count].setValue(1)  # Set the progress bar level
                    self.build_board_layout.addWidget(self.progress_key[count], count + 2, 0, QtCore.Qt.AlignCenter)  # Add the ticket under its relevant title
                elif (ticket.raw['fields']['status']['name'].lower() == settings.design_status):
                    self.progress[count].setValue(3)  # Set the progress bar level
                    self.build_board_layout.addWidget(self.progress_key[count], count + 2, 1, QtCore.Qt.AlignCenter)  # Add the ticket under its relevant title
                elif (ticket.raw['fields']['status']['name'].lower() == settings.test_status):
                    self.progress[count].setValue(5)  # Set the progress bar level
                    self.build_board_layout.addWidget(self.progress_key[count], count + 2, 2, QtCore.Qt.AlignCenter)  # Add the ticket under its relevant title
                self.progress_key[count].setText(str(ticket.raw['key']))  # Add the ticket key to the bar
                count = count + 1


if __name__ == 'build_board_view':
    print('Instantiating build_board_view')
    build_board_view = BuildBoardView()
    # Add the ticket board widget/layout to the main window widget
    main_view.window.addWidget(build_board_view)
