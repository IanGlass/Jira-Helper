PROJECT_NAME = "wherewolf support"
BOARD_TICKET_STATUS = "waiting for support"
QUEUE_TICKET_STATUS = "waiting for customer"
SAMPLE_TICKET = "WS-217"




#This module creates a Qt table to display overdue issues as either older than:
#2 days - displayed in black text
#5 days - displayed as flashing red text
#10 days - displayed as solid red text
#Up to 200 tickets are fetched using a thread (to prevent locking updating of the Qt table)
#This project follows the PEP-8 style guides

PROJECT_NAME = PROJECT_NAME.replace(" ", "\ ") #Format project name to UNIX compatible directory path used by JIRA API
BOARD_TICKET_STATUS = BOARD_TICKET_STATUS.replace(" ", "\ ") #Format ticket status to UNIX compatible directory path used by JIRA API
QUEUE_TICKET_STATUS = QUEUE_TICKET_STATUS.replace(" ", "\ ") #Format ticket status to UNIX compatible directory path used by JIRA API

from jira import JIRA
from datetime import datetime
from dateutil import parser #Used to truncate and convert string to datetime Obj
import netrc
from time import sleep

import threading

#GUI
import sys
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui

from PyQt5.QtCore import QDate, QTime, Qt #Used to covert and import datetime

fontFile = "arial.ttf" #font used to display text
FONT_SIZE = 12

BLACK_ALERT_DELAY = 60*60*24*2 #(seconds) displays ticket with 'Last Updated' older than this in black
RED_ALERT_DELAY = 60*60*24*7 #(seconds) tickets with 'Last Updated' older than this are flashed red
MELT_DOWN_DELAY = 60*60*24*14 #(seconds) tickets with 'Last Updated' older than this are solid red
BOARD_SIZE = 25

#grab credentials from ~/.netrc file
secrets = netrc.netrc()
username,account,password = secrets.authenticators('Jira-Credentials')  

class MyMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setGeometry(300, 300, 1000, 1000)

        win = QtWidgets.QWidget()
        self.setCentralWidget(win)
        grid = QtWidgets.QGridLayout()
        win.setLayout(grid)

        self.col_key = list()
        self.col_assigned = list()
        self.col_summary = list()
        self.col_last_updated = list()

        self.fnt = QtGui.QFont("Times", FONT_SIZE)
        for i in range(0,BOARD_SIZE+2):
            self.col_key.append(QtWidgets.QLabel())
            self.col_key[i].setFont(self.fnt)
            grid.addWidget(self.col_key[i], i, 0)

            self.col_summary.append(QtWidgets.QLabel())
            self.col_summary[i].setFont(self.fnt)
            grid.addWidget(self.col_summary[i], i, 1)

            self.col_assigned.append(QtWidgets.QLabel())
            self.col_assigned[i].setFont(self.fnt)
            grid.addWidget(self.col_assigned[i], i, 2)

            self.col_last_updated.append(QtWidgets.QLabel())
            self.col_last_updated[i].setFont(self.fnt)
            grid.addWidget(self.col_last_updated[i], i, 3)

        #Fill column titles
        self.fnt.setBold(True)
        self.col_key[1].setFont(self.fnt)
        self.col_key[1].setText("Ticket Number")
        self.col_summary[1].setFont(self.fnt)
        self.col_summary[1].setText("Summary")
        self.col_assigned[1].setFont(self.fnt)
        self.col_assigned[1].setText("Assignee")
        self.col_last_updated[1].setFont(self.fnt)
        self.col_last_updated[1].setText("Last Updated")
        self.fnt.setBold(False) #Reset font

        self.col_assigned[0].setStyleSheet('font-size: 40px')
        self.col_last_updated[0].setStyleSheet('font-size: 40px')

        self.red_phase = False #used to flash rows if red alert

        self.start_timers()

    def fetch_board_tickets(self): #Thread method to fetch a list of tickets from jira
        self.board_tickets = jira.search_issues('project=' + PROJECT_NAME + ' AND status=' + BOARD_TICKET_STATUS, maxResults=200)

    def check_queue(self):
        #Get the transition id needed to move the ticket to the waiting on support queue
        try:
            transitions = jira.transitions(SAMPLE_TICKET)
            for key in transitions:
                if (key.get('name') == 'Respond to support'):
                    transition_key = key.get('id')
            
            self.queue_tickets = jira.search_issues('project=' + PROJECT_NAME + ' AND status=' + QUEUE_TICKET_STATUS, maxResults=10)
            for ticket in self.queue_tickets:
                date = datetime.now() #get current date
                ticket_date = parser.parse(ticket.fields.updated[0:23]) #truncate and convert string to datetime obj
                last_updated = (date - ticket_date).total_seconds()
                if (ticket.key == 'WS-886'):
                    jira.transition_issue(ticket, transition_key)
                    if (ticket.fields.summary[0:23] != '(follow up with client)'): #prevent tacking more than one on to summary
                        ticket.update(summary='(follow up with client) ' + ticket.fields.summary)
        except: #Wildcard exception, likely cause at this point is invalid sample ticket number
            print("Invalid ticket number provided")

    def start_timers(self):

        #Timer used to fecth issues from jira
        self.fetch_ticket_timer = QtCore.QTimer(self)
        self.fetch_ticket_timer.timeout.connect(self.fetch_tickets_timeout)
        self.fetch_ticket_timer.start(2000)

        #Pre-populate ticket list so board does not stay empty until fetch_ticket_timer timeout period
        self.board_tickets = jira.search_issues('project=' + PROJECT_NAME + ' AND status=' + BOARD_TICKET_STATUS, maxResults=200)

        #Timer used to update board
        self.update_board_timer = QtCore.QTimer(self)
        self.update_board_timer.timeout.connect(self.update_board_timeout)
        self.update_board_timer.start(1000)

        #Timer used to fetch the waiting on customer queue and throw back into
        self.check_queue_timer = QtCore.QTimer(self)
        self.check_queue_timer.timeout.connect(self.check_queue_timeout)
        self.check_queue_timer.start(10000) #check every 10 seconds

    def fetch_tickets_timeout(self): #Thread is re-created every call to this function

        self.fetch_tickets_thread = threading.Thread(target=self.fetch_board_tickets) #Load thread into obj
        self.fetch_tickets_thread.start() #Start thread

    def check_queue_timeout(self): 
        if (SAMPLE_TICKET): #if sample ticket is supplie then we can proceed
            self.check_queue_thread = threading.Thread(target=self.check_queue) #Load thread into obj
            self.check_queue_thread.start() #Start thread

    def update_board_timeout(self):

        self.clear_widgets()
        self.update_board()

    def clear_widgets(self): #Ensures table is cleared if less than BOARD_SIZE issues are overdue
        for i in range(2,BOARD_SIZE+2): #Don't clear first or second row, which contain time and col headings
            self.col_key[i].setText("")
            self.col_summary[i].setText("")
            self.col_assigned[i].setText("")
            self.col_last_updated[i].setText("")

    def update_board(self):
        count = 2 #Prevent write over column titles and datetime
        
        date = QDate.currentDate()
        time = QTime.currentTime()
        self.col_assigned[0].setText(date.toString(Qt.DefaultLocaleLongDate))
        self.col_last_updated[0].setText(time.toString(Qt.DefaultLocaleLongDate))
        if (self.red_phase): #pulse red_phase for flashing redlert tickets
            self.red_phase = False
        else:
            self.red_phase = True
        for ticket in self.board_tickets:
            date = datetime.now() #get current date
            ticket_date = parser.parse(ticket.fields.updated[0:23]) #truncate and convert string to datetime obj
            last_updated = (date - ticket_date).total_seconds()
            if (last_updated > BLACK_ALERT_DELAY and count <= BOARD_SIZE+1): #Only display if board is not full
                if (last_updated > MELT_DOWN_DELAY): #Things are serious!
                    self.col_key[count].setStyleSheet('color: red')
                    self.col_summary[count].setStyleSheet('color: red') 
                    self.col_assigned[count].setStyleSheet('color: red')
                    self.col_last_updated[count].setStyleSheet('color: red')
                elif (last_updated > RED_ALERT_DELAY): #Things are not so Ok
                    if (self.red_phase):
                        self.col_key[count].setStyleSheet('color: red') 
                        self.col_summary[count].setStyleSheet('color: red') 
                        self.col_assigned[count].setStyleSheet('color: red') 
                        self.col_last_updated[count].setStyleSheet('color: red') 
                    else:
                        self.col_key[count].setStyleSheet('color: black') 
                        self.col_summary[count].setStyleSheet('color: black')
                        self.col_assigned[count].setStyleSheet('color: black') 
                        self.col_last_updated[count].setStyleSheet('color: black')
                else : #Things are still Okish
                    self.col_key[count].setStyleSheet('color: black') 
                    self.col_summary[count].setStyleSheet('color: black') 
                    self.col_assigned[count].setStyleSheet('color: black') 
                    self.col_last_updated[count].setStyleSheet('color: black') 
                self.col_key[count].setText(str(ticket.key))
                self.col_summary[count].setText(str(ticket.fields.summary))
                self.col_assigned[count].setText(str(ticket.fields.assignee))
                self.col_last_updated[count].setText(str(ticket.fields.updated))
                count = count + 1
                

if __name__ == '__main__':
    #Create a JIRA object using netrc credentials
    try:
        jira = JIRA(basic_auth=(username,password), options={'server': account})
        app = QtWidgets.QApplication(sys.argv)
        main_window = MyMainWindow()
        main_window.show()
        sys.exit(app.exec_())
    except: #Likely issue is invalid credentials
        print("Invalid credentials")