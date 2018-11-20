

from jira import JIRA
from database_model import database_model

class JiraModel():
    def __init__(self):
        self.support_tickets = list()
        self.customer_tickets = list()
        self.in_progress_tickets = list()
        self.dev_tickets = list()
        self.design_tickets = list()
        self.test_tickets = list()

    def fetch_tickets(self):  # Thread for grabbing all tickets used by program
        try:
            # Create a JIRA object using netrc credentials
            self.jira = JIRA(basic_auth=(database_model.settings['username'], database_model.settings['api_key']), options={'server': database_model.settings['jira_url']})
            self.support_tickets = self.jira.search_issues('status=' + database_model.settings['support_status'].replace(" ", "\ "), maxResults=200)
            self.customer_tickets = self.jira.search_issues('status=' + database_model.settings['customer_status'].replace(" ", "\ "), maxResults=200)
            self.in_progress_tickets = self.jira.search_issues('status=' + database_model.settings['in_progress_status'].replace(" ", "\ "), maxResults=200)
            self.dev_tickets = self.jira.search_issues('status=' + database_model.settings['dev_status'].replace(" ", "\ ") + ' OR status=new', maxResults=200)
            self.design_tickets = self.jira.search_issues('status=' + database_model.settings['design_status'].replace(" ", "\ "), maxResults=200)
            self.test_tickets = self.jira.search_issues('status=' + database_model.settings['test_status'].replace(" ", "\ "), maxResults=200)
        except:
            print("Invalid credentials")

    def save_ticket_history(self):
        database_model.save_ticket_history(len(self.support_tickets), len(self.customer_tickets), len(self.in_progress_tickets), len(self.dev_tickets), len(self.design_tickets), len(self.test_tickets))

    
if __name__ == 'jira_model':
    print('Instantiating jira_model')
    jira_model = JiraModel()
