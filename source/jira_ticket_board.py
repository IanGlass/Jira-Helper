PROJECT_NAME = "wherewolf support"
SUPPORT_TICKET_STATUS = "waiting for support"
CUSTOMER_TICKET_STATUS = "waiting for customer"
IN_PROGRESS_TICKET_STATUS = "in progress"
DEV_TICKET_STATUS = "dev"
DESIGN_TICKET_STATUS = "design"
TEST_TICKET_STATUS = "test"
SAMPLE_TICKET = "WS-462"




#This module creates a Qt table to display overdue issues as either older than:
#2 days - displayed in black text
#5 days - displayed as flashing red text
#10 days - displayed as solid red text
#Up to 200 tickets are fetched using a thread (to prevent locking updating of the Qt table)
#This project follows the PEP-8 style guides

PROJECT_NAME = PROJECT_NAME.replace(" ", "\ ") #Format project name to UNIX compatible directory path used by JIRA API
SUPPORT_TICKET_STATUS = SUPPORT_TICKET_STATUS.replace(" ", "\ ") #Format ticket status to UNIX compatible directory path used by JIRA API
CUSTOMER_TICKET_STATUS = CUSTOMER_TICKET_STATUS.replace(" ", "\ ") #Format ticket status to UNIX compatible directory path used by JIRA API
IN_PROGRESS_TICKET_STATUS = IN_PROGRESS_TICKET_STATUS.replace(" ", "\ ") #Format ticket status to UNIX compatible directory path used by JIRA API
DEV_TICKET_STATUS = DEV_TICKET_STATUS.replace(" ", "\ ") #Format ticket status to UNIX compatible directory path used by JIRA API
DESIGN_TICKET_STATUS = DESIGN_TICKET_STATUS.replace(" ", "\ ") #Format ticket status to UNIX compatible directory path used by JIRA API
TEST_TICKET_STATUS = TEST_TICKET_STATUS.replace(" ", "\ ") #Format ticket status to UNIX compatible directory path used by JIRA API


from jira import JIRA
from datetime import datetime
from dateutil import parser #Used to truncate and convert string to datetime Obj
import netrc
from time import sleep

import threading

#GUI
import sys
from PyQt5 import QtCore, QtWidgets, QtGui

from PyQt5.QtCore import QDate, QTime, Qt #Used to covert and import datetime

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

FONT = "Times" #font used to display text
FONT_SIZE = 12

BLACK_ALERT_DELAY = 60*60*24*2 #(seconds) displays ticket with 'Last Updated' older than this in black
RED_ALERT_DELAY = 60*60*24*7 #(seconds) tickets with 'Last Updated' older than this are flashed red
MELT_DOWN_DELAY = 60*60*24*14 #(seconds) tickets with 'Last Updated' older than this are solid red
QUEUE_OVERDUE = 60*60*24*7 #(seconds) queue tickets older than this are thrown back into waiting on support with
#(follow up with client) text added to summary
BOARD_SIZE = 25
TRANSITION_PERIOD = 5000 #(miliseconds) time between page swap

#grab credentials from ~/.netrc file
secrets = netrc.netrc()
username,account,password = secrets.authenticators('Jira-Credentials')  

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.window = QtWidgets.QStackedWidget() #create the main widget for the page
        self.setCentralWidget(self.window)

        #Timer used to fetch the waiting on customer queue and throw back into
        self.check_customer_tickets_timer = QtCore.QTimer(self)
        self.check_customer_tickets_timer.timeout.connect(self.check_customer_tickets_timeout)
        self.check_customer_tickets_timer.start(1000) #check every 10 seconds

        #Timer used to transition the page
        self.transition_page_timer = QtCore.QTimer(self)
        self.transition_page_timer.timeout.connect(self.transition_page_timeout)
        self.transition_page_timer.start(TRANSITION_PERIOD) #transition every 10 seconds

        #Timer used to transition the page
        self.fetch_tickets_timer = QtCore.QTimer(self)
        self.fetch_tickets_timer.timeout.connect(self.fetch_tickets_timeout)
        self.fetch_tickets_timer.start(5000) #transition every 10 seconds

        #Timer used to transition the page
        self.save_to_db_timer = QtCore.QTimer(self)
        self.save_to_db_timer.timeout.connect(self.save_to_db_timeout)
        self.save_to_db_timer.start(60*60*1000) #save every hour

        #Pre-populate support ticket list so board does not stay empty until fetch ticket timeout
        self.support_tickets = jira.search_issues('project=' + PROJECT_NAME + ' AND status=' + SUPPORT_TICKET_STATUS, maxResults=200)


    def transition_page_timeout(self):
        index_Id = self.window.currentIndex()
        if index_Id < self.window.count() - 1:
            self.window.setCurrentIndex(index_Id + 1)
        else:
            self.window.setCurrentIndex(0)

    def check_customer_tickets_timeout(self): 
        if (SAMPLE_TICKET): #if sample ticket is supplie then we can proceed
            self.check_customer_tickets_thread = threading.Thread(target=self.check_customer_tickets) #Load thread into obj
            self.check_customer_tickets_thread.start() #Start thread

    def fetch_tickets_timeout(self): 
        self.fetch_tickets_thread = threading.Thread(target=self.fetch_tickets) #Load thread into obj
        self.fetch_tickets_thread.start() #Start thread

    def save_to_db_timeout(self):
        self.save_to_db_thread = threading.Thread(target=self.save_to_db) #Load thread into obj
        self.save_to_db_thread.start() #Start thread        

    def check_customer_tickets(self):
        #Get the transition id needed to move the ticket to the waiting on support queue
        transition_key = '781'
        #transitions = jira.transitions(SAMPLE_TICKET)
        #for key in transitions:
            #if (key.get('name') == 'Respond to support'):
                #print(key.get('id'))
                #transition_key = key.get('id')
        
        queue_tickets = jira.search_issues('project=' + PROJECT_NAME + ' AND status=' + CUSTOMER_TICKET_STATUS, maxResults=200)
        for queue_ticket in queue_tickets:
            date = datetime.now() #get current date
            queue_ticket_date = parser.parse(queue_ticket.fields.updated[0:23]) #truncate and convert string to datetime obj
            last_updated = (date - queue_ticket_date).total_seconds()
            if (last_updated > QUEUE_OVERDUE): #If tickets are overdue
                jira.transition_issue(queue_ticket, transition_key) #Change ticket status
                if (queue_ticket.fields.summary[0:30] != '(please follow up with client)'): #prevent tacking more than one on to summary
                    queue_ticket.update(summary='(please follow up with client) ' + queue_ticket.fields.summary)

    def fetch_tickets(self): #Thread for grabbing all tickets used by program
        self.support_tickets = jira.search_issues('project=' + PROJECT_NAME + ' AND status=' + SUPPORT_TICKET_STATUS, maxResults=200)
        self.customer_tickets = jira.search_issues('project=' + PROJECT_NAME + ' AND status=' + CUSTOMER_TICKET_STATUS, maxResults=200)
        self.in_progress_tickets = jira.search_issues('status=' + IN_PROGRESS_TICKET_STATUS, maxResults=200)
        self.dev_tickets = jira.search_issues('status=' + DEV_TICKET_STATUS, maxResults=200)
        self.design_tickets = jira.search_issues('status=' + DESIGN_TICKET_STATUS, maxResults=200)
        self.test_tickets = jira.search_issues('status=' + TEST_TICKET_STATUS, maxResults=200)

    def save_to_db(self):

        self.date = datetime.now() #get current date

        cur.execute('insert into ticket_stats (date,waiting_on_support,waiting_on_customer,in_progress,dev,design,test) values (%s,%s,%s,%s,%s,%s,%s)', (self.date,len(self.support_tickets),len(self.customer_tickets),len(self.in_progress_tickets),len(self.dev_tickets),len(self.design_tickets),len(self.test_tickets)))

class TicketBoard(QtWidgets.QMainWindow):
    
    def __init__(self):
        super().__init__()
        ticket_board_widget = QtWidgets.QWidget() #create the widget to contain the ticket board layout
        ticket_board_layout = QtWidgets.QGridLayout() #layout for ticket board
        ticket_board_widget.setLayout(ticket_board_layout)
        main_window.window.addWidget(ticket_board_widget) #add the ticket board widget/layout to the main window widget

        self.col_key = list()
        self.col_assigned = list()
        self.col_summary = list()
        self.col_last_updated = list()

        self.fnt = QtGui.QFont(FONT, FONT_SIZE)
        for i in range(0,BOARD_SIZE+2):
            self.col_key.append(QtWidgets.QLabel())
            self.col_key[i].setFont(self.fnt)
            ticket_board_layout.addWidget(self.col_key[i], i, 0)

            self.col_summary.append(QtWidgets.QLabel())
            self.col_summary[i].setFont(self.fnt)
            ticket_board_layout.addWidget(self.col_summary[i], i, 1)

            self.col_assigned.append(QtWidgets.QLabel())
            self.col_assigned[i].setFont(self.fnt)
            ticket_board_layout.addWidget(self.col_assigned[i], i, 2)

            self.col_last_updated.append(QtWidgets.QLabel())
            self.col_last_updated[i].setFont(self.fnt)
            ticket_board_layout.addWidget(self.col_last_updated[i], i, 3)
        
        self.col_key[0].setStyleSheet('background-image: url(Wherewolf.png); background-repeat: no-repeat ')

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

        #Timer used to update board
        self.update_board_timer = QtCore.QTimer(self)
        self.update_board_timer.timeout.connect(self.update_board_timeout)
        self.update_board_timer.start(1000)

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
        for support_ticket in MainWindow.support_tickets:
            date = datetime.now() #get current date
            ticket_date = parser.parse(support_ticket.fields.updated[0:23]) #truncate and convert string to datetime obj
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
                self.col_key[count].setText(str(support_ticket.key))
                self.col_summary[count].setText(str(support_ticket.fields.summary))
                self.col_assigned[count].setText(str(support_ticket.fields.assignee))
                self.col_last_updated[count].setText(str(support_ticket.fields.updated))
                count = count + 1

class AnalyticsBoard(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        analytics_board_widget = QtWidgets.QWidget() #create the widget to contain the analytics board layout
        analytics_board_layout = QtWidgets.QGridLayout() #layout for analytics board
        analytics_board_widget.setLayout(analytics_board_layout)
        main_window.window.addWidget(analytics_board_widget) #add the analytics board widget/layout to the main window widget

        self.col_support = list()
        self.col_customer = list()
        self.col_in_progress = list()
        self.col_dev = list()
        self.col_design = list()
        self.col_test = list()

        self.fnt = QtGui.QFont(FONT, FONT_SIZE)
        for i in range(0,10):
            self.col_support.append(QtWidgets.QLabel())
            self.col_support[i].setFont(self.fnt)
            analytics_board_layout.addWidget(self.col_support[i], i, 0)

            self.col_customer.append(QtWidgets.QLabel())
            self.col_customer[i].setFont(self.fnt)
            analytics_board_layout.addWidget(self.col_customer[i], i, 1)

            self.col_in_progress.append(QtWidgets.QLabel())
            self.col_in_progress[i].setFont(self.fnt)
            analytics_board_layout.addWidget(self.col_in_progress[i], i, 2)

            self.col_dev.append(QtWidgets.QLabel())
            self.col_dev[i].setFont(self.fnt)
            analytics_board_layout.addWidget(self.col_dev[i], i, 3)

            self.col_design.append(QtWidgets.QLabel())
            self.col_design[i].setFont(self.fnt)
            analytics_board_layout.addWidget(self.col_design[i], i, 4)

            self.col_test.append(QtWidgets.QLabel())
            self.col_test[i].setFont(self.fnt)
            analytics_board_layout.addWidget(self.col_test[i], i, 5)

        #Fill column titles
        self.fnt.setBold(True)
        self.col_support[0].setFont(self.fnt)
        self.col_support[0].setText("# of support tickets")
        self.col_customer[0].setFont(self.fnt)
        self.col_customer[0].setText("# of customer tickets")
        self.col_in_progress[0].setFont(self.fnt)
        self.col_in_progress[0].setText("# of tickets in Progress")
        self.col_dev[0].setFont(self.fnt)
        self.col_dev[0].setText("# of tickest in dev")
        self.col_design[0].setFont(self.fnt)
        self.col_design[0].setText("# of tickest in design")
        self.col_test[0].setFont(self.fnt)
        self.col_test[0].setText("# of tickest in test")
        self.fnt.setBold(False) #Reset font

        self.update_analytics()

    def update_analytics(self):
        MainWindow.support_tickets = jira.search_issues('project=' + PROJECT_NAME + ' AND status=' + 'waiting\ for\ support', maxResults=200)
        MainWindow.customer_tickets = jira.search_issues('project=' + PROJECT_NAME + ' AND status=' + 'waiting\ for\ customer', maxResults=200)
        MainWindow.in_progress_tickets = jira.search_issues('project=' + PROJECT_NAME + ' AND status=' + 'in\ progress', maxResults=200)
        MainWindow.dev_tickets = jira.search_issues('status=' + 'Dev', maxResults=200)
        MainWindow.design_tickets = jira.search_issues('status=' + 'design', maxResults=200)
        MainWindow.test_tickets = jira.search_issues('status=' + 'test', maxResults=200)

        self.col_support[1].setText(str(len(MainWindow.support_tickets)))
        self.col_customer[1].setText(str(len(MainWindow.customer_tickets)))
        self.col_in_progress[1].setText(str(len(MainWindow.in_progress_tickets)))
        self.col_dev[1].setText(str(len(MainWindow.dev_tickets)))
        self.col_design[1].setText(str(len(MainWindow.design_tickets)))
        self.col_test[1].setText(str(len(MainWindow.test_tickets)))

if __name__ == '__main__':
    con = psycopg2.connect(dbname='jiradb',
    user='postgres', host='',
    password='') #Connect to the db

    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    cur = con.cursor()


    #Create a JIRA object using netrc credentials
    jira = JIRA(basic_auth=(username,password), options={'server': account})
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    ticket_board = TicketBoard()
    analytics_board = AnalyticsBoard()
    main_window.showMaximized()
    sys.exit(app.exec_())