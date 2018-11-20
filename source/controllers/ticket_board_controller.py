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

# TODO use setStyleSheet() instead of setFont

class TicketBoardController(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        # Pre-populate ticket list so boards do not stay empty until fetch ticket timeout
        #jira_model.fetch_tickets()

        # Timer used to update board
        self.update_board_timer = QtCore.QTimer(self)
        self.update_board_timer.timeout.connect(ticket_board_view.update_board)
        self.update_board_timer.start(1000)

        # Timer fetch tickets from JIRA server
        self.fetch_tickets_timer = QtCore.QTimer(self)
        self.fetch_tickets_timer.timeout.connect(self.fetch_tickets_timeout)
        self.fetch_tickets_timer.start(2000)  # Fetch tickets every 2 seconds

        # Timer to save ticket stats to db
        self.save_ticket_history_timer = QtCore.QTimer(self)
        self.save_ticket_history_timer.timeout.connect(self.save_ticket_history_timeout)
        self.save_ticket_history_timer.start(5 * 60 * 1000)  # Save every 5 mins

    def fetch_tickets_timeout(self):
        self.fetch_tickets_thread = threading.Thread(target=jira_model.fetch_tickets)  # Load thread into obj
        self.fetch_tickets_thread.start()  # Start thread

    def save_ticket_history_timeout(self):
        self.save_ticket_history_thread = threading.Thread(target=jira_model.save_ticket_history)  # Load thread into obj
        self.save_ticket_history_thread.start()  # Start thread
    
    
if __name__ == 'ticket_board_controller':
    ticket_board_controller = TicketBoardController()