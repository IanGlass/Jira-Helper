# Creates a QWidget containing a graph of ticket history in waiting on support, waiting on customer and in progress. Also displays the current number of tickets in waiting for support, waiting for customer, in progress, dev, design and test. Ticket history is grabbed from a local database using psycopg2

import sys
from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from dateutil import tz   # Used to convert local-UTC
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main_view import main_view
from jira_service import jira_service
from ticket_history_model import TicketHistoryModel, Base

FROM_ZONE = tz.tzutc()
TO_ZONE = tz.tzlocal()


class AnalyticsBoardView(QWidget):
    def __init__(self):
        super(AnalyticsBoardView, self).__init__()
        engine = create_engine('sqlite:///jira_helper.db')
        Base.metadata.bind = engine
        self.DBSession = sessionmaker(bind=engine)

        analytics_board_layout = QGridLayout()  # Layout for analytics board
        self.setLayout(analytics_board_layout)

        # Create a page title
        title = QLabel()
        title_font = QFont("Times", 20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setText('Ticket Analytics')
        analytics_board_layout.addWidget(title, 0, 0, 1, 0, QtCore.Qt.AlignCenter)

        # Create column headers
        header_font = QFont("Times", 12)
        header_font.setBold(True)

        support_header = QLabel()
        support_header.setFont(header_font)
        support_header.setText("# of support tickets")
        analytics_board_layout.addWidget(support_header, 1, 0, QtCore.Qt.AlignCenter)

        customer_header = QLabel()
        customer_header.setFont(header_font)
        customer_header.setText("# of customer tickets")
        analytics_board_layout.addWidget(customer_header, 1, 1, QtCore.Qt.AlignCenter)

        in_progress_header = QLabel()
        in_progress_header.setFont(header_font)
        in_progress_header.setText("# of tickets in Progress")
        analytics_board_layout.addWidget(in_progress_header, 1, 2, QtCore.Qt.AlignCenter)

        dev_header = QLabel()
        dev_header.setFont(header_font)
        dev_header.setText("# of tickets in Dev")
        analytics_board_layout.addWidget(dev_header, 1, 3, QtCore.Qt.AlignCenter)

        design_header = QLabel()
        design_header.setFont(header_font)
        design_header.setText("# of tickets in Design")
        analytics_board_layout.addWidget(design_header, 1, 4, QtCore.Qt.AlignCenter)

        test_header = QLabel()
        test_header.setFont(header_font)
        test_header.setText("# of tickets in Test")
        analytics_board_layout.addWidget(test_header, 1, 5, QtCore.Qt.AlignCenter)

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
            analytics_board_layout.addWidget(self.col_support[i], i + 1, 0, QtCore.Qt.AlignCenter)

            self.col_customer.append(QLabel())
            self.col_customer[i].setFont(self.fnt)
            analytics_board_layout.addWidget(self.col_customer[i], i + 1, 1, QtCore.Qt.AlignCenter)

            self.col_in_progress.append(QLabel())
            self.col_in_progress[i].setFont(self.fnt)
            analytics_board_layout.addWidget(self.col_in_progress[i], i + 1, 2, QtCore.Qt.AlignCenter)

            self.col_dev.append(QLabel())
            self.col_dev[i].setFont(self.fnt)
            analytics_board_layout.addWidget(self.col_dev[i], i + 1, 3, QtCore.Qt.AlignCenter)

            self.col_design.append(QLabel())
            self.col_design[i].setFont(self.fnt)
            analytics_board_layout.addWidget(self.col_design[i], i + 1, 4, QtCore.Qt.AlignCenter)

            self.col_test.append(QLabel())
            self.col_test[i].setFont(self.fnt)
            analytics_board_layout.addWidget(self.col_test[i], i + 1, 5, QtCore.Qt.AlignCenter)

        # Create a graph
        self.figure = Figure(figsize=(7, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        analytics_board_layout.addWidget(self.canvas, 3, 0, -1, 6)  # Add plot to analytics board
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel('date')
        self.ax.set_ylabel('# of tickets')
        self.figure.patch.set_facecolor([240 / 255, 240 / 255, 240 / 255, 1])

    def update_analytics(self):
        # try:
        session = self.DBSession()
        date_history = session.query(TicketHistoryModel.stamp).filter(TicketHistoryModel.stamp > (datetime.now() - timedelta(weeks=2))).all()
        support_history = session.query(TicketHistoryModel.support).filter(TicketHistoryModel.stamp > (datetime.now() - timedelta(weeks=2))).all()
        customer_history = session.query(TicketHistoryModel.customer).filter(TicketHistoryModel.stamp > (datetime.now() - timedelta(weeks=2))).all()
        in_progress_history = session.query(TicketHistoryModel.in_progress).filter(TicketHistoryModel.stamp > (datetime.now() - timedelta(weeks=2))).all()
        session.close()
        # Updates overall numbers view
        self.col_support[1].setText(str(len(jira_service.support_tickets)))
        self.col_customer[1].setText(str(len(jira_service.customer_tickets)))
        self.col_in_progress[1].setText(str(len(jira_service.in_progress_tickets)))
        self.col_dev[1].setText(str(len(jira_service.dev_tickets)))
        self.col_design[1].setText(str(len(jira_service.design_tickets)))
        self.col_test[1].setText(str(len(jira_service.test_tickets)))

        self.ax.clear()
        self.ax.plot(date_history, support_history, 'r-', label='waiting for support')
        self.ax.plot(date_history, customer_history, 'b-', label='waiting for customer')
        self.ax.plot(date_history, in_progress_history, 'g-', label='in progress')
        self.ax.legend(loc='best')
        self.canvas.draw()

        # except:
        #     print('Missing queue status configuration')


if __name__ == 'analytics_board_view':
    print('Instantiating analytics_view')
    analytics_board_view = AnalyticsBoardView()
    # Add the analytics board widget/layout to the main window widget
    main_view.window.addWidget(analytics_board_view)
