projectName = "wherewolf support"


projectName = projectName.replace(" ", "\ ") #Format project name to UNIX compatible directory path

from jira import JIRA
from tkinter import Tk, Label, Button
from datetime import datetime
from dateutil import parser
import netrc
from time import sleep

import threading

#GUI
import sys
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui

from PyQt5.QtCore import QDate, QTime, Qt #used to covert and import datetime

fontFile = "arial.ttf" #font used to display text
fontSize = 25

#grab credentials from ~.netrc file
secrets = netrc.netrc()
username,account,password = secrets.authenticators('Jira-Credentials')  

#Create a JIRA object using netrc credentials
jira = JIRA(basic_auth=(username,password), options={'server': account})

#print('project=Wherewolf\ Support AND status=Waiting\ For\ Support')
#print("Tickets overdue") 
blackAlertDelay = 60*60*24*2 #(seconds) displays ticket with 'Last Updated' older than this
redAlertDelay = 60*60*24*5 #(seconds) tickets with 'Last Updated' older than this are displayed red
meltDownDelay = 60*60*24*10#for issue in jira.search_issues('project=Wherewolf\ Support AND status=Waiting\ For\ Support', maxResults=100):
boardSize = 25
#            date = datetime.now() #get current date
#            ticket_date = parser.parse(issue.fields.updated[0:23]) #truncate and convert string to datetime obj
#            diff = (date - ticket_date).total_seconds()
#            if diff > delayLimit:
#                print('Ticket Number:{}, Summary:{}, Assignee:{}, Updated:{}'.format(issue.key, issue.fields.summary, issue.fields.assignee, issue.fields.updated))

#now = QDateTime.currentDateTime()
#print("Local Date: ", now.toString(Qt.ISODate))
#print("UTC Date: ", now.toUTC().toString(Qt.ISODate))

class MyMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setGeometry(300, 300, 1000, 1000)

        win = QtWidgets.QWidget()
        self.setCentralWidget(win)
        grid = QtWidgets.QGridLayout()
        win.setLayout(grid)

        self.wKey = list()
        self.wAssignee = list()
        self.wSummary = list()
        self.wUpdated = list()

        self.fnt = QtGui.QFont("Times", 12)
        for i in range(0,boardSize+2):
            self.wKey.append(QtWidgets.QLabel())
            self.wKey[i].setFont(self.fnt)
            grid.addWidget(self.wKey[i], i, 0)

            self.wSummary.append(QtWidgets.QLabel())
            self.wSummary[i].setFont(self.fnt)
            grid.addWidget(self.wSummary[i], i, 1)

            self.wAssignee.append(QtWidgets.QLabel())
            self.wAssignee[i].setFont(self.fnt)
            grid.addWidget(self.wAssignee[i], i, 2)

            self.wUpdated.append(QtWidgets.QLabel())
            self.wUpdated[i].setFont(self.fnt)
            grid.addWidget(self.wUpdated[i], i, 3)

        #Fill column titles
        self.fnt.setBold(True)
        self.wKey[1].setFont(self.fnt)
        self.wKey[1].setText("Ticket Number")
        self.wSummary[1].setFont(self.fnt)
        self.wSummary[1].setText("Summary")
        self.wAssignee[1].setFont(self.fnt)
        self.wAssignee[1].setText("Assignee")
        self.wUpdated[1].setFont(self.fnt)
        self.wUpdated[1].setText("Last Updated")
        self.fnt.setBold(False) #Reset font

        self.wAssignee[0].setStyleSheet('font-size: 40px')
        self.wUpdated[0].setStyleSheet('font-size: 40px')

        self.redPhase = False #used to flash rows if red alert

        self.start_timers()

    def FetchTickets(self): #Thread method to fetch a list of tickets from jira
        self.issues = jira.search_issues('project=' + projectName + ' AND status=Waiting\ For\ Support', maxResults=200)

    def start_timers(self):

        #Timer used to fecth issues from jira
        self.FetchTicketTimer = QtCore.QTimer(self)
        self.FetchTicketTimer.timeout.connect(self.fetch_tickets_timeout)
        self.FetchTicketTimer.start(2000)

        #Pre-populate ticket list so board does not stay empty until FetchTicketTimer timeout period
        self.issues = jira.search_issues('project=' + projectName + ' AND status=Waiting\ For\ Support', maxResults=200)

        #Timer used to update board
        self.UpdateBoardTimer = QtCore.QTimer(self)
        self.UpdateBoardTimer.timeout.connect(self.update_board_timeout)
        self.UpdateBoardTimer.start(1000)

    def fetch_tickets_timeout(self): #Thread is re-created every call to this function

        self.FetchIssuesThread = threading.Thread(target=self.FetchTickets) #Load thread into obj
        self.FetchIssuesThread.start() #Start thread

    def update_board_timeout(self):

        self.ClearWidgets()
        self.UpdateBoard()

    def ClearWidgets(self): #Ensures table is cleared if less than 15 issues are out of date
        for i in range(2,boardSize+2): #Don't clear first or second row
            self.wKey[i].setText("")
            self.wSummary[i].setText("")
            self.wAssignee[i].setText("")
            self.wUpdated[i].setText("")

    def UpdateBoard(self):
        count = 2 #Prevent write over column titles and datetime

        date = QDate.currentDate()
        time = QTime.currentTime()
        self.wAssignee[0].setText(date.toString(Qt.DefaultLocaleLongDate))
        self.wUpdated[0].setText(time.toString(Qt.DefaultLocaleLongDate))
        if self.redPhase:
            self.redPhase = False
        else:
            self.redPhase = True
        for issue in self.issues:
            date = datetime.now() #get current date
            ticket_date = parser.parse(issue.fields.updated[0:23]) #truncate and convert string to datetime obj
            diff = (date - ticket_date).total_seconds()
            if (diff > blackAlertDelay and count <= boardSize+1): #Only display if board is not full
                if (diff > meltDownDelay): #Things are serious!
                    if (self.redPhase):
                        self.wKey[count].setStyleSheet('background-color: none')
                        self.wKey[count].setStyleSheet('color: red') 
                        self.wSummary[count].setStyleSheet('background-color: none')
                        self.wSummary[count].setStyleSheet('color: red') 
                        self.wAssignee[count].setStyleSheet('background-color: none')
                        self.wAssignee[count].setStyleSheet('color: red') 
                        self.wUpdated[count].setStyleSheet('background-color: none')
                        self.wUpdated[count].setStyleSheet('color: red') 
                    else:
                        self.wKey[count].setStyleSheet('background-color: none')
                        self.wKey[count].setStyleSheet('color: black') 
                        self.wSummary[count].setStyleSheet('background-color: none')
                        self.wSummary[count].setStyleSheet('color: black')
                        self.wAssignee[count].setStyleSheet('background-color: none')
                        self.wAssignee[count].setStyleSheet('color: black') 
                        self.wUpdated[count].setStyleSheet('background-color: none')
                        self.wUpdated[count].setStyleSheet('color: black')
                elif (diff > redAlertDelay):      
                    self.wKey[count].setStyleSheet('background-color: none') #Things are not so Ok
                    self.wKey[count].setStyleSheet('color: red')
                    self.wSummary[count].setStyleSheet('background-color: black')
                    self.wSummary[count].setStyleSheet('color: red') 
                    self.wAssignee[count].setStyleSheet('background-color: black')
                    self.wAssignee[count].setStyleSheet('color: red')
                    self.wUpdated[count].setStyleSheet('background-color: black')
                    self.wUpdated[count].setStyleSheet('color: red')
                else : #Things are still Okish
                    self.wKey[count].setStyleSheet('background-color: none')
                    self.wKey[count].setStyleSheet('color: black') 
                    self.wSummary[count].setStyleSheet('background-color: none')
                    self.wSummary[count].setStyleSheet('color: black') 
                    self.wAssignee[count].setStyleSheet('background-color: none')
                    self.wAssignee[count].setStyleSheet('color: black') 
                    self.wUpdated[count].setStyleSheet('background-color: none')
                    self.wUpdated[count].setStyleSheet('color: black') 
                self.wKey[count].setText(str(issue.key))
                self.wSummary[count].setText(str(issue.fields.summary))
                self.wAssignee[count].setText(str(issue.fields.assignee))
                self.wUpdated[count].setText(str(issue.fields.updated))
                count = count + 1
                

if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)
    main_window = MyMainWindow()
    main_window.show()
    sys.exit(app.exec_())