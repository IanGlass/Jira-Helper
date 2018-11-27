# Creates the main window and top row tool panel containing the 'settings' and 'clean queue' button, time and date. Also performs waiting on customer queue cleaning through a background thread which is toggled using the 'clean queue' button

import sys
from PyQt5.QtCore import QTimer, QObject
from PyQt5.QtWidgets import QApplication

from jira import JIRA
import threading
from datetime import datetime
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = dir_path[:-12]
sys.path.append(dir_path + '\\models')
sys.path.append(dir_path + '\\views')
sys.path.append(dir_path + '\\controllers')
sys.path.append(dir_path + '\\services')

app = QApplication(sys.argv)

AUTOMATED_MESSAGE = "Hi Team,\n\nThis is an automated email from the Wherewolf Support System.\n\nIt has been over 7 days since we have received a responce in relation to your support ticket.\n\nCan you please confirm if the ticket/request requires further attention or if it has been resolved and can be closed\n\nPlease respond to this email so we can take appropriate action.\n\nMany thanks,\n\nWherewolf Support"
TRANSITION_PERIOD = 10 * 1000  # (miliseconds) time between page swap
QUEUE_OVERDUE = 60 * 60 * 24 * 7  # (seconds) waiting on customer tickets older than
# this are thrown back into waiting on support with (follow up with client) text added to summary


class MainController(QObject):
    def __init__(self):
        super(MainController, self).__init__()
        engine = create_engine('sqlite:///jira_helper.db')
        Base.metadata.bind = engine
        self.DBSession = sessionmaker(bind=engine)

        # Attach controller function to submit button view
        main_view.settings_submit_button.clicked.connect(self.push_settings_button)

        # Timer used to fetch the waiting on customer queue and throw back into
        clean_queue_timer = QTimer(self)
        clean_queue_timer.timeout.connect(self.clean_queue_timeout)
        clean_queue_timer.start(60 * 1000)  # Clean every minute

        # Timer used to transition the page
        self.transition_page_timer = QTimer(self)
        self.transition_page_timer.timeout.connect(main_view.transition_page)
        self.transition_page_timer.start(TRANSITION_PERIOD)

        # Timer update board
        update_datetime_timer = QTimer(self)
        update_datetime_timer.timeout.connect(main_view.update_datetime)
        update_datetime_timer.start(1000)  # update every 1 second

    def clean_queue_timeout(self):
        '''Timeout function to create a thread and execute self.clean_queue()'''
        if main_view.clean_queue_button.isChecked():
            # Load thread into obj
            clean_queue_thread = threading.Thread(target=self.clean_queue)
            clean_queue_thread.start()  # Start thread

    def clean_queue(self):
        '''Periodically called to check through the 'waiting for customer' queue and send an automated message'''
        # Try to get a transition key if there are any tickets in waiting for customer
        try:
            session = self.DBSession()
            jira = JIRA(basic_auth=(str(settings.username), str(settings.api_key)), options={'server': settings.jira_url})
            # Get list of transitions for a ticket in the waiting on customer queue
            transitions = jira.transitions(ticket_board.customer_tickets[0].key)
            # Find the transition key needed to move from waiting for customer to cold tickets queue
            for key in transitions:
                if (key['name'] == 'No reply transition'):
                    transition_key = key['id']

            for customer_ticket in ticket_board.customer_tickets:
                if customer_ticket.key == 'WS-909':
                    date = datetime.now()  # Get current date
                    # Truncate and convert string to datetime obj
                    customer_ticket_date = parser.parse(customer_ticket.fields.updated[0:23])
                    last_updated = (date - customer_ticket_date).total_seconds()
                    if (last_updated > QUEUE_OVERDUE):  # If tickets are overdue
                        # Fetch the comments obj for the current ticket
                        comments = jira.issue(customer_ticket.key)
                        # Check last comment in the ticket and see if it was the AUTOMATED_MESSAGE, if so
                        # client has not responded to automation message. Throw into cold queue
                        if AUTOMATED_MESSAGE in comments.raw['fields']['comment']['comments'][len(comments.raw['fields']['comment']['comments']) - 1]['body']:
                            jira.transition_issue(customer_ticket, transition_key)
                        else:  # AUTOMATION_MESSAGE not found, then ticket is just old, add AUTOMATION_MESSAGE to ticket
                            jira.add_comment(customer_ticket.key, AUTOMATED_MESSAGE, is_internal=False)

        except:
            print("No tickets to check or invalid transition key")

    def push_settings_button(self):
        '''Push button function to stop page transitions, set the settings page as the active widget, load the cached settings retrieved from the db and change its own on push function'''
        self.transition_page_timer.stop()
        main_view.window.addWidget(settings_board_view)
        main_view.window.setCurrentWidget(settings_board_view)

        # Load values
        settings_board_controller.load_settings()

        # Remove all currently connected functions
        main_view.settings_submit_button.disconnect()
        # Change button submit to save current results
        main_view.settings_submit_button.clicked.connect(main_controller.push_submit_button)
        main_view.settings_submit_button.setText("Submit")

    def push_submit_button(self):
        '''Push button function to trigger transitions again, remove the settings widget, save the settings to cache and db and change its own on push function'''
        self.transition_page_timer.start()
        main_view.window.removeWidget(settings_board_view)  # Remove settings board so it doesn't show in transition

        # Save values to cache and db
        settings_board_controller.save_settings()

        main_view.settings_submit_button.disconnect()
        main_view.settings_submit_button.clicked.connect(main_controller.push_settings_button)
        main_view.settings_submit_button.setText("Settings")


if __name__ == '__main__':
    from main_view import main_view
    # Instantiate models, dbs and services
    from settings_model import Base, SettingsModel
    from ticket_history_model import TicketHistoryModel
    from jira_service import jira_service
    main_controller = MainController()
    main_view.setWindowTitle('Jira Helper')
    # Can't import module until instantiation of main_view
    from ticket_board_controller import ticket_board_controller
    from analytics_board_controller import analytics_board_controller
    from build_board_controller import build_board_controller
    from settings_board_controller import settings_board_controller
    from settings_board_view import settings_board_view
    main_view.showMaximized()
    sys.exit(app.exec_())  # Launch event loop
