
from PyQt5.QtCore import QTimer, QObject
# from PyQt5.QtWidgets import

from new_ticket_view import new_ticket_view


class NewTicketController(QObject):
    def __init__(self):
        super(NewTicketController, self).__init__()

        # Timer update board
        self.close_window_timer = QTimer(self)
        self.close_window_timer.timeout.connect(self.close_window_timeout)

    def show_window(self, key, reporter, summary):
        new_ticket_view.key.setText(key)
        new_ticket_view.reporter.setText(str(reporter))
        new_ticket_view.summary.setText(summary)
        new_ticket_view.show()
        new_ticket_view.resize(1000, 150)
        self.close_window_timer.start(10000)  # Keep window open for 10 seconds

    def close_window_timeout(self):
        new_ticket_view.close()
        self.close_window_timer.stop()


if __name__ == 'new_ticket_controller':
    print('Instantiating ' + __name__)
    new_ticket_controller = NewTicketController()
