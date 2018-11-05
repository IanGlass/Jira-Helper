SUPPORT_TICKET_STATUS = "waiting for support"
CUSTOMER_TICKET_STATUS = "waiting for customer"
IN_PROGRESS_TICKET_STATUS = "in progress"
DEV_TICKET_STATUS = "dev"
DESIGN_TICKET_STATUS = "design"
TEST_TICKET_STATUS = "test"
SAMPLE_TICKET = "100"


#This module creates a Qt table to display overdue issues as either older than:
#2 days - displayed in black text
#5 days - displayed as flashing red text
#10 days - displayed as solid red text
#Up to 200 tickets are fetched using a thread (to prevent locking updating of the Qt table)
#This project follows the PEP-8 style guides

SUPPORT_TICKET_STATUS = SUPPORT_TICKET_STATUS.replace(" ", "\ ") #Format ticket status to UNIX compatible directory path used by JIRA API
CUSTOMER_TICKET_STATUS = CUSTOMER_TICKET_STATUS.replace(" ", "\ ") #Format ticket status to UNIX compatible directory path used by JIRA API
IN_PROGRESS_TICKET_STATUS = IN_PROGRESS_TICKET_STATUS.replace(" ", "\ ") #Format ticket status to UNIX compatible directory path used by JIRA API
DEV_TICKET_STATUS = DEV_TICKET_STATUS.replace(" ", "\ ") #Format ticket status to UNIX compatible directory path used by JIRA API
DESIGN_TICKET_STATUS = DESIGN_TICKET_STATUS.replace(" ", "\ ") #Format ticket status to UNIX compatible directory path used by JIRA API
TEST_TICKET_STATUS = TEST_TICKET_STATUS.replace(" ", "\ ") #Format ticket status to UNIX compatible directory path used by JIRA API

from jira import JIRA
from datetime import datetime
from dateutil import parser #Used to truncate and convert string to datetime Obj
from dateutil import tz #used to convert local-UTC
import netrc
from time import sleep

import threading

#GUI
import sys
from PyQt5 import QtCore, QtWidgets, QtGui

from PyQt5.QtCore import QDate, QTime, Qt #Used to covert and import datetime

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

FONT = "Times" #font used to display text
FONT_SIZE = 12

#TODO make these variables defined from bash
BLACK_ALERT_DELAY = 60*60*24*2 #(seconds) displays ticket with 'Last Updated' older than this in black
RED_ALERT_DELAY = 60*60*24*7 #(seconds) tickets with 'Last Updated' older than this are flashed red
MELT_DOWN_DELAY = 60*60*24*14 #(seconds) tickets with 'Last Updated' older than this are solid red
QUEUE_OVERDUE = 60*60*24*7 #(seconds) waiting on customer tickets older than this are thrown back into waiting on support with
#(follow up with client) text added to summary
TRANSITION_PERIOD = 5000 #(miliseconds) time between page swap

BOARD_SIZE = 25

DISPLAY_PERIOD = '14 days' #this is passed directly into psql query for analytics board display

#grab credentials from ~/.netrc file
secrets = netrc.netrc()
username,account,password = secrets.authenticators('Jira-Credentials')

FROM_ZONE = tz.tzutc()
TO_ZONE = tz.tzlocal()


#TODO
#Place each class in own module
#Save in local db
#use flags to check if waiting on customer support cleanout is required, place cleanup in own class and only execute if flag is set in bash

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.window = QtWidgets.QStackedWidget() #create the main widget for the page
        self.setCentralWidget(self.window)

        try: #Try to connect to existing db for ticket analytics
            self.con = psycopg2.connect(dbname='ticketdb',
            user='postgres', host='',
            password='') #Connect to the db
            self.con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cur = self.con.cursor()

        except: #If this reached then db does not exist, need to create it
            self.con = psycopg2.connect(dbname='postgres',
            user='postgres', host='',
            password='') #Connect to default postgres db first
            self.con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            self.cur = self.con.cursor()
            self.cur.execute('CREATE DATABASE ticketdb')

            #Connect to new db
            self.con = psycopg2.connect(dbname='ticketdb',
            user='postgres', host='',
            password='')
            self.con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cur = self.con.cursor()
            #Populate db with a table and cols
            self.cur.execute('''CREATE TABLE IF NOT EXISTS ticket_stats(
            stamp timestamptz PRIMARY KEY, 
            support int NOT NULL, 
            in_progress int NOT NULL, 
            customer int NOT NULL, 
            dev int NOT NULL, 
            design int NOT NULL, 
            test int NOT NULL)''')

        #Timer used to fetch the waiting on customer queue and throw back into
        self.check_customer_tickets_timer = QtCore.QTimer(self)
        self.check_customer_tickets_timer.timeout.connect(self.check_customer_tickets_timeout)
        self.check_customer_tickets_timer.start(1000) #check every 10 seconds

        #Timer used to transition the page
        self.transition_page_timer = QtCore.QTimer(self)
        self.transition_page_timer.timeout.connect(self.transition_page_timeout)
        self.transition_page_timer.start(TRANSITION_PERIOD) #transition every 10 seconds

        #Timer fetch tickets from JIRA server
        self.fetch_tickets_timer = QtCore.QTimer(self)
        self.fetch_tickets_timer.timeout.connect(self.fetch_tickets_timeout)
        self.fetch_tickets_timer.start(2000) #fetch tickets every 2 seconds

        #Timer to save ticket stats to db
        self.save_to_db_timer = QtCore.QTimer(self)
        self.save_to_db_timer.timeout.connect(self.save_to_db_timeout)
        self.save_to_db_timer.start(10*60*1000) #save every half-hour

        #Pre-populate ticket list so boards do not stay empty until fetch ticket timeout
        self.support_tickets = jira.search_issues('status=' + SUPPORT_TICKET_STATUS, maxResults=200)
        self.customer_tickets = jira.search_issues('status=' + CUSTOMER_TICKET_STATUS, maxResults=200)
        self.in_progress_tickets = jira.search_issues('status=' + IN_PROGRESS_TICKET_STATUS, maxResults=200)
        self.dev_tickets = jira.search_issues('status=' + DEV_TICKET_STATUS + ' OR status=new', maxResults=200)
        self.design_tickets = jira.search_issues('status=' + DESIGN_TICKET_STATUS, maxResults=200)
        self.test_tickets = jira.search_issues('status=' + TEST_TICKET_STATUS, maxResults=200)

        #Fetch ticket history from db, so analytics doesn't have to wait for call to db, only get tickets younger than DISPLAY_PERIOD
        self.cur.execute('select stamp, support, in_progress, customer from ticket_stats where stamp > now() - %(period)s::interval', {"period": DISPLAY_PERIOD})
        self.ticket_history = self.cur.fetchall()

        self.date_history = list()
        self.support_history = list()
        self.in_progress_history = list()
        self.customer_history = list()

        #TODO this is horrible
        for i in range(0,len(self.ticket_history)):
            self.date_history.append(self.ticket_history[i][0])
            self.support_history.append(self.ticket_history[i][1])
            self.in_progress_history.append(self.ticket_history[i][2])
            self.customer_history.append(self.ticket_history[i][3])

    def transition_page_timeout(self):
        index_Id = self.window.currentIndex()
        if index_Id < self.window.count() - 1:
            self.window.setCurrentIndex(index_Id + 1)
        else:
            self.window.setCurrentIndex(0)

    def check_customer_tickets_timeout(self): 
        if (SAMPLE_TICKET): #if sample ticket is supplied then we can proceed
            self.check_customer_tickets_thread = threading.Thread(target=self.check_customer_tickets) #Load thread into obj
            self.check_customer_tickets_thread.start() #Start thread

    def fetch_tickets_timeout(self): 
        self.fetch_tickets_thread = threading.Thread(target=self.fetch_tickets) #Load thread into obj
        self.fetch_tickets_thread.start() #Start thread

    def save_to_db_timeout(self):
        self.save_to_db_thread = threading.Thread(target=self.save_to_db) #Load thread into obj
        self.save_to_db_thread.start() #Start thread        

    def check_customer_tickets(self):
        #Try to get a transition key if there are any tickets in waiting for customer
        try:
            #Get list of transitions for a ticket in the waiting on customer queue
            transitions = jira.transitions(self.customer_tickets[0].key)
            #find the transition key needed to move from waiting for customer to waiting for support
            for key in transitions:
                if (key.get('name') == 'Respond to support'):
                    transition_key = key.get('id')
    
            for customer_ticket in self.customer_tickets:
                date = datetime.now() #get current date
                customer_ticket_date = parser.parse(customer_ticket.fields.updated[0:23]) #truncate and convert string to datetime obj
                last_updated = (date - customer_ticket_date).total_seconds()
                if (last_updated > QUEUE_OVERDUE): #If tickets are overdue
                    jira.transition_issue(customer_ticket, transition_key) #Change ticket status
                    if (customer_ticket.fields.summary[0:30] != '(please follow up with client)'): #prevent tacking more than one on to summary
                        customer_ticket.update(summary='(please follow up with client) ' + customer_ticket.fields.summary)

        except:
            print("No customer tickets to manage")

    def fetch_tickets(self): #Thread for grabbing all tickets used by program
        self.support_tickets = jira.search_issues('status=' + SUPPORT_TICKET_STATUS, maxResults=200)
        self.customer_tickets = jira.search_issues('status=' + CUSTOMER_TICKET_STATUS, maxResults=200)
        self.in_progress_tickets = jira.search_issues('status=' + IN_PROGRESS_TICKET_STATUS, maxResults=200)
        self.dev_tickets = jira.search_issues('status=' + DEV_TICKET_STATUS + ' OR status=new', maxResults=200)
        self.design_tickets = jira.search_issues('status=' + DESIGN_TICKET_STATUS, maxResults=200)
        self.test_tickets = jira.search_issues('status=' + TEST_TICKET_STATUS, maxResults=200)

    def save_to_db(self):

        self.date = datetime.utcnow() #get current date in UTC to save to db

        self.cur.execute('insert into ticket_stats (stamp,support,customer,in_progress,dev,design,test) values (%s,%s,%s,%s,%s,%s,%s)', (self.date,len(self.support_tickets),len(self.customer_tickets),len(self.in_progress_tickets),len(self.dev_tickets),len(self.design_tickets),len(self.test_tickets)))

        #Fetch ticket history from db, only get tickets younger than DISPLAY_PERIOD
        self.cur.execute('select stamp, support, in_progress, customer from ticket_stats where stamp > now() - %(period)s::interval', {"period": DISPLAY_PERIOD})
        self.ticket_history = self.cur.fetchall()

        #Empty lists so we don't get double ups
        self.date_history.clear()
        self.support_history.clear()
        self.in_progress_history.clear()
        self.customer_history.clear()

        #TODO this is horrible
        for i in range(0,len(self.ticket_history)):
            self.date_history.append(self.ticket_history[i][0].astimezone(TO_ZONE))
            self.support_history.append(self.ticket_history[i][1])
            self.in_progress_history.append(self.ticket_history[i][2])
            self.customer_history.append(self.ticket_history[i][3])
        

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
        for i in range(0,BOARD_SIZE+2): #Build the ticket board
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
        for support_ticket in main_window.support_tickets:
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

        self.figure = Figure(figsize=(7, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        analytics_board_layout.addWidget(self.canvas,3,1,-1,3)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel('date')
        self.ax.set_ylabel('# of tickets')
        self.figure.patch.set_facecolor([240/255,240/255,240/255,1])

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

        #Timer used to update the analytics page
        self.update_analytics_timer = QtCore.QTimer(self)
        self.update_analytics_timer.timeout.connect(self.update_analytics_timeout)
        self.update_analytics_timer.start(1000) #update every second

    def update_analytics_timeout(self): 
        self.update_analytics_thread = threading.Thread(target=self.update_analytics) #Load thread into obj
        self.update_analytics_thread.start() #Start thread

    def update_analytics(self):
        self.col_support[1].setText(str(len(main_window.support_tickets)))
        self.col_customer[1].setText(str(len(main_window.customer_tickets)))
        self.col_in_progress[1].setText(str(len(main_window.in_progress_tickets)))
        self.col_dev[1].setText(str(len(main_window.dev_tickets)))
        self.col_design[1].setText(str(len(main_window.design_tickets)))
        self.col_test[1].setText(str(len(main_window.test_tickets)))

        self.ax.clear()
        self.ax.plot(main_window.date_history, main_window.support_history, 'r-', label = 'waiting on support')
        self.ax.plot(main_window.date_history, main_window.customer_history, 'b-', label = 'waiting on customer')
        self.ax.plot(main_window.date_history, main_window.in_progress_history, 'g-', label = 'in progress')
        self.ax.legend(loc='best')
        self.canvas.draw()

if __name__ == '__main__':


    #Create a JIRA object using netrc credentials
    jira = JIRA(basic_auth=(username,password), options={'server': account})
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    ticket_board = TicketBoard()
    analytics_board = AnalyticsBoard()
    main_window.showMaximized()
    main_window.setWindowTitle('The coolest program in the world')
    sys.exit(app.exec_())