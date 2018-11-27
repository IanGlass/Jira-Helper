# Creates a QWidget containing a graph of ticket history in waiting on support, waiting on customer and in progress. Also displays the current number of tickets in waiting for support, waiting for customer, in progress, dev, design and test. Ticket history is grabbed from a local database using psycopg2

# GUI
import sys
from PyQt5.QtCore import QTimer, QObject

from analytics_board_view import analytics_board_view
from jira_service import jira_service


class AnalyticsBoardController(QObject):
    def __init__(self):
        super(AnalyticsBoardController, self).__init__()

        # Timer used to update the analytics page
        update_analytics_timer = QTimer(self)
        update_analytics_timer.timeout.connect(analytics_board_view.update_analytics)
        update_analytics_timer.start(1000)  # Update every second


if __name__ == 'analytics_board_controller':
    analytics_board_controller = AnalyticsBoardController()
