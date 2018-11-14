# Creates a QWidget to display overdue tickets in the waiting for support queue. Tickets are fetched using a JIRA api and filtered for last_updated > overdue time. Module also saves the ticket history to the local db.

# GUI
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from datetime import timedelta
from datetime import datetime
# Used to truncate and convert string to datetime Obj
from dateutil import parser
from jira import JIRA
import netrc
from PyQt5.QtCore import QDate, QTime, Qt
import threading

from database import database

SUPPORT_TICKET_STATUS = "waiting for support"
CUSTOMER_TICKET_STATUS = "waiting for customer"
IN_PROGRESS_TICKET_STATUS = "in progress"
DEV_TICKET_STATUS = "dev"
DESIGN_TICKET_STATUS = "design"
TEST_TICKET_STATUS = "test"
# Format ticket status' to UNIX compatible directory path used by JIRA API
SUPPORT_TICKET_STATUS = SUPPORT_TICKET_STATUS.replace(" ", "\ ")
CUSTOMER_TICKET_STATUS = CUSTOMER_TICKET_STATUS.replace(" ", "\ ")
IN_PROGRESS_TICKET_STATUS = IN_PROGRESS_TICKET_STATUS.replace(" ", "\ ")
DEV_TICKET_STATUS = DEV_TICKET_STATUS.replace(" ", "\ ")
DESIGN_TICKET_STATUS = DESIGN_TICKET_STATUS.replace(" ", "\ ")
TEST_TICKET_STATUS = TEST_TICKET_STATUS.replace(" ", "\ ")

FONT = "Times"  # Font used to display text
FONT_SIZE = 12

# TODO make these defined from config page in db
BLACK_ALERT_DELAY = 60 * 60 * 24 * 2  # (seconds) displays ticket with 'Last Updated' older than this in black
RED_ALERT_DELAY = 60 * 60 * 24 * 7  # (seconds) tickets with 'Last Updated' older than this are flashed red
MELT_DOWN_DELAY = 60 * 60 * 24 * 14  # (seconds) tickets with 'Last Updated' older than this are solid red

BOARD_SIZE = 25

# TODO use setStyleSheet() instead of setFont


class TicketBoard(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.ticket_board_widget = QtWidgets.QWidget()  # Create the widget to contain the ticket board layout
        self.ticket_board_layout = QtWidgets.QGridLayout()  # Layout for ticket board
        self.ticket_board_widget.setLayout(self.ticket_board_layout)

        self.col_key = list()
        self.col_assigned = list()
        self.col_summary = list()
        self.col_last_updated = list()
        self.col_sla = list()

        self.fnt = QtGui.QFont(FONT, FONT_SIZE)
        for i in range(0, BOARD_SIZE + 1):  # Build the ticket board
            self.col_key.append(QtWidgets.QLabel())
            self.col_key[i].setFont(self.fnt)
            self.ticket_board_layout.addWidget(self.col_key[i], i, 0)

            self.col_summary.append(QtWidgets.QLabel())
            self.col_summary[i].setFont(self.fnt)
            self.ticket_board_layout.addWidget(self.col_summary[i], i, 1)

            self.col_assigned.append(QtWidgets.QLabel())
            self.col_assigned[i].setFont(self.fnt)
            self.ticket_board_layout.addWidget(self.col_assigned[i], i, 2)

            self.col_last_updated.append(QtWidgets.QLabel())
            self.col_last_updated[i].setFont(self.fnt)
            self.ticket_board_layout.addWidget(self.col_last_updated[i], i, 3)

            self.col_sla.append(QtWidgets.QLabel())
            self.col_sla[i].setFont(self.fnt)
            self.ticket_board_layout.addWidget(self.col_sla[i], i, 4)

        # Fill column titles
        self.fnt.setBold(True)
        self.col_key[0].setFont(self.fnt)
        self.col_key[0].setText("Ticket Number")
        self.col_summary[0].setFont(self.fnt)
        self.col_summary[0].setText("Summary")
        self.col_assigned[0].setFont(self.fnt)
        self.col_assigned[0].setText("Assignee")
        self.col_last_updated[0].setFont(self.fnt)
        self.col_last_updated[0].setText("Last Updated")
        self.col_sla[0].setFont(self.fnt)
        self.col_sla[0].setText("Open for")
        self.fnt.setBold(False)  # Reset font

        self.red_phase = False  # Used to flash rows if red alert

        # Pre-populate ticket list so boards do not stay empty until fetch ticket timeout
        try:
            # Create a JIRA object using netrc credentials
            jira = JIRA(basic_auth=(database.settings.get('username'), database.settings.get('api_key')), options={'server': database.settings.get('jira_url')})
            self.support_tickets = jira.search_issues('status=' + SUPPORT_TICKET_STATUS, maxResults=200)
            self.customer_tickets = jira.search_issues('status=' + CUSTOMER_TICKET_STATUS, maxResults=200)
            self.in_progress_tickets = jira.search_issues('status=' + IN_PROGRESS_TICKET_STATUS, maxResults=200)
            self.dev_tickets = jira.search_issues('status=' + DEV_TICKET_STATUS + ' OR status=new', maxResults=200)
            self.design_tickets = jira.search_issues('status=' + DESIGN_TICKET_STATUS, maxResults=200)
            self.test_tickets = jira.search_issues('status=' + TEST_TICKET_STATUS, maxResults=200)
        except:
            print("Invalid credentials")

        # Timer used to update board
        self.update_board_timer = QtCore.QTimer(self)
        self.update_board_timer.timeout.connect(self.update_board_timeout)
        self.update_board_timer.start(1000)

        # Timer fetch tickets from JIRA server
        self.fetch_tickets_timer = QtCore.QTimer(self)
        self.fetch_tickets_timer.timeout.connect(self.fetch_tickets_timeout)
        self.fetch_tickets_timer.start(2000)  # Fetch tickets every 2 seconds

        # Timer to save ticket stats to db
        self.save_ticket_history_timer = QtCore.QTimer(self)
        self.save_ticket_history_timer.timeout.connect(self.save_ticket_history_timeout)
        self.save_ticket_history_timer.start(5 * 60 * 1000)  # Save every 5 mins

    def update_board_timeout(self):
        self.clear_widgets()
        self.update_board()

    def fetch_tickets_timeout(self):
        self.fetch_tickets_thread = threading.Thread(target=self.fetch_tickets)  # Load thread into obj
        self.fetch_tickets_thread.start()  # Start thread

    def save_ticket_history_timeout(self):
        self.save_ticket_history_thread = threading.Thread(target=self.save_ticket_history)  # Load thread into obj
        self.save_ticket_history_thread.start()  # Start thread

    def fetch_tickets(self):  # Thread for grabbing all tickets used by program
        try:
            # Create a JIRA object using netrc credentials
            jira = JIRA(basic_auth=(database.settings.get('username'), database.settings.get('api_key')), options={'server': database.settings.get('jira_url')})
            self.support_tickets = jira.search_issues('status=' + SUPPORT_TICKET_STATUS, maxResults=200)
            self.customer_tickets = jira.search_issues('status=' + CUSTOMER_TICKET_STATUS, maxResults=200)
            self.in_progress_tickets = jira.search_issues('status=' + IN_PROGRESS_TICKET_STATUS, maxResults=200)
            self.dev_tickets = jira.search_issues('status=' + DEV_TICKET_STATUS + ' OR status=new', maxResults=200)
            self.design_tickets = jira.search_issues('status=' + DESIGN_TICKET_STATUS, maxResults=200)
            self.test_tickets = jira.search_issues('status=' + TEST_TICKET_STATUS, maxResults=200)
        except:
            print("Invalid credentials")

    def save_ticket_history(self):
        database.save_ticket_history(len(self.support_tickets), len(self.customer_tickets), len(self.in_progress_tickets), len(self.dev_tickets), len(self.design_tickets), len(self.test_tickets))

    def clear_widgets(self):  # Ensures table is cleared if less than BOARD_SIZE issues are overdue
        # TODO use .clear to clear widget lists
        for i in range(1, BOARD_SIZE + 1):  # Don't clear first or second row, which contain time and col headings
            self.col_key[i].setText("")
            self.col_summary[i].setText("")
            self.col_assigned[i].setText("")
            self.col_last_updated[i].setText("")
            self.col_sla[i].setText("")

    def update_board(self):
        count = 1  # Prevent write over column titles and datetime

        if (self.red_phase):  # Pulse red_phase for flashing redlert tickets
            self.red_phase = False
        else:
            self.red_phase = True
        try:
            for support_ticket in self.support_tickets:
                date = datetime.now()  # Get current date
                # Truncate and convert string to datetime obj
                ticket_date = parser.parse(support_ticket.fields.updated[0:23])
                last_updated = (date - ticket_date).total_seconds()
                # TODO dynamically get 'customfield_11206 val
                try:  # Get the ongoingCycle SLA, ongoingCycle does not always exist and is never an array
                    open_for_hours = timedelta(seconds=int(support_ticket.raw['fields']['customfield_11206']['ongoingCycle']['elapsedTime']['millis'] / 1000))

                except:  # Grab last dictionary in completedCycles array instead, is always an array
                    open_for_hours = timedelta(seconds=int(support_ticket.raw['fields']['customfield_11206']['completedCycles'][len(support_ticket.raw['fields']['customfield_11206']['completedCycles']) - 1]['elapsedTime']['millis'] / 1000))

                if (last_updated > BLACK_ALERT_DELAY and count <= BOARD_SIZE + 1):  # Only display if board is not full
                    if (last_updated > MELT_DOWN_DELAY):  # Things are serious!
                        self.col_key[count].setStyleSheet('color: red')
                        self.col_summary[count].setStyleSheet('color: red')
                        self.col_assigned[count].setStyleSheet('color: red')
                        self.col_last_updated[count].setStyleSheet('color: red')
                        self.col_sla[count].setStyleSheet('color: red')
                    elif (last_updated > RED_ALERT_DELAY):  # Things are not so Ok
                        if (self.red_phase):
                            self.col_key[count].setStyleSheet('color: red')
                            self.col_summary[count].setStyleSheet('color: red')
                            self.col_assigned[count].setStyleSheet('color: red')
                            self.col_last_updated[count].setStyleSheet('color: red')
                            self.col_sla[count].setStyleSheet('color: red')
                        else:
                            self.col_key[count].setStyleSheet('color: black')
                            self.col_summary[count].setStyleSheet('color: black')
                            self.col_assigned[count].setStyleSheet('color: black')
                            self.col_last_updated[count].setStyleSheet('color: black')
                            self.col_sla[count].setStyleSheet('color: black')
                    else:  # Things are still Okish
                        self.col_key[count].setStyleSheet('color: black')
                        self.col_summary[count].setStyleSheet('color: black')
                        self.col_assigned[count].setStyleSheet('color: black')
                        self.col_last_updated[count].setStyleSheet('color: black')
                        self.col_sla[count].setStyleSheet('color: black')
                    self.col_key[count].setText(str(support_ticket.key))
                    self.col_summary[count].setText(str(support_ticket.fields.summary))
                    self.col_assigned[count].setText(str(support_ticket.fields.assignee))
                    self.col_last_updated[count].setText(str(support_ticket.fields.updated))
                    self.col_sla[count].setText(str(open_for_hours))
                    count = count + 1

        except:
            print("No support tickets")
