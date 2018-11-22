# Creates a QWidget to display overdue tickets in the waiting for support queue. Tickets are fetched using a JIRA api and filtered for last_updated > overdue time. Module also saves the ticket history to the local db.

# GUI
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from datetime import timedelta
from datetime import datetime
# Used to truncate and convert string to datetime Obj
from dateutil import parser
from jira import JIRA
from PyQt5.QtCore import QDate, QTime, Qt
import threading

from jira_model import jira_model
from ticket_board_view import ticket_board_view
from database_model import database_model


class TicketBoardController(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        # Timer used to update board
        self.update_board_timer = QtCore.QTimer(self)
        self.update_board_timer.timeout.connect(ticket_board_view.update_board)
        self.update_board_timer.start(1000)


if __name__ == 'ticket_board_controller':
    ticket_board_controller = TicketBoardController()
