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

from database_model import database_model
from main_view import main_view
from jira_model import jira_model

FONT = "Times"  # Font used to display text
FONT_SIZE = 12

BOARD_SIZE = 25

# TODO use setStyleSheet() instead of setFont

class TicketBoardView(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.ticket_board_widget = QtWidgets.QWidget()  # Create the widget to contain the ticket board layout
        self.ticket_board_layout = QtWidgets.QGridLayout()  # Layout for ticket board
        self.ticket_board_widget.setLayout(self.ticket_board_layout)

        self.col_key = list()
        self.col_assigned = list()
        self.col_summary = list()
        self.col_last_updated = list()
        self.col_sla = list()

        self.fnt = QtGui.QFont(FONT, FONT_SIZE)
        for i in range(0, BOARD_SIZE + 1):  # Build the ticket board
            self.col_key.append(QtWidgets.QLabel())
            self.col_key[i].setFont(self.fnt)
            self.ticket_board_layout.addWidget(self.col_key[i], i, 0)

            self.col_summary.append(QtWidgets.QLabel())
            self.col_summary[i].setFont(self.fnt)
            self.ticket_board_layout.addWidget(self.col_summary[i], i, 1)

            self.col_assigned.append(QtWidgets.QLabel())
            self.col_assigned[i].setFont(self.fnt)
            self.ticket_board_layout.addWidget(self.col_assigned[i], i, 2)

            self.col_last_updated.append(QtWidgets.QLabel())
            self.col_last_updated[i].setFont(self.fnt)
            self.ticket_board_layout.addWidget(self.col_last_updated[i], i, 3)

            self.col_sla.append(QtWidgets.QLabel())
            self.col_sla[i].setFont(self.fnt)
            self.ticket_board_layout.addWidget(self.col_sla[i], i, 4)

        # Fill column titles
        self.fnt.setBold(True)
        self.col_key[0].setFont(self.fnt)
        self.col_key[0].setText("Ticket Number")
        self.col_summary[0].setFont(self.fnt)
        self.col_summary[0].setText("Summary")
        self.col_assigned[0].setFont(self.fnt)
        self.col_assigned[0].setText("Assignee")
        self.col_last_updated[0].setFont(self.fnt)
        self.col_last_updated[0].setText("Last Updated")
        self.col_sla[0].setFont(self.fnt)
        self.col_sla[0].setText("Open for")
        self.fnt.setBold(False)  # Reset font

        self.red_phase = False  # Used to flash rows if red alert

    def clear_widgets(self):  # Ensures table is cleared if less than BOARD_SIZE issues are overdue
        # TODO use .clear to clear widget lists
        for i in range(1, BOARD_SIZE + 1):  # Don't clear first or second row, which contain time and col headings
            self.col_key[i].setText("")
            self.col_summary[i].setText("")
            self.col_assigned[i].setText("")
            self.col_last_updated[i].setText("")
            self.col_sla[i].setText("")

    def update_board(self):
        self.clear_widgets()
        count = 1  # Prevent write over column titles and datetime

        if (self.red_phase):  # Pulse red_phase for flashing redlert tickets
            self.red_phase = False
        else:
            self.red_phase = True
        # try:
        for support_ticket in jira_model.support_tickets:
            date = datetime.now()  # Get current date
            # Truncate and convert string to datetime obj
            ticket_date = parser.parse(support_ticket.fields.updated[0:23])
            last_updated = (date - ticket_date).total_seconds()
            # TODO dynamically get 'customfield_11206 val
            try:  # Get the ongoingCycle SLA, ongoingCycle does not always exist and is never an array
                open_for_hours = timedelta(seconds=int(support_ticket.raw['fields']['customfield_11206']['ongoingCycle']['elapsedTime']['millis'] / 1000))

            except:  # Grab last dictionary in completedCycles array instead, is always an array
                open_for_hours = timedelta(seconds=int(support_ticket.raw['fields']['customfield_11206']['completedCycles'][len(support_ticket.raw['fields']['customfield_11206']['completedCycles']) - 1]['elapsedTime']['millis'] / 1000))

            if (last_updated > database_model.settings['black_alert'] and count <= BOARD_SIZE + 1):  # Only display if board is not full
                if (last_updated > database_model.settings['melt_down']):  # Things are serious!
                    self.col_key[count].setStyleSheet('color: red')
                    self.col_summary[count].setStyleSheet('color: red')
                    self.col_assigned[count].setStyleSheet('color: red')
                    self.col_last_updated[count].setStyleSheet('color: red')
                    self.col_sla[count].setStyleSheet('color: red')
                elif (last_updated > database_model.settings['red_alert']):  # Things are not so Ok
                    if (self.red_phase):
                        self.col_key[count].setStyleSheet('color: red')
                        self.col_summary[count].setStyleSheet('color: red')
                        self.col_assigned[count].setStyleSheet('color: red')
                        self.col_last_updated[count].setStyleSheet('color: red')
                        self.col_sla[count].setStyleSheet('color: red')
                    else:
                        self.col_key[count].setStyleSheet('color: black')
                        self.col_summary[count].setStyleSheet('color: black')
                        self.col_assigned[count].setStyleSheet('color: black')
                        self.col_last_updated[count].setStyleSheet('color: black')
                        self.col_sla[count].setStyleSheet('color: black')
                else:  # Things are still Okish
                    self.col_key[count].setStyleSheet('color: black')
                    self.col_summary[count].setStyleSheet('color: black')
                    self.col_assigned[count].setStyleSheet('color: black')
                    self.col_last_updated[count].setStyleSheet('color: black')
                    self.col_sla[count].setStyleSheet('color: black')
                self.col_key[count].setText(str(support_ticket.key))
                self.col_summary[count].setText(str(support_ticket.fields.summary))
                self.col_assigned[count].setText(str(support_ticket.fields.assignee))
                self.col_last_updated[count].setText(str(support_ticket.fields.updated))
                self.col_sla[count].setText(str(open_for_hours))
                count = count + 1

        # except:
        #     print("No support tickets")


if __name__ == 'ticket_board_view':
    ticket_board_view = TicketBoardView()
    # Add the ticket board widget/layout to the main window widget
    main_view.window.addWidget(ticket_board_view.ticket_board_widget) 
