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

from analytics_board_view import analytics_board_view
from database_model import database_model
from jira_model import jira_model

FONT = "Times"  # Font used to display text
FONT_SIZE = 12

FROM_ZONE = tz.tzutc()
TO_ZONE = tz.tzlocal()


class AnalyticsBoardController(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Timer used to update the analytics page
        self.update_analytics_timer = QtCore.QTimer(self)
        self.update_analytics_timer.timeout.connect(analytics_board_view.update_analytics)
        self.update_analytics_timer.start(1000)  # Update every second


if __name__ == 'analytics_board_controller':
    analytics_board_controller = AnalyticsBoardController()
