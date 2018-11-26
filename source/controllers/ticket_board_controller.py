# Creates a QWidget to display overdue tickets in the waiting for support queue. Tickets are fetched using a JIRA api and filtered for last_updated > overdue time. Module also saves the ticket history to the local db.

# GUI
import sys
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer

from jira_model import jira_model
from ticket_board_view import ticket_board_view
from database_model import database_model


class TicketBoardController(QMainWindow):

    def __init__(self):
        super().__init__()
        # Timer used to update board
        self.update_board_timer = QTimer(self)
        self.update_board_timer.timeout.connect(ticket_board_view.update_board)
        self.update_board_timer.start(1000)


if __name__ == 'ticket_board_controller':
    ticket_board_controller = TicketBoardController()
