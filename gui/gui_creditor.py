from typing import Callable

from gui.creditor_window import Ui_creditor_window
from gui.main_window import Ui_main_window
from gui.window_with_close_listener import WindowWithCloseListener


def gui_init_creditor(ui: Ui_main_window) -> Callable[[], None]:
    action_creditor = ui.action_creditor

    creditor_window = None

    is_creditor_window_open = False

    def on_creditor_window_close():
        nonlocal is_creditor_window_open
        is_creditor_window_open = False
        action_creditor.setEnabled(True)
        action_creditor.setToolTip(None)

    def on_action_creditor_clicked():
        nonlocal is_creditor_window_open, creditor_window
        is_creditor_window_open = True
        action_creditor.setEnabled(False)
        action_creditor.setToolTip("Creditor window is already open")

        creditor_window = WindowWithCloseListener(on_creditor_window_close)
        creditor_ui = Ui_creditor_window()
        creditor_ui.setupUi(creditor_window)

        creditor_window.show()

    def close_listener() -> None:
        if is_creditor_window_open:
            # noinspection PyUnresolvedReferences
            creditor_window.close()

    action_creditor.triggered.connect(on_action_creditor_clicked)

    return close_listener
