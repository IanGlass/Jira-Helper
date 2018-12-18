# Creates the main window and top row tool panel containing the 'settings' and 'clean queue' button, time and date. Also performs waiting on customer queue cleaning through a background thread which is toggled using the 'clean queue' button

import sys
from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QStackedWidget, QGridLayout, QWidget, QHBoxLayout, QPushButton, QLabel
# Used to covert and import datetime
from PyQt5.QtCore import QDate, QTime, Qt


class MainView(QMainWindow):
    def __init__(self):
        super(MainView, self).__init__()
        self.setWindowTitle('Jira Helper')

        self.window = QStackedWidget()  # Create the main widget for the page

        main_window_widget = QWidget()
        main_window_layout = QGridLayout()
        main_window_widget.setLayout(main_window_layout)
        menu_widget = QWidget()
        menu_layout = QHBoxLayout()
        menu_widget.setLayout(menu_layout)
        main_window_layout.addWidget(menu_widget, 0, 0)
        main_window_layout.addWidget(self.window, 1, 0)
        self.setCentralWidget(main_window_widget)

        # Create a settings button
        self.settings_submit_button = QPushButton()
        self.settings_submit_button.setText("Settings")
        menu_layout.addWidget(self.settings_submit_button)

        # Create date time
        datetime_font = QFont("Times", 30)
        self.date = QLabel()
        self.date.setFont(datetime_font)
        self.time = QLabel()
        self.time.setFont(datetime_font)
        menu_layout.addWidget(self.date)
        menu_layout.addWidget(self.time)

        # Create a clean queue button
        self.clean_queue_button = QPushButton()
        self.clean_queue_button.setText("Clean Queue")
        self.clean_queue_button.setCheckable(True)
        menu_layout.addWidget(self.clean_queue_button)

    def update_datetime(self):
        '''Connected to a Qtimer to periodically update the date and time'''
        Qdate = QDate.currentDate()
        Qtime = QTime.currentTime()
        self.date.setText(Qdate.toString(Qt.DefaultLocaleLongDate))
        self.time.setText(Qtime.toString(Qt.DefaultLocaleLongDate))

    def transition_page(self):
        '''Connected to a Qtimer to periodically transition through the widgets stacked on self.window'''
        index_Id = self.window.currentIndex()
        if index_Id < self.window.count() - 1:
            self.window.setCurrentIndex(index_Id + 1)
        else:
            self.window.setCurrentIndex(0)


if __name__ == 'main_view':
    print('Instantiating ' + __name__)
    main_view = MainView()
