# Creates a QWidget to display overdue tickets in the waiting for support queue. Tickets are fetched using a JIRA api and filtered for last_updated > overdue time. Module also saves the ticket history to the local db.

# GUI
import sys
from PyQt5.QtCore import QTimer, QObject

from jira_service import jira_service
from ticket_board_view import ticket_board_view


class TicketBoardController(QObject):
    def __init__(self):
        super(TicketBoardController, self).__init__()
        # Timer used to update board
        update_ticket_board_timer = QTimer(self)
        update_ticket_board_timer.timeout.connect(ticket_board_view.update_board)
        update_ticket_board_timer.start(1000)


if __name__ == 'ticket_board_controller':
    print('Instantiating ' + __name__)
    ticket_board_controller = TicketBoardController()
