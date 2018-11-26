

import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow

from jira_model import jira_model
from build_board_view import build_board_view


class BuildBoardController(QMainWindow):
    def __init__(self):
        super().__init__()
        # Timer update build progress
        self.update_datetime_timer = QTimer(self)
        self.update_datetime_timer.timeout.connect(build_board_view.update_board)
        self.update_datetime_timer.start(10000)  # update every 1 second


if __name__ == 'build_board_controller':
    build_board_controller = BuildBoardController()
