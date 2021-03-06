

from PyQt5.QtCore import QObject, QTimer, QSettings
import threading
from jira import JIRA
from datetime import datetime

from ticket_history_model import TicketHistoryModel, Base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class JiraService(QObject):
    def __init__(self):
        super(JiraService, self).__init__()
        engine = create_engine('sqlite:///jira_helper.db')
        Base.metadata.bind = engine
        self.DBSession = sessionmaker(bind=engine)

        # Grab settings from file
        self.settings = QSettings('Open-Source', 'Jira-Helper')

        self.support_tickets = list()
        self.customer_tickets = list()
        self.in_progress_tickets = list()
        self.dev_tickets = list()
        self.design_tickets = list()
        self.test_tickets = list()
        self.build_tickets = list()

        # Timer to fetch tickets from JIRA server
        fetch_tickets_timer = QTimer(self)
        fetch_tickets_timer.timeout.connect(self.fetch_tickets_timeout)
        fetch_tickets_timer.start(5000)  # Fetch tickets every 5 seconds

        # Timer to save ticket stats to db
        save_ticket_history_timer = QTimer(self)
        save_ticket_history_timer.timeout.connect(self.save_ticket_history_timeout)
        save_ticket_history_timer.start(5 * 60 * 1000)  # Save every 5 mins

    def fetch_tickets_timeout(self):
        self.fetch_tickets_thread = threading.Thread(target=self.fetch_tickets)  # Load thread into obj
        self.fetch_tickets_thread.start()  # Start thread

    def save_ticket_history_timeout(self):
        self.save_ticket_history_thread = threading.Thread(target=self.save_ticket_history)  # Load thread into obj
        self.save_ticket_history_thread.start()  # Start thread

    def fetch_tickets(self):  # Thread for grabbing all tickets used by program
        # Catch invalid credentials
        try:
            # Create a JIRA object and populate ticket arrays
            self.jira = JIRA(basic_auth=(
                str(self.settings.value('username')),
                str(self.settings.value('api_key'))),
                options={'server': self.settings.value('jira_url')}
            )
            self.support_tickets = self.jira.search_issues('status=' + self.settings.value('support_status').replace(" ", "\ "), maxResults=200)
            self.customer_tickets = self.jira.search_issues('status=' + self.settings.value('customer_status').replace(" ", "\ "), maxResults=200)
            self.in_progress_tickets = self.jira.search_issues('status=' + self.settings.value('in_progress_status').replace(" ", "\ "), maxResults=200)
            self.dev_tickets = self.jira.search_issues('status=' + self.settings.value('dev_status').replace(" ", "\ ") + ' OR status=new', maxResults=200)
            self.design_tickets = self.jira.search_issues('status=' + self.settings.value('design_status').replace(" ", "\ "), maxResults=200)
            self.test_tickets = self.jira.search_issues('status=' + self.settings.value('test_status').replace(" ", "\ "), maxResults=200)

            # Empty the list to prevent double ups
            self.build_tickets = []
            # Create a list of build tickets
            for ticket in (self.dev_tickets + self.design_tickets + self.test_tickets):
                # Check if suffix of ticket number is 1, indicating a build ticket
                if int(ticket.raw['key'][ticket.raw['key'].find('-') + 1:len(ticket.raw['key'])]) == 1:
                    self.build_tickets.append(ticket)

        except:
            print("Invalid credentials")

    def save_ticket_history(self):
        date = datetime.today()  # Get current date in UTC to save to db
        session = self.DBSession()
        history = TicketHistoryModel(
            stamp=date,
            support=len(self.support_tickets),
            customer=len(self.customer_tickets),
            in_progress=len(self.in_progress_tickets),
            dev=len(self.dev_tickets),
            design=len(self.design_tickets),
            test=len(self.test_tickets)
        )
        session.add(history)
        session.commit()
        # Close the session for this thread OR FACE ERRORS!
        session.close()


if __name__ == 'jira_service':
    print('Instantiating ' + __name__)
    jira_service = JiraService()
