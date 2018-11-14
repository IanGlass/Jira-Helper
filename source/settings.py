import sys
from PyQt5 import QtCore, QtWidgets, QtGui
# Used to covert and import datetime
from PyQt5.QtCore import QDate, QTime, Qt

import threading
from database import database


class SettingsBoard(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings_board_widget = QtWidgets.QWidget()
        settings_form = QtWidgets.QFormLayout()
        self.settings_board_widget.setLayout(settings_form)

        self.jira_url_label = QtWidgets.QLabel()
        self.jira_url_value = QtWidgets.QLineEdit()
        self.jira_url_value.setText(database.settings.get('jira_url'))
        self.jira_url_label.setText("JIRA URL")
        settings_form.addRow(self.jira_url_label, self.jira_url_value)

        self.username_label = QtWidgets.QLabel()
        self.username_value = QtWidgets.QLineEdit()
        self.username_value.setText(database.settings.get('username'))
        self.username_label.setText("JIRA Username")
        settings_form.addRow(self.username_label, self.username_value)

        self.api_key_label = QtWidgets.QLabel()
        self.api_key_value = QtWidgets.QLineEdit()
        self.api_key_value.setText(database.settings.get('api_key'))
        self.api_key_label.setText("JIRA Api Key")
        settings_form.addRow(self.api_key_label, self.api_key_value)

        self.support_status_label = QtWidgets.QLabel()
        self.support_status_value = QtWidgets.QLineEdit()
        self.support_status_value.setText(database.settings.get('support_status'))
        self.support_status_label.setText("Support Ticket Status")
        settings_form.addRow(self.support_status_label, self.support_status_value)

        self.customer_status_label = QtWidgets.QLabel()
        self.customer_status_value = QtWidgets.QLineEdit()
        self.customer_status_value.setText(database.settings.get('customer_status'))
        self.customer_status_label.setText("Customer Ticket Status")
        settings_form.addRow(self.customer_status_label, self.customer_status_value)

        self.in_progress_status_label = QtWidgets.QLabel()
        self.in_progress_status_value = QtWidgets.QLineEdit()
        self.in_progress_status_value.setText(database.settings.get('in_progress_status'))
        self.in_progress_status_label.setText("In Progress Ticket Status")
        settings_form.addRow(self.in_progress_status_label, self.in_progress_status_value)

        self.dev_status_label = QtWidgets.QLabel()
        self.dev_status_value = QtWidgets.QLineEdit()
        self.dev_status_value.setText(database.settings.get('dev_status'))
        self.dev_status_label.setText("Dev Ticket Status")
        settings_form.addRow(self.dev_status_label, self.dev_status_value)

        self.design_status_label = QtWidgets.QLabel()
        self.design_status_value = QtWidgets.QLineEdit()
        self.design_status_value.setText(database.settings.get('design_status'))
        self.design_status_label.setText("Design Ticket Status")
        settings_form.addRow(self.design_status_label, self.design_status_value)

        self.test_status_label = QtWidgets.QLabel()
        self.test_status_value = QtWidgets.QLineEdit()
        self.test_status_value.setText(database.settings.get('test_status'))
        self.test_status_label.setText("Test ticket Status")
        settings_form.addRow(self.test_status_label, self.test_status_value)

    def load_from_cache(self):
        database.fetch_settings()
        self.jira_url_value.setText(database.settings.get('jira_url'))
        self.username_value.setText(database.settings.get('username'))
        self.api_key_value.setText(database.settings.get('api_key'))
        self.support_status_value.setText(database.settings.get('support_status'))
        self.customer_status_value.setText(database.settings.get('customer_status'))
        self.in_progress_status_value.setText(database.settings.get('in_progress_status'))
        self.dev_status_value.setText(database.settings.get('dev_status'))
        self.design_status_value.setText(database.settings.get('design_status'))
        self.test_status_value.setText(database.settings.get('test_status'))

    def save_to_cache(self):
        database.settings["jira_url"] = self.jira_url_value.text()
        database.settings["username"] = self.username_value.text()
        database.settings["api_key"] = self.api_key_value.text()
        database.settings["support_status"] = self.support_status_value.text()
        database.settings["customer_status"] = self.customer_status_value.text()
        database.settings["in_progress_status"] = self.in_progress_status_value.text()
        database.settings["dev_status"] = self.dev_status_value.text()
        database.settings["design_status"] = self.design_status_value.text()
        database.settings["test_status"] = self.test_status_value.text()
        database.save_settings()
