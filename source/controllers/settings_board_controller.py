# Creates a child widget for the main window, which is shown when 'settings' button is pushed. Grabs the cached variables from database and displays them. Also pushes the user updated variables to cache which is then saved to database

import sys
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget, QFormLayout, QLabel, QLineEdit

from settings_board_view import settings_board_view
from settings_model import Base, SettingsModel

from jira import JIRA
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class SettingsBoardController(QObject):
    def __init__(self):
        super(SettingsBoardController, self).__init__()
        engine = create_engine('sqlite:///jira_helper.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()
        self.settings = SettingsModel()

    def toggle_display_boards(self):
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
        settings = self.session.query(SettingsModel).first()
        if (settings is None):
            # Create settings row if none exists, with some defaults
            settings = SettingsModel(
                ID=100,
                jira_url='',
                username='',
                api_key='',
                support_status='',
                customer_status='',
                in_progress_status='',
                dev_status='',
                design_status='',
                test_status='',
                black_alert=172800,
                red_alert=432000,
                melt_down=864000,
                clean_queue_delay=864000,
                automated_message=''
            )
            # Add the new record so that save_settings has something to grab
            self.session.add(settings)
            self.session.commit()

        settings_board_view.jira_url_value.setText(settings.jira_url)
        settings_board_view.username_value.setText(settings.username)
        settings_board_view.api_key_value.setText(settings.api_key)
        settings_board_view.support_status_value.setText(settings.support_status)
        settings_board_view.customer_status_value.setText(settings.customer_status)
        settings_board_view.in_progress_status_value.setText(settings.in_progress_status)
        settings_board_view.dev_status_value.setText(settings.dev_status)
        settings_board_view.design_status_value.setText(settings.design_status)
        settings_board_view.test_status_value.setText(settings.test_status)
        settings_board_view.black_alert_value.setText(str(settings.black_alert / (60 * 60 * 24)))
        settings_board_view.red_alert_value.setText(str(settings.red_alert / (60 * 60 * 24)))
        settings_board_view.melt_down_value.setText(str(settings.melt_down / (60 * 60 * 24)))
        settings_board_view.clean_queue_delay_value.setText(str(settings.clean_queue_delay / (60 * 60 * 24)))
        settings_board_view.automated_message_value.setText(settings.automated_message)

    def save_settings(self):
        # Toggle the board status' on submit
        self.toggle_display_boards()
        settings = self.session.query(SettingsModel).first()

        # Load settings into db obj from view
        settings.jira_url = str(settings_board_view.jira_url_value.text())
        settings.username = str(settings_board_view.username_value.text())
        settings.api_key = str(settings_board_view.api_key_value.text())
        settings.support_status = str(settings_board_view.support_status_value.text())
        settings.customer_status = str(settings_board_view.customer_status_value.text())
        settings.in_progress_status = str(settings_board_view.in_progress_status_value.text())
        settings.dev_status = str(settings_board_view.dev_status_value.text())
        settings.design_status = str(settings_board_view.design_status_value.text())
        settings.test_status = str(settings_board_view.test_status_value.text())
        settings.black_alert = float(settings_board_view.black_alert_value.text()) * (60 * 60 * 24)
        settings.red_alert = float(settings_board_view.red_alert_value.text()) * (60 * 60 * 24)
        settings.melt_down = float(settings_board_view.melt_down_value.text()) * (60 * 60 * 24)
        settings.clean_queue_delay = float(settings_board_view.clean_queue_delay_value.text()) * (60 * 60 * 24)
        settings.automated_message = str(settings_board_view.automated_message_value.text())

        self.session.query(SettingsModel).filter(SettingsModel.ID == 0).update({"jira_url": settings.jira_url})
        self.session.commit()


if __name__ == 'settings_board_controller':
    settings_board_controller = SettingsBoardController()
    from main_view import main_view
    from ticket_board_view import ticket_board_view
    from analytics_board_view import analytics_board_view
    from build_board_view import build_board_view
