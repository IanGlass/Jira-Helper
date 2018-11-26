# Creates the main window and top row tool panel containing the 'settings' and 'clean queue' button, time and date. Also performs waiting on customer queue cleaning through a background thread which is toggled using the 'clean queue' button

import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication 

from jira import JIRA
import threading
from datetime import datetime
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = dir_path[:-12]
sys.path.append(dir_path + '\\models')
sys.path.append(dir_path + '\\views')
sys.path.append(dir_path + '\\controllers')

app = QApplication(sys.argv)

from main_view import main_view
from database_model import database_model
from jira_model import jira_model

AUTOMATED_MESSAGE = "Hi Team,\n\nThis is an automated email from the Wherewolf Support System.\n\nIt has been over 7 days since we have received a responce in relation to your support ticket.\n\nCan you please confirm if the ticket/request requires further attention or if it has been resolved and can be closed\n\nPlease respond to this email so we can take appropriate action.\n\nMany thanks,\n\nWherewolf Support"

# TODO make these defined from settings page in db
TRANSITION_PERIOD = 10 * 1000  # (miliseconds) time between page swap
QUEUE_OVERDUE = 60 * 60 * 24 * 7  # (seconds) waiting on customer tickets older than
# this are thrown back into waiting on support with (follow up with client) text added to summary

# TODO
# Place check_queue into own class?
# Silence waiting for customer ticket updates so last_updated is not affected, if possible
# Remove update to customer ticket summary and write an internal comment instead
# Create gui constructor methods for each class
# Remove self. where its not needed


class MainController(QMainWindow):
    def __init__(self):
        super().__init__()

        # Attach controller function to submit button view
        main_view.settings_submit_button.clicked.connect(self.push_settings_button)

        # Timer used to fetch the waiting on customer queue and throw back into
        self.clean_queue_timer = QTimer(self)
        self.clean_queue_timer.timeout.connect(self.clean_queue_timeout)
        self.clean_queue_timer.start(60 * 1000)  # Clean every minute

        # Timer used to transition the page
        self.transition_page_timer = QTimer(self)
        self.transition_page_timer.timeout.connect(main_view.transition_page)
        self.transition_page_timer.start(TRANSITION_PERIOD)

        # Timer update board
        self.update_datetime_timer = QTimer(self)
        self.update_datetime_timer.timeout.connect(main_view.update_datetime)
        self.update_datetime_timer.start(1000)  # update every 1 second

    def clean_queue_timeout(self):
        if main_view.clean_queue_button.isChecked():
            # Load thread into obj
            self.clean_queue_thread = threading.Thread(target=self.clean_queue)
            self.clean_queue_thread.start()  # Start thread

    def clean_queue(self):
        # Try to get a transition key if there are any tickets in waiting for customer
        try:
            jira = JIRA(basic_auth=(database.settings['username'], database.settings['api_key']), options={'server': database.settings['jira_url']})
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
        self.transition_page_timer.stop()
        main_view.window.addWidget(settings_board_view.settings_board_widget)
        main_view.window.setCurrentWidget(settings_board_view.settings_board_widget)

        # Load values
        settings_board_view.load_from_cache()

        # Remove all currently connected functions
        main_view.settings_submit_button.disconnect()
        # Change button submit to save current results
        main_view.settings_submit_button.clicked.connect(main_controller.push_submit_button)
        main_view.settings_submit_button.setText("Submit")

    def push_submit_button(self):
        self.transition_page_timer.start()
        main_view.window.removeWidget(settings_board_view.settings_board_widget)  # Remove settings board so it doesn't show in transition

        # Save values to cache and db
        settings_board_view.save_to_cache()

        main_view.settings_submit_button.disconnect()
        main_view.settings_submit_button.clicked.connect(main_controller.push_settings_button)
        main_view.settings_submit_button.setText("Settings")


if __name__ == '__main__':
    main_controller = MainController()
    main_view.setWindowTitle('Jira Helper')
    # Can't import module until instantiation of main_view
    import ticket_board_controller
    from ticket_board_view import ticket_board_view
    from analytics_board_controller import analytics_board_controller
    from build_board_controller import build_board_controller
    from settings_board_view import settings_board_view
    main_view.showMaximized()
    sys.exit(app.exec_())  # Launch event loop
