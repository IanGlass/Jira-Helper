

from PyQt5 import QtCore, QtWidgets, QtGui
import threading
from jira import JIRA
from database_model import database_model


class JiraModel(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.support_tickets = list()
        self.customer_tickets = list()
        self.in_progress_tickets = list()
        self.dev_tickets = list()
        self.design_tickets = list()
        self.test_tickets = list()
        self.build_tickets = list()

        # Timer to fetch tickets from JIRA server
        fetch_tickets_timer = QtCore.QTimer(self)
        fetch_tickets_timer.timeout.connect(self.fetch_tickets_timeout)
        fetch_tickets_timer.start(2000)  # Fetch tickets every 2 seconds

        # Timer to save ticket stats to db
        save_ticket_history_timer = QtCore.QTimer(self)
        save_ticket_history_timer.timeout.connect(self.save_ticket_history_timeout)
        save_ticket_history_timer.start(5 * 60 * 1000)  # Save every 5 mins

    def fetch_tickets_timeout(self):
        self.fetch_tickets_thread = threading.Thread(target=self.fetch_tickets)  # Load thread into obj
        self.fetch_tickets_thread.start()  # Start thread

    def save_ticket_history_timeout(self):
        self.save_ticket_history_thread = threading.Thread(target=self.save_ticket_history)  # Load thread into obj
        self.save_ticket_history_thread.start()  # Start thread

    def fetch_tickets(self):  # Thread for grabbing all tickets used by program
        try:
            # Create a JIRA object and populate ticket arrays
            self.jira = JIRA(basic_auth=(database_model.settings['username'], database_model.settings['api_key']), options={'server': database_model.settings['jira_url']})
            self.support_tickets = self.jira.search_issues('status=' + database_model.settings['support_status'].replace(" ", "\ "), maxResults=200)
            self.customer_tickets = self.jira.search_issues('status=' + database_model.settings['customer_status'].replace(" ", "\ "), maxResults=200)
            self.in_progress_tickets = self.jira.search_issues('status=' + database_model.settings['in_progress_status'].replace(" ", "\ "), maxResults=200)
            self.dev_tickets = self.jira.search_issues('status=' + database_model.settings['dev_status'].replace(" ", "\ ") + ' OR status=new', maxResults=200)
            self.design_tickets = self.jira.search_issues('status=' + database_model.settings['design_status'].replace(" ", "\ "), maxResults=200)
            self.test_tickets = self.jira.search_issues('status=' + database_model.settings['test_status'].replace(" ", "\ "), maxResults=200)

            # Empty the list to prevent double ups
            self.build_tickets = []
            # Create a list of build tickets
            for ticket in (self.dev_tickets + self.design_tickets + self.test_tickets):
                # Check if suffice of ticket number is 1, indicating a build ticket
                if int(ticket.raw['key'][ticket.raw['key'].find('-') + 1:len(ticket.raw['key'])]) == 1:
                    self.build_tickets.append(ticket)

        except:
            print("Invalid credentials")

    def save_ticket_history(self):
        database_model.save_ticket_history(len(self.support_tickets), len(self.customer_tickets), len(self.in_progress_tickets), len(self.dev_tickets), len(self.design_tickets), len(self.test_tickets))


if __name__ == 'jira_model':
    print('Instantiating jira_model')
    jira_model = JiraModel()
