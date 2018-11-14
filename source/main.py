# Module creates a Qt table to display overdue issues as either older than:
# 2 days - displayed in black text
# 5 days - displayed as flashing red text
# 10 days - displayed as solid red text
# Up to 200 tickets are fetched using a thread (prevent locking updating table)
# This project follows the PEP-8 style guides

import sys
from PyQt5 import QtCore, QtWidgets, QtGui
# Used to covert and import datetime
from PyQt5.QtCore import QDate, QTime, Qt

from jira import JIRA
import netrc
import threading
from datetime import datetime
# Used to truncate and convert string to datetime Obj
from dateutil import parser

from ticket_board import TicketBoard
from analytics import AnalyticsBoard
from settings import SettingsBoard
from database import database

AUTOMATED_MESSAGE = "Hi Team,\n\nThis is an automated email from the Wherewolf Support System.\n\nIt has been over 7 days since we have received a responce in relation to your support ticket.\n\nCan you please confirm if the ticket/request requires further attention or if it has been resolved and can be closed\n\nPlease respond to this email so we can take appropriate action.\n\nMany thanks,\n\nWherewolf Support"

# TODO make these defined from settings page in db
TRANSITION_PERIOD = 10 * 1000  # (miliseconds) time between page swap
QUEUE_OVERDUE = 60 * 60 * 24 * 7  # (seconds) waiting on customer tickets older than
# this are thrown back into waiting on support with (follow up with client) text added to summary

# TODO
# Place check_queue into own class
# Silence waiting for customer ticket updates so last_updated is not affected
# Remove update to customer ticket summary and write an internal comment instead
# Create gui constructor methods for each class
# Remove self. where its not needed


class MainWindow(QtWidgets.QMainWindow):
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
        self.settings_submit_button.clicked.connect(self.push_settings_button)
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

        # Timer used to fetch the waiting on customer queue and throw back into
        self.clean_queue_timer = QtCore.QTimer(self)
        self.clean_queue_timer.timeout.connect(self.clean_queue_timeout)
        self.clean_queue_timer.start(60 * 1000)  # Clean every minute

        # Timer used to transition the page
        self.transition_page_timer = QtCore.QTimer(self)
        self.transition_page_timer.timeout.connect(self.transition_page_timeout)
        self.transition_page_timer.start(TRANSITION_PERIOD)

        # Timer fetch tickets from JIRA server
        self.update_datetime_timer = QtCore.QTimer(self)
        self.update_datetime_timer.timeout.connect(self.update_datetime_timeout)
        self.update_datetime_timer.start(1000)  # update every 1 second

    def update_datetime_timeout(self):
        self.update_datetime_thread = threading.Thread(target=self.update_datetime)  # Load thread into obj
        self.update_datetime_thread.start()  # Start thread

    def update_datetime(self):
        Qdate = QDate.currentDate()
        Qtime = QTime.currentTime()
        self.date.setText(Qdate.toString(Qt.DefaultLocaleLongDate))
        self.time.setText(Qtime.toString(Qt.DefaultLocaleLongDate))

    def transition_page_timeout(self):
        index_Id = self.window.currentIndex()
        if index_Id < self.window.count() - 1:
            self.window.setCurrentIndex(index_Id + 1)
        else:
            self.window.setCurrentIndex(0)

    def clean_queue_timeout(self):
        if self.clean_queue_button.isChecked():
            # Load thread into obj
            self.clean_queue_thread = threading.Thread(target=self.clean_queue)
            self.clean_queue_thread.start()  # Start thread

    def clean_queue(self):
        # Try to get a transition key if there are any tickets in waiting for customer
        try:
            jira = JIRA(basic_auth=(database.settings['username'], database.settings['api_key']), options={'server': database.settings['jira_url']})
            # Get list of transitions for a ticket in the waiting on customer queue
            transitions = jira.transitions(ticket_board.customer_tickets[0].key)
            # Find the transition key needed to move from waiting for customer to cold tickets queue
            for key in transitions:
                if (key['name'] == 'No reply transition'):
                    transition_key = key['id']

            for customer_ticket in ticket_board.customer_tickets:
                if customer_ticket.key == 'WS-909':
                    date = datetime.now()  # Get current date
                    # Truncate and convert string to datetime obj
                    customer_ticket_date = parser.parse(customer_ticket.fields.updated[0:23])
                    last_updated = (date - customer_ticket_date).total_seconds()
                    if (last_updated > QUEUE_OVERDUE):  # If tickets are overdue
                        # Fetch the comments obj for the current ticket
                        comments = jira.issue(customer_ticket.key)
                        # Check last comment in the ticket and see if it was the AUTOMATED_MESSAGE, if so
                        # client has not responded to automation message. Throw into cold queue
                        if AUTOMATED_MESSAGE in comments.raw['fields']['comment']['comments'][len(comments.raw['fields']['comment']['comments']) - 1]['body']:
                            jira.transition_issue(customer_ticket, transition_key)
                        else:  # AUTOMATION_MESSAGE not found, then ticket is just old, add AUTOMATION_MESSAGE to ticket
                            jira.add_comment(customer_ticket.key, AUTOMATED_MESSAGE, is_internal=False)

        except:
            print("No tickets to check or invalid transition key")

    def push_settings_button(self):
        self.transition_page_timer.stop()
        self.window.addWidget(settings_board.settings_board_widget)
        self.window.setCurrentWidget(settings_board.settings_board_widget)

        # Load values
        settings_board.load_from_cache()

        # Remove all currently connected functions
        self.settings_submit_button.disconnect()
        # Change button submit to save current results
        self.settings_submit_button.clicked.connect(self.push_submit_button)
        self.settings_submit_button.setText("Submit")

    def push_submit_button(self):
        self.transition_page_timer.start()
        self.window.removeWidget(settings_board.settings_board_widget)  # Remove settings board so it doesn't show in transition
        self.window.setCurrentWidget(ticket_board.ticket_board_widget)  # Don't wait for transition to change back to another page

        # Save values to cache and db
        settings_board.save_to_cache()

        self.settings_submit_button.disconnect()
        self.settings_submit_button.clicked.connect(self.push_settings_button)
        self.settings_submit_button.setText("Settings")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.showMaximized()
    main_window.setWindowTitle('Jira Helper')
    ticket_board = TicketBoard()
    main_window.window.addWidget(ticket_board.ticket_board_widget)  # Add the ticket board widget/layout to the main window widget
    analytics_board = AnalyticsBoard()
    main_window.window.addWidget(analytics_board.analytics_board_widget)  # Add the analytics board widget/layout to the main window widget
    settings_board = SettingsBoard()
    main_window.show()
    sys.exit(app.exec_())  # Launch event loop
