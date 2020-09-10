from typing import Callable

from PyQt5 import QtWidgets
from PyQt5.QtGui import QMovie

from gui.main_window import Ui_main_window
from gui.tutorial_window import Ui_tutorial_window
from gui.window_with_close_listener import WindowWithCloseListener


_tutorial_path = "tutorials/media/"


def _gui_init_tutorial(tutorial_push_button: QtWidgets.QPushButton, title: str, file_name: str) -> Callable[[], None]:
    tutorial_window = None

    is_tutorial_window_open = False

    def on_tutorial_window_close():
        nonlocal is_tutorial_window_open
        is_tutorial_window_open = False
        tutorial_push_button.setEnabled(True)
        # noinspection PyTypeChecker
        tutorial_push_button.setToolTip(None)

    def on_tutorial_push_button_clicked():
        nonlocal is_tutorial_window_open, tutorial_window
        is_tutorial_window_open = True
        tutorial_push_button.setEnabled(False)
        tutorial_push_button.setToolTip("Tutorial window is already open now")

        tutorial_window = WindowWithCloseListener(on_tutorial_window_close)
        tutorial_ui = Ui_tutorial_window()
        tutorial_ui.setupUi(tutorial_window)

        tutorial_window.setWindowTitle(title)
        gif = QMovie(_tutorial_path + file_name)
        tutorial_ui.tutorial_label.setMovie(gif)
        gif.start()

        tutorial_window.show()

    def close_listener() -> None:
        if is_tutorial_window_open:
            # noinspection PyUnresolvedReferences
            creditor_window.close()

    tutorial_push_button.clicked.connect(on_tutorial_push_button_clicked)

    return close_listener


def gui_init_usa_tutorial(ui: Ui_main_window) -> Callable[[], None]:
    return _gui_init_tutorial(ui.usa_tutorial_push_button,
                              "Tutorial for USA country",
                              "usa_country.gif")


def gui_init_all_other_tutorial(ui: Ui_main_window) -> Callable[[], None]:
    return _gui_init_tutorial(ui.all_other_tutorial_push_button,
                              "Tutorial for All other countries",
                              "all_other_countries.gif")
