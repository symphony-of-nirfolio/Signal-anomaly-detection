from typing import Callable

from PyQt5 import QtWidgets


class WindowWithCloseListener(QtWidgets.QMainWindow):
    def __init__(self, listener: Callable[[], None]) -> None:
        QtWidgets.QMainWindow.__init__(self)

        self.listener = listener

    def closeEvent(self, event) -> None:
        self.listener()

        event.accept()
