# Creates a QWidget to display overdue tickets in the waiting for support queue. Tickets are fetched using a JIRA api and filtered for last_updated > overdue time. Module also saves the ticket history to the local db.

import sys
from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt5.QtCore import QDate, QTime, Qt
from datetime import timedelta
from datetime import datetime
# Used to truncate and convert string to datetime Obj
from dateutil import parser

from database_model import database_model
from main_view import main_view
from jira_model import jira_model

BOARD_SIZE = 25


class TicketBoardView(QWidget):
    def __init__(self):
        super().__init__()
        ticket_board_layout = QGridLayout()  # Layout for ticket board
        self.setLayout(ticket_board_layout)

        # Create a page title
        title = QLabel()
        title_font = QFont("Times", 20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setText('Overdue Support Tickets')
        ticket_board_layout.addWidget(title, 0, 0, 1, 0, QtCore.Qt.AlignCenter)

        # Create column headers
        header_font = QFont("Times", 12)
        header_font.setBold(True)

        key_header = QLabel()
        key_header.setFont(header_font)
        key_header.setText("Ticket Number")
        ticket_board_layout.addWidget(key_header, 1, 0)

        summary_header = QLabel()
        summary_header.setFont(header_font)
        summary_header.setText("Summary")
        ticket_board_layout.addWidget(summary_header, 1, 1)

        assigned_header = QLabel()
        assigned_header.setFont(header_font)
        assigned_header.setText("Assignee")
        ticket_board_layout.addWidget(assigned_header, 1, 2)

        last_updated_header = QLabel()
        last_updated_header.setFont(header_font)
        last_updated_header.setText("Last Updated")
        ticket_board_layout.addWidget(last_updated_header, 1, 3)

        sla_header = QLabel()
        sla_header.setFont(header_font)
        sla_header.setText("Open for")
        ticket_board_layout.addWidget(sla_header, 1, 4)

        # Build the ticket board
        self.col_key = list()
        self.col_assigned = list()
        self.col_summary = list()
        self.col_last_updated = list()
        self.col_sla = list()
        text_font = QFont("Times", 12)
        for i in range(0, BOARD_SIZE):
            self.col_key.append(QLabel())
            self.col_key[i].setFont(text_font)
            ticket_board_layout.addWidget(self.col_key[i], i + 2, 0)

            self.col_summary.append(QLabel())
            self.col_summary[i].setFont(text_font)
            ticket_board_layout.addWidget(self.col_summary[i], i + 2, 1)

            self.col_assigned.append(QLabel())
            self.col_assigned[i].setFont(text_font)
            ticket_board_layout.addWidget(self.col_assigned[i], i + 2, 2)

            self.col_last_updated.append(QLabel())
            self.col_last_updated[i].setFont(text_font)
            ticket_board_layout.addWidget(self.col_last_updated[i], i + 2, 3)

            self.col_sla.append(QLabel())
            self.col_sla[i].setFont(text_font)
            ticket_board_layout.addWidget(self.col_sla[i], i + 2, 4)

        self.red_phase = False  # Used to flash rows if red alert

    def clear_widgets(self):  # Ensures table is cleared if less than BOARD_SIZE issues are overdue
        for i in range(0, BOARD_SIZE):
            self.col_key[i].clear()
            self.col_summary[i].clear()
            self.col_assigned[i].clear()
            self.col_last_updated[i].clear()
            self.col_sla[i].clear()

    def update_board(self):
        self.clear_widgets()
        count = 0
        if (self.red_phase):  # Pulse red_phase for flashing redlert tickets
            self.red_phase = False
        else:
            self.red_phase = True
        try:
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

                if (last_updated > database_model.settings['black_alert'] and count <= BOARD_SIZE):  # Only display if board is not full
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

        except:
            print("No support tickets")


if __name__ == 'ticket_board_view':
    ticket_board_view = TicketBoardView()
    # Add the ticket board widget/layout to the main window widget
    main_view.window.addWidget(ticket_board_view)
