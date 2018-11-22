import sys
from PyQt5 import QtCore, QtWidgets, QtGui
# Used to covert and import datetime
from PyQt5.QtCore import QDate, QTime, Qt

from jira import JIRA
import threading
from datetime import datetime
# Used to truncate and convert string to datetime Obj
from dateutil import parser
from operator import itemgetter

from jira_model import jira_model
from build_board_view import build_board_view


class BuildBoardController(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Timer update build progress
        self.update_datetime_timer = QtCore.QTimer(self)
        self.update_datetime_timer.timeout.connect(build_board_view.update_board)
        self.update_datetime_timer.start(10000)  # update every 1 second


if __name__ == 'build_board_controller':
    build_board_controller = BuildBoardController()
