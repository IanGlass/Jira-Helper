# Creates a QWidget containing a graph of ticket history in waiting on support, waiting on customer and in progress. Also displays the current number of tickets in waiting for support, waiting for customer, in progress, dev, design and test. Ticket history is grabbed from a local database using psycopg2

# GUI
import sys
from PyQt5 import QtCore, QtWidgets, QtGui

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from dateutil import tz   # Used to convert local-UTC
from datetime import datetime

from jira import JIRA

import threading

from database import database

FONT = "Times"  # Font used to display text
FONT_SIZE = 12

FROM_ZONE = tz.tzutc()
TO_ZONE = tz.tzlocal()


class AnalyticsBoard(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.analytics_board_widget = QtWidgets.QWidget()  # Create the widget to contain the analytics board layout
        self.analytics_board_layout = QtWidgets.QGridLayout()  # Layout for analytics board
        self.analytics_board_widget.setLayout(self.analytics_board_layout)

        self.figure = Figure(figsize=(7, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.analytics_board_layout.addWidget(self.canvas, 3, 0, -1, 6)  # Add plot to analytics board
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel('date')
        self.ax.set_ylabel('# of tickets')
        self.figure.patch.set_facecolor([240 / 255, 240 / 255, 240 / 255, 1])

        self.col_support = list()
        self.col_customer = list()
        self.col_in_progress = list()
        self.col_dev = list()
        self.col_design = list()
        self.col_test = list()

        self.fnt = QtGui.QFont(FONT, FONT_SIZE)
        for i in range(0, 10):
            self.col_support.append(QtWidgets.QLabel())
            self.col_support[i].setFont(self.fnt)
            self.analytics_board_layout.addWidget(self.col_support[i], i, 0)

            self.col_customer.append(QtWidgets.QLabel())
            self.col_customer[i].setFont(self.fnt)
            self.analytics_board_layout.addWidget(self.col_customer[i], i, 1)

            self.col_in_progress.append(QtWidgets.QLabel())
            self.col_in_progress[i].setFont(self.fnt)
            self.analytics_board_layout.addWidget(self.col_in_progress[i], i, 2)

            self.col_dev.append(QtWidgets.QLabel())
            self.col_dev[i].setFont(self.fnt)
            self.analytics_board_layout.addWidget(self.col_dev[i], i, 3)

            self.col_design.append(QtWidgets.QLabel())
            self.col_design[i].setFont(self.fnt)
            self.analytics_board_layout.addWidget(self.col_design[i], i, 4)

            self.col_test.append(QtWidgets.QLabel())
            self.col_test[i].setFont(self.fnt)
            self.analytics_board_layout.addWidget(self.col_test[i], i, 5)

        # Fill column titles
        self.fnt.setBold(True)
        self.col_support[0].setFont(self.fnt)
        self.col_support[0].setText("# of support tickets")
        self.col_customer[0].setFont(self.fnt)
        self.col_customer[0].setText("# of customer tickets")
        self.col_in_progress[0].setFont(self.fnt)
        self.col_in_progress[0].setText("# of tickets in Progress")
        self.col_dev[0].setFont(self.fnt)
        self.col_dev[0].setText("# of tickest in dev")
        self.col_design[0].setFont(self.fnt)
        self.col_design[0].setText("# of tickest in design")
        self.col_test[0].setFont(self.fnt)
        self.col_test[0].setText("# of tickest in test")
        self.fnt.setBold(False)  # Reset font

        self.date_history = list()
        self.support_history = list()
        self.in_progress_history = list()
        self.customer_history = list()

        try:
            # Create a JIRA object using netrc credentials
            jira = JIRA(basic_auth=(database.settings['username'], database.settings['api_key']), options={'server': database.settings['jira_url']})
            self.support_tickets = jira.search_issues('status=' + database.settings['support_status'].replace(" ", "\ "), maxResults=200)
            self.customer_tickets = jira.search_issues('status=' + database.settings['customer_status'].replace(" ", "\ "), maxResults=200)
            self.in_progress_tickets = jira.search_issues('status=' + database.settings['in_progress_status'].replace(" ", "\ "), maxResults=200)
            self.dev_tickets = jira.search_issues('status=' + database.settings['dev_status'].replace(" ", "\ ") + ' OR status=new', maxResults=200)
            self.design_tickets = jira.search_issues('status=' + database.settings['design_status'].replace(" ", "\ "), maxResults=200)
            self.test_tickets = jira.search_issues('status=' + database.settings['test_status'].replace(" ", "\ "), maxResults=200)
        except:
            print("Invalid credentials")

        # Timer used to update the analytics page
        self.update_analytics_timer = QtCore.QTimer(self)
        self.update_analytics_timer.timeout.connect(self.update_analytics_timeout)
        self.update_analytics_timer.start(1000)  # Update every second

        # Timer fetch tickets from JIRA server
        self.fetch_tickets_timer = QtCore.QTimer(self)
        self.fetch_tickets_timer.timeout.connect(self.fetch_tickets_timeout)
        self.fetch_tickets_timer.start(2000)  # Fetch tickets every 2 seconds

    def update_analytics_timeout(self):
        self.update_analytics_thread = threading.Thread(target=self.update_analytics)  # Load thread into obj
        self.update_analytics_thread.start()  # Start thread

    def fetch_tickets_timeout(self):
        self.fetch_tickets_thread = threading.Thread(target=self.fetch_tickets)  # Load thread into obj
        self.fetch_tickets_thread.start()  # Start thread

    def fetch_tickets(self):  # Thread for grabbing all tickets used by program
        try:
            # Create a JIRA object using netrc credentials
            jira = JIRA(basic_auth=(database.settings['username'], database.settings['api_key']), options={'server': database.settings['jira_url']})
            self.support_tickets = jira.search_issues('status=' + database.settings['support_status'].replace(" ", "\ "), maxResults=200)
            self.customer_tickets = jira.search_issues('status=' + database.settings['customer_status'].replace(" ", "\ "), maxResults=200)
            self.in_progress_tickets = jira.search_issues('status=' + database.settings['in_progress_status'].replace(" ", "\ "), maxResults=200)
            self.dev_tickets = jira.search_issues('status=' + database.settings['dev_status'].replace(" ", "\ ") + ' OR status=new', maxResults=200)
            self.design_tickets = jira.search_issues('status=' + database.settings['design_status'].replace(" ", "\ "), maxResults=200)
            self.test_tickets = jira.search_issues('status=' + database.settings['test_status'].replace(" ", "\ "), maxResults=200)
        except:
            print("Invalid credentials")

    def update_analytics(self):
        self.ticket_history = database.fetch_ticket_history()

        if not self.ticket_history:  # db was empty so prevent errors
            date = datetime.now()
            self.ticket_history.append([date, 0, 0, 0, 0, 0, 0])

        # Empty lists so we don't get double ups
        self.date_history.clear()
        self.support_history.clear()
        self.in_progress_history.clear()
        self.customer_history.clear()

        # TODO this is horrible
        for i in range(0, len(self.ticket_history)):
            # Add timedate to date_history from UTC to local time zone
            self.date_history.append(self.ticket_history[i][0].astimezone(TO_ZONE))
            self.support_history.append(self.ticket_history[i][1])
            self.in_progress_history.append(self.ticket_history[i][2])
            self.customer_history.append(self.ticket_history[i][3])

        self.col_support[1].setText(str(len(self.support_tickets)))
        self.col_customer[1].setText(str(len(self.customer_tickets)))
        self.col_in_progress[1].setText(str(len(self.in_progress_tickets)))
        self.col_dev[1].setText(str(len(self.dev_tickets)))
        self.col_design[1].setText(str(len(self.design_tickets)))
        self.col_test[1].setText(str(len(self.test_tickets)))

        self.ax.clear()
        self.ax.plot(self.date_history, self.support_history, 'r-', label='waiting for support')
        self.ax.plot(self.date_history, self.customer_history, 'b-', label='waiting for customer')
        self.ax.plot(self.date_history, self.in_progress_history, 'g-', label='in progress')
        self.ax.legend(loc='best')
        self.canvas.draw()
