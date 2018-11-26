# Creates a child widget for the main window, which is shown when 'settings' button is pushed. Grabs the cached variables from database and displays them. Also pushes the user updated variables to cache which is then saved to database

import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QFormLayout, QLabel, QLineEdit

from database_model import database_model
from settings_board_view import settings_board_view


class SettingsBoardController(QMainWindow):
    def __init__(self):
        super().__init__()

    def load_from_cache(self):
        database_model.fetch_settings()
        settings_board_view.jira_url_value.setText(str(database_model.settings['jira_url']))
        settings_board_view.username_value.setText(str(database_model.settings['username']))
        settings_board_view.api_key_value.setText(str(database_model.settings['api_key']))
        settings_board_view.support_status_value.setText(str(database_model.settings['support_status']))
        settings_board_view.customer_status_value.setText(str(database_model.settings['customer_status']))
        settings_board_view.in_progress_status_value.setText(str(database_model.settings['in_progress_status']))
        settings_board_view.dev_status_value.setText(str(database_model.settings['dev_status']))
        settings_board_view.design_status_value.setText(str(database_model.settings['design_status']))
        settings_board_view.test_status_value.setText(str(database_model.settings['test_status']))
        settings_board_view.black_alert_value.setText(str(database_model.settings['black_alert'] / (60 * 60 * 24)))
        settings_board_view.red_alert_value.setText(str(database_model.settings['red_alert'] / (60 * 60 * 24)))
        settings_board_view.melt_down_value.setText(str(database_model.settings['melt_down'] / (60 * 60 * 24)))

    def save_to_cache(self):
        database_model.settings["jira_url"] = str(settings_board_view.jira_url_value.text())
        database_model.settings["username"] = str(settings_board_view.username_value.text())
        database_model.settings["api_key"] = str(settings_board_view.api_key_value.text())
        database_model.settings["support_status"] = str(settings_board_view.support_status_value.text())
        database_model.settings["customer_status"] = str(settings_board_view.customer_status_value.text())
        database_model.settings["in_progress_status"] = str(settings_board_view.in_progress_status_value.text())
        database_model.settings["dev_status"] = str(settings_board_view.dev_status_value.text())
        database_model.settings["design_status"] = str(settings_board_view.design_status_value.text())
        database_model.settings["test_status"] = str(settings_board_view.test_status_value.text())
        database_model.settings["black_alert"] = float(settings_board_view.black_alert_value.text()) * (60 * 60 * 24)
        database_model.settings["red_alert"] = float(settings_board_view.red_alert_value.text()) * (60 * 60 * 24)
        database_model.settings["melt_down"] = float(settings_board_view.melt_down_value.text()) * (60 * 60 * 24)
        database_model.save_settings()


if __name__ == 'settings_board_controller':
    settings_board_controller = SettingsBoardController()
