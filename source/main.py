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

AUTOMATED_MESSAGE = "Hi Team,\n\nThis is an automated email from the Wherewolf Support System.\n\nIt has been over 7 days since we have received a responce in relation to your support ticket.\n\nCan you please confirm if the ticket/request requires further attention or if it has been resolved and can be closed\n\nPlease respond to this email so we can take appropriate action.\n\nMany thanks,\n\nWherewolf Support"

FONT = "Times"  # Font used to display text
FONT_SIZE = 12

# TODO make these defined from config page in db
TRANSITION_PERIOD = 20000  # (miliseconds) time between page swap
QUEUE_OVERDUE = 60 * 60 * 24 * 7  # (seconds) waiting on customer tickets older than
# this are thrown back into waiting on support with (follow up with client) text added to summary

# Grab credentials from ~/.netrc file
secrets = netrc.netrc()
username, account, password = secrets.authenticators('Jira-Credentials')

# Create a JIRA object using netrc credentials
jira = JIRA(basic_auth=(username, password), options={'server': account})

# TODO
# Place check_queue into own class
# Place each class in own module
# Save in local db
# Silence waiting for customer ticket updates so last_updated is not affected
# Remove update to customer ticket summary and write an internal comment instead


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.window = QtWidgets.QStackedWidget()  # Create the main widget for the page
        self.setCentralWidget(self.window)

        try:  # This will fail if an arg is not supplied
            if sys.argv[1] == "cleanup":  # If cleanup specified in bash, this is the second arg of call to program
                # Timer used to fetch the waiting on customer queue and throw back into
                self.clean_up_timer = QtCore.QTimer(self)
                self.clean_up_timer.timeout.connect(self.clean_up_timeout)
                self.clean_up_timer.start(1000)  # Check every 10 seconds
        except:
            print("Not running clean up")

        # Timer used to transition the page
        self.transition_page_timer = QtCore.QTimer(self)
        self.transition_page_timer.timeout.connect(self.transition_page_timeout)
        self.transition_page_timer.start(TRANSITION_PERIOD)  # Transition every 10 seconds

    def transition_page_timeout(self):
        index_Id = self.window.currentIndex()
        if index_Id < self.window.count() - 1:
            self.window.setCurrentIndex(index_Id + 1)
        else:
            self.window.setCurrentIndex(0)

    def clean_up_timeout(self):
        # Load thread into obj
        self.clean_up_thread = threading.Thread(target=self.clean_up)
        self.clean_up_thread.start()  # Start thread

    def clean_up(self):
        # Try to get a transition key if there are any tickets in waiting for customer
        try:
            # Get list of transitions for a ticket in the waiting on customer queue
            transitions = jira.transitions(self.customer_tickets[0].key)
            # Find the transition key needed to move from waiting for customer to cold tickets queue
            for key in transitions:
                if (key.get('name') == 'No reply transition'):
                    transition_key = key.get('id')

            for customer_ticket in self.customer_tickets:
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


# Create some global objects used by all modules
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.showMaximized()
    main_window.setWindowTitle('Jira Helper')
    ticket_board = TicketBoard()
    main_window.window.addWidget(ticket_board.ticket_board_widget)  # Add the ticket board widget/layout to the main window widget
    analytics_board = AnalyticsBoard()
    main_window.window.addWidget(analytics_board.analytics_board_widget)  # Add the analytics board widget/layout to the main window widget
    sys.exit(app.exec_())
