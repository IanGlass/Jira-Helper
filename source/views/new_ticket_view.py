
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QLabel
from PyQt5.QtGui import QFont
from PyQt5 import QtCore


class NewTicketView(QMainWindow):
    def __init__(self):
        super(NewTicketView, self).__init__()
        new_ticket_widget = QWidget()
        new_ticket_layout = QGridLayout()
        new_ticket_widget.setLayout(new_ticket_layout)
        self.setCentralWidget(new_ticket_widget)
        self.setWindowTitle('New Ticket')

        title = QLabel()
        title.setFont(QFont("Times", 20))
        title.setText('New Ticket!!!')
        new_ticket_layout.addWidget(title, 0, 0, 0, 4, QtCore.Qt.AlignCenter)

        self.key = QLabel()
        self.key.setFont(QFont("Times", 14))
        self.reporter = QLabel()
        self.reporter.setFont(QFont("Times", 14))
        self.summary = QLabel()
        self.summary.setFont(QFont("Times", 14))
        new_ticket_layout.addWidget(self.key, 3, 0)
        new_ticket_layout.addWidget(self.reporter, 3, 1)
        new_ticket_layout.addWidget(self.summary, 3, 3)


if __name__ == 'new_ticket_view':
    print('Instantiating ' + __name__)
    new_ticket_view = NewTicketView()
