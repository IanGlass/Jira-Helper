# Creates a QWidget containing a graph of ticket history in waiting on support, waiting on customer and in progress. Also displays the current number of tickets in waiting for support, waiting for customer, in progress, dev, design and test. Ticket history is grabbed from a local database using psycopg2

# GUI
import sys
from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QLabel

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from dateutil import tz   # Used to convert local-UTC
from datetime import datetime

from main_view import main_view
from jira_model import jira_model
from database_model import database_model

FROM_ZONE = tz.tzutc()
TO_ZONE = tz.tzlocal()


class AnalyticsBoardView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.analytics_board_widget = QWidget()  # Create the widget to contain the analytics board layout
        self.analytics_board_layout = QGridLayout()  # Layout for analytics board
        self.analytics_board_widget.setLayout(self.analytics_board_layout)

        # Create a page title
        title = QLabel()
        title_font = QFont("Times", 20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setText('Ticket Analytics')
        self.analytics_board_layout.addWidget(title, 0, 0, 1, 0, QtCore.Qt.AlignCenter)

        # Create column headers
        header_font = QFont("Times", 12)
        header_font.setBold(True)

        support_header = QLabel()
        support_header.setFont(header_font)
        support_header.setText("# of support tickets")
        self.analytics_board_layout.addWidget(support_header, 1, 0, QtCore.Qt.AlignCenter)

        customer_header = QLabel()
        customer_header.setFont(header_font)
        customer_header.setText("# of support tickets")
        self.analytics_board_layout.addWidget(customer_header, 1, 1, QtCore.Qt.AlignCenter)

        in_progress_header = QLabel()
        in_progress_header.setFont(header_font)
        in_progress_header.setText("# of tickets in Progress")
        self.analytics_board_layout.addWidget(in_progress_header, 1, 2, QtCore.Qt.AlignCenter)

        dev_header = QLabel()
        dev_header.setFont(header_font)
        dev_header.setText("# of tickets in Dev")
        self.analytics_board_layout.addWidget(dev_header, 1, 3, QtCore.Qt.AlignCenter)

        design_header = QLabel()
        design_header.setFont(header_font)
        design_header.setText("# of tickets in Design")
        self.analytics_board_layout.addWidget(design_header, 1, 4, QtCore.Qt.AlignCenter)

        test_header = QLabel()
        test_header.setFont(header_font)
        test_header.setText("# of tickets in Test")
        self.analytics_board_layout.addWidget(test_header, 1, 5, QtCore.Qt.AlignCenter)

        self.col_support = list()
        self.col_customer = list()
        self.col_in_progress = list()
        self.col_dev = list()
        self.col_design = list()
        self.col_test = list()

        self.fnt = QFont("Times", 12)
        for i in range(0, 10):  # TODO not a great way to space between graph and cols
            self.col_support.append(QLabel())
            self.col_support[i].setFont(self.fnt)
            self.analytics_board_layout.addWidget(self.col_support[i], i + 1, 0, QtCore.Qt.AlignCenter)

            self.col_customer.append(QLabel())
            self.col_customer[i].setFont(self.fnt)
            self.analytics_board_layout.addWidget(self.col_customer[i], i + 1, 1, QtCore.Qt.AlignCenter)

            self.col_in_progress.append(QLabel())
            self.col_in_progress[i].setFont(self.fnt)
            self.analytics_board_layout.addWidget(self.col_in_progress[i], i + 1, 2, QtCore.Qt.AlignCenter)

            self.col_dev.append(QLabel())
            self.col_dev[i].setFont(self.fnt)
            self.analytics_board_layout.addWidget(self.col_dev[i], i + 1, 3, QtCore.Qt.AlignCenter)

            self.col_design.append(QLabel())
            self.col_design[i].setFont(self.fnt)
            self.analytics_board_layout.addWidget(self.col_design[i], i + 1, 4, QtCore.Qt.AlignCenter)

            self.col_test.append(QLabel())
            self.col_test[i].setFont(self.fnt)
            self.analytics_board_layout.addWidget(self.col_test[i], i + 1, 5, QtCore.Qt.AlignCenter)

        # Create a graph
        self.figure = Figure(figsize=(7, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.analytics_board_layout.addWidget(self.canvas, 3, 0, -1, 6)  # Add plot to analytics board
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel('date')
        self.ax.set_ylabel('# of tickets')
        self.figure.patch.set_facecolor([240 / 255, 240 / 255, 240 / 255, 1])

        # Global vars
        self.date_history = list()
        self.support_history = list()
        self.in_progress_history = list()
        self.customer_history = list()

    def update_analytics(self):
        self.ticket_history = database_model.fetch_ticket_history()

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

        try:
            self.col_support[1].setText(str(len(jira_model.support_tickets)))
            self.col_customer[1].setText(str(len(jira_model.customer_tickets)))
            self.col_in_progress[1].setText(str(len(jira_model.in_progress_tickets)))
            self.col_dev[1].setText(str(len(jira_model.dev_tickets)))
            self.col_design[1].setText(str(len(jira_model.design_tickets)))
            self.col_test[1].setText(str(len(jira_model.test_tickets)))

        except:
            print('Missing queue status configuration')

        self.ax.clear()
        self.ax.plot(self.date_history, self.support_history, 'r-', label='waiting for support')
        self.ax.plot(self.date_history, self.customer_history, 'b-', label='waiting for customer')
        self.ax.plot(self.date_history, self.in_progress_history, 'g-', label='in progress')
        self.ax.legend(loc='best')
        self.canvas.draw()


if __name__ == 'analytics_board_view':
    print('Instantiating analytics_view')
    analytics_board_view = AnalyticsBoardView()
    # Add the analytics board widget/layout to the main window widget
    main_view.window.addWidget(analytics_board_view.analytics_board_widget)
