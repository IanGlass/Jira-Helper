

import sys
from PyQt5.QtCore import QTimer, QObject

from jira_model import jira_model
from build_board_view import build_board_view


class BuildBoardController(QObject):
    def __init__(self):
        super().__init__()
        # Timer update build progress
        self.update_build_board = QTimer(self)
        self.update_build_board.timeout.connect(build_board_view.update_board)
        self.update_build_board.start(10000)  # update every 10 seconds


if __name__ == 'build_board_controller':
    build_board_controller = BuildBoardController()
