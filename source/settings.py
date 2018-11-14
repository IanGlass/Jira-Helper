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
        self.jira_url_value.setText(str(database.settings['jira_url']))
        self.jira_url_label.setText("JIRA URL")
        settings_form.addRow(self.jira_url_label, self.jira_url_value)

        self.username_label = QtWidgets.QLabel()
        self.username_value = QtWidgets.QLineEdit()
        self.username_value.setText(str(database.settings['username']))
        self.username_label.setText("JIRA Username")
        settings_form.addRow(self.username_label, self.username_value)

        self.api_key_label = QtWidgets.QLabel()
        self.api_key_value = QtWidgets.QLineEdit()
        self.api_key_value.setText(str(database.settings['api_key']))
        self.api_key_label.setText("JIRA Api Key")
        settings_form.addRow(self.api_key_label, self.api_key_value)

        self.support_status_label = QtWidgets.QLabel()
        self.support_status_value = QtWidgets.QLineEdit()
        self.support_status_value.setText(str(database.settings['support_status']))
        self.support_status_label.setText("Support Ticket Status")
        settings_form.addRow(self.support_status_label, self.support_status_value)

        self.customer_status_label = QtWidgets.QLabel()
        self.customer_status_value = QtWidgets.QLineEdit()
        self.customer_status_value.setText(str(database.settings['customer_status']))
        self.customer_status_label.setText("Customer Ticket Status")
        settings_form.addRow(self.customer_status_label, self.customer_status_value)

        self.in_progress_status_label = QtWidgets.QLabel()
        self.in_progress_status_value = QtWidgets.QLineEdit()
        self.in_progress_status_value.setText(str(database.settings['in_progress_status']))
        self.in_progress_status_label.setText("In Progress Ticket Status")
        settings_form.addRow(self.in_progress_status_label, self.in_progress_status_value)

        self.dev_status_label = QtWidgets.QLabel()
        self.dev_status_value = QtWidgets.QLineEdit()
        self.dev_status_value.setText(str(database.settings['dev_status']))
        self.dev_status_label.setText("Dev Ticket Status")
        settings_form.addRow(self.dev_status_label, self.dev_status_value)

        self.design_status_label = QtWidgets.QLabel()
        self.design_status_value = QtWidgets.QLineEdit()
        self.design_status_value.setText(str(database.settings['design_status']))
        self.design_status_label.setText("Design Ticket Status")
        settings_form.addRow(self.design_status_label, self.design_status_value)

        self.test_status_label = QtWidgets.QLabel()
        self.test_status_value = QtWidgets.QLineEdit()
        self.test_status_value.setText(str(database.settings['test_status']))
        self.test_status_label.setText("Test ticket Status")
        settings_form.addRow(self.test_status_label, self.test_status_value)

        self.black_alert_label = QtWidgets.QLabel()
        self.black_alert_value = QtWidgets.QLineEdit()
        self.black_alert_value.setText(str(database.settings['black_alert']))
        self.black_alert_label.setText("Age of black tickets (days)")
        settings_form.addRow(self.black_alert_label, self.black_alert_value)

        self.red_alert_label = QtWidgets.QLabel()
        self.red_alert_value = QtWidgets.QLineEdit()
        self.red_alert_value.setText(str(database.settings['red_alert']))
        self.red_alert_label.setText("Age of flashing red tickets (days), must be > black tickets")
        settings_form.addRow(self.red_alert_label, self.red_alert_value)

        self.melt_down_label = QtWidgets.QLabel()
        self.melt_down_value = QtWidgets.QLineEdit()
        self.melt_down_value.setText(str(database.settings['melt_down']))
        self.melt_down_label.setText("Age of solid red tickets (days), must be > flashing red tickets")
        settings_form.addRow(self.melt_down_label, self.melt_down_value)

    def load_from_cache(self):
        database.fetch_settings()
        self.jira_url_value.setText(str(database.settings['jira_url']))
        self.username_value.setText(str(database.settings['username']))
        self.api_key_value.setText(str(database.settings['api_key']))
        self.support_status_value.setText(str(database.settings['support_status']))
        self.customer_status_value.setText(str(database.settings['customer_status']))
        self.in_progress_status_value.setText(str(database.settings['in_progress_status']))
        self.dev_status_value.setText(str(database.settings['dev_status']))
        self.design_status_value.setText(str(database.settings['design_status']))
        self.test_status_value.setText(str(database.settings['test_status']))
        self.black_alert_value.setText(str(database.settings['black_alert'] / (60 * 60 * 24)))
        self.red_alert_value.setText(str(database.settings['red_alert'] / (60 * 60 * 24)))
        self.melt_down_value.setText(str(database.settings['melt_down'] / (60 * 60 * 24)))

    def save_to_cache(self):
        database.settings["jira_url"] = str(self.jira_url_value.text())
        database.settings["username"] = str(self.username_value.text())
        database.settings["api_key"] = str(self.api_key_value.text())
        database.settings["support_status"] = str(self.support_status_value.text())
        database.settings["customer_status"] = str(self.customer_status_value.text())
        database.settings["in_progress_status"] = str(self.in_progress_status_value.text())
        database.settings["dev_status"] = str(self.dev_status_value.text())
        database.settings["design_status"] = str(self.design_status_value.text())
        database.settings["test_status"] = str(self.test_status_value.text())
        database.settings["black_alert"] = float(self.black_alert_value.text()) * (60 * 60 * 24)
        database.settings["red_alert"] = float(self.red_alert_value.text()) * (60 * 60 * 24)
        database.settings["melt_down"] = float(self.melt_down_value.text()) * (60 * 60 * 24)
        database.save_settings()
