from typing import Callable

from gui.main_window import Ui_main_window
from gui.settings_window import Ui_settings_window
from gui.window_with_close_listener import WindowWithCloseListener


def gui_init_settings(ui: Ui_main_window) -> Callable[[], None]:
    action_settings = ui.action_settings

    settings_window = None

    is_settings_window_open = False

    def on_settings_window_close():
        nonlocal is_settings_window_open
        is_settings_window_open = False
        action_settings.setEnabled(True)

    def on_action_settings_clicked():
        nonlocal is_settings_window_open, settings_window
        is_settings_window_open = True
        action_settings.setEnabled(False)

        settings_window = WindowWithCloseListener(on_settings_window_close)
        settings_ui = Ui_settings_window()
        settings_ui.setupUi(settings_window)

        settings_window.show()

    def close_listener() -> None:
        if is_settings_window_open:
            # noinspection PyUnresolvedReferences
            settings_window.close()

    action_settings.triggered.connect(on_action_settings_clicked)

    return close_listener
