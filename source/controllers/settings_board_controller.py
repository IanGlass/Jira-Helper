# Creates a child widget for the main window, which is shown when 'settings' button is pushed. Grabs and saves the settings from file using the QSettings object

import sys
from PyQt5.QtCore import QObject, QSettings
from PyQt5.QtWidgets import QWidget, QFormLayout, QLabel, QLineEdit

from settings_board_view import settings_board_view
from jira import JIRA


class SettingsBoardController(QObject):
    def __init__(self):
        super(SettingsBoardController, self).__init__()
        self.settings = QSettings('Open-Source', 'Jira-Helper')
        # Check if settings is empty and set defaults,
        if (self.settings.value('black_alert') is None):  # Then settings is empty and needs some defaults in (s)
            self.settings.setValue('black_alert', 172800)
            self.settings.setValue('red_alert', 432000)
            self.settings.setValue('melt_down', 864000)
            self.settings.setValue('clean_queue_delay', 864000)

    def toggle_display_boards(self):  # Remove/add boards from QStackedWidget
        if (settings_board_view.toggle_ticket_board_button.isChecked()):
            main_view.window.addWidget(ticket_board_view)
        else:
            main_view.window.removeWidget(ticket_board_view)

        if (settings_board_view.toggle_analytics_board_button.isChecked()):
            main_view.window.addWidget(analytics_board_view)
        else:
            main_view.window.removeWidget(analytics_board_view)

        if (settings_board_view.toggle_build_board_button.isChecked()):
            main_view.window.addWidget(build_board_view)
        else:
            main_view.window.removeWidget(build_board_view)

    def load_settings(self):
        settings_board_view.jira_url_value.setText(self.settings.value('jira_url'))
        settings_board_view.username_value.setText(self.settings.value('username'))
        settings_board_view.api_key_value.setText(self.settings.value('api_key'))
        settings_board_view.support_status_value.setText(self.settings.value('support_status'))
        settings_board_view.customer_status_value.setText(self.settings.value('customer_status'))
        settings_board_view.in_progress_status_value.setText(self.settings.value('in_progress_status'))
        settings_board_view.dev_status_value.setText(self.settings.value('dev_status'))
        settings_board_view.design_status_value.setText(self.settings.value('design_status'))
        settings_board_view.test_status_value.setText(self.settings.value('test_status'))
        settings_board_view.black_alert_value.setText(str(self.settings.value('black_alert', type=int) / (60 * 60 * 24)))
        settings_board_view.red_alert_value.setText(str(self.settings.value('red_alert', type=int) / (60 * 60 * 24)))
        settings_board_view.melt_down_value.setText(str(self.settings.value('melt_down', type=int) / (60 * 60 * 24)))
        settings_board_view.clean_queue_delay_value.setText(str(self.settings.value('clean_queue_delay', type=int) / (60 * 60 * 24)))
        settings_board_view.automated_message_value.setText(self.settings.value('automated_message'))

    def save_settings(self):
        # Toggle the board status' on submit
        self.toggle_display_boards()

        # Load settings into db obj from view
        self.settings.setValue('jira_url', str(settings_board_view.jira_url_value.text()))
        self.settings.setValue('username', str(settings_board_view.username_value.text()))
        self.settings.setValue('api_key', str(settings_board_view.api_key_value.text()))
        self.settings.setValue('support_status', str(settings_board_view.support_status_value.text()))
        self.settings.setValue('customer_status', str(settings_board_view.customer_status_value.text()))
        self.settings.setValue('in_progress_status', str(settings_board_view.in_progress_status_value.text()))
        self.settings.setValue('dev_status', str(settings_board_view.dev_status_value.text()))
        self.settings.setValue('design_status', str(settings_board_view.design_status_value.text()))
        self.settings.setValue('test_status', str(settings_board_view.test_status_value.text()))
        self.settings.setValue('black_alert', float(settings_board_view.black_alert_value.text()) * (60 * 60 * 24))
        self.settings.setValue('red_alert', float(settings_board_view.red_alert_value.text()) * (60 * 60 * 24))
        self.settings.setValue('melt_down', float(settings_board_view.melt_down_value.text()) * (60 * 60 * 24))
        self.settings.setValue('clean_queue_delay', float(settings_board_view.clean_queue_delay_value.text()) * (60 * 60 * 24))
        self.settings.setValue('automated_message', str(settings_board_view.automated_message_value.text()))


if __name__ == 'settings_board_controller':
    print('Instantiating ' + __name__)
    settings_board_controller = SettingsBoardController()
    from main_view import main_view
    from ticket_board_view import ticket_board_view
    from analytics_board_view import analytics_board_view
    from build_board_view import build_board_view
