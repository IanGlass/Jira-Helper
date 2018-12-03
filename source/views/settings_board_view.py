# Creates a child widget for the main window, which is shown when 'settings' button is pushed. Grabs the cached variables from database and displays them. Also pushes the user updated variables to cache which is then saved to database

import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QFormLayout, QPushButton


class SettingsBoardView(QWidget):
    def __init__(self):
        super(SettingsBoardView, self).__init__()
        settings_form = QFormLayout()
        self.setLayout(settings_form)

        self.jira_url_label = QLabel()
        self.jira_url_value = QLineEdit()
        self.jira_url_label.setText("JIRA URL")
        settings_form.addRow(self.jira_url_label, self.jira_url_value)

        self.username_label = QLabel()
        self.username_value = QLineEdit()
        self.username_label.setText("JIRA Username")
        settings_form.addRow(self.username_label, self.username_value)

        self.api_key_label = QLabel()
        self.api_key_value = QLineEdit()
        self.api_key_label.setText("JIRA Api Key")
        settings_form.addRow(self.api_key_label, self.api_key_value)

        self.support_status_label = QLabel()
        self.support_status_value = QLineEdit()
        self.support_status_label.setText("Support Ticket Status")
        settings_form.addRow(self.support_status_label, self.support_status_value)

        self.customer_status_label = QLabel()
        self.customer_status_value = QLineEdit()
        self.customer_status_label.setText("Customer Ticket Status")
        settings_form.addRow(self.customer_status_label, self.customer_status_value)

        self.in_progress_status_label = QLabel()
        self.in_progress_status_value = QLineEdit()
        self.in_progress_status_label.setText("In Progress Ticket Status")
        settings_form.addRow(self.in_progress_status_label, self.in_progress_status_value)

        self.dev_status_label = QLabel()
        self.dev_status_value = QLineEdit()
        self.dev_status_label.setText("Dev Ticket Status")
        settings_form.addRow(self.dev_status_label, self.dev_status_value)

        self.design_status_label = QLabel()
        self.design_status_value = QLineEdit()
        self.design_status_label.setText("Design Ticket Status")
        settings_form.addRow(self.design_status_label, self.design_status_value)

        self.test_status_label = QLabel()
        self.test_status_value = QLineEdit()
        self.test_status_label.setText("Test ticket Status")
        settings_form.addRow(self.test_status_label, self.test_status_value)

        self.black_alert_label = QLabel()
        self.black_alert_value = QLineEdit()
        self.black_alert_label.setText("Age of black tickets (days)")
        settings_form.addRow(self.black_alert_label, self.black_alert_value)

        self.red_alert_label = QLabel()
        self.red_alert_value = QLineEdit()
        self.red_alert_label.setText("Age of flashing red tickets (days), must be > black tickets")
        settings_form.addRow(self.red_alert_label, self.red_alert_value)

        self.melt_down_label = QLabel()
        self.melt_down_value = QLineEdit()
        self.melt_down_label.setText("Age of solid red tickets (days), must be > flashing red tickets")
        settings_form.addRow(self.melt_down_label, self.melt_down_value)

        self.clean_queue_delay_label = QLabel()
        self.clean_queue_delay_value = QLineEdit()
        self.clean_queue_delay_label.setText("Time in customer queue (days) until automated message is sent")
        settings_form.addRow(self.clean_queue_delay_label, self.clean_queue_delay_value)

        self.automated_message_label = QLabel()
        self.automated_message_value = QLineEdit()
        self.automated_message_label.setText("Please enter your automated message here")
        settings_form.addRow(self.automated_message_label, self.automated_message_value)

        self.toggle_ticket_board_button = QPushButton()
        self.toggle_ticket_board_button.setCheckable(True)
        self.toggle_ticket_board_button.setChecked(True)
        self.toggle_ticket_board_button.setText('Enable/Disable Ticket Board')

        self.toggle_analytics_board_button = QPushButton()
        self.toggle_analytics_board_button.setCheckable(True)
        self.toggle_analytics_board_button.setChecked(True)
        self.toggle_analytics_board_button.setText('Enable/Disable Analytics Board')

        self.toggle_build_board_button = QPushButton()
        self.toggle_build_board_button.setCheckable(True)
        self.toggle_build_board_button.setChecked(True)
        self.toggle_build_board_button.setText('Enable/Disable Build Board')

        settings_form.addRow(self.toggle_ticket_board_button)
        settings_form.addRow(self.toggle_analytics_board_button)
        settings_form.addRow(self.toggle_build_board_button)


if __name__ == 'settings_board_view':
    print('Instantiating settings_view')
    settings_board_view = SettingsBoardView()
