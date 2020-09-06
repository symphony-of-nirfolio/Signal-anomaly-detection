from typing import Callable, Tuple

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QMessageBox, QApplication

from gui.main_window import Ui_main_window
from gui.worker import Worker
from handle_data.handle_data import handle_data_to_files


def gui_init_data_extraction(ui: Ui_main_window,
                             main_window: QtWidgets.QMainWindow,
                             event_list: list,
                             thread_pool: QThreadPool,
                             stations_info: dict,
                             set_busy_by: Callable[..., None],
                             is_busy_by: Callable[..., Tuple[bool, str]],
                             on_extract_finished: list,
                             play_finish_notification: Callable[[], None],
                             play_error_notification: Callable[[], None]) -> Callable[[], None]:
    station_id_line_edit = ui.station_id_line_edit
    extract_data_push_button = ui.extract_data_push_button
    data_extraction_status_value_label = ui.data_extraction_status_value_label

    is_extracting_data = False

    def get_station_id() -> str:
        return station_id_line_edit.text()

    def is_current_station_id_in_stations_info() -> bool:
        station_id = get_station_id()
        return station_id in stations_info

    def update_enabled_push_buttons() -> None:
        if is_extracting_data:
            extract_data_push_button.setEnabled(False)
            extract_data_push_button.setToolTip("Data is extracting now")
            return

        if is_current_station_id_in_stations_info():
            station_id = get_station_id()
            is_busy, tooltip = is_busy_by(station_id, is_data_extract=True)
            if is_busy:
                extract_data_push_button.setEnabled(False)
                extract_data_push_button.setToolTip(tooltip)
            else:
                extract_data_push_button.setEnabled(True)
                extract_data_push_button.setToolTip(None)
        else:
            extract_data_push_button.setEnabled(True)
            extract_data_push_button.setToolTip(None)

    def lock_components() -> None:
        station_id_line_edit.setEnabled(False)
        station_id_line_edit.setToolTip("Data is extracting now")

    def unlock_components() -> None:
        station_id_line_edit.setEnabled(True)
        station_id_line_edit.setToolTip(None)

    def on_extract_data_started() -> None:
        nonlocal is_extracting_data
        is_extracting_data = True

        lock_components()

        station_id = get_station_id()
        set_busy_by(station_id, is_data_extract=True)

    def on_extract_data_finished() -> None:
        nonlocal is_extracting_data
        is_extracting_data = False

        unlock_components()

        set_busy_by("", is_data_extract=True)

        [listener() for listener in on_extract_finished]

    def update_station_id_push_buttons() -> None:
        update_enabled_push_buttons()

        if is_current_station_id_in_stations_info():
            extract_data_push_button.setText("Update to latest")
        else:
            extract_data_push_button.setText("Extract data")

    def on_error(message: str) -> None:
        on_extract_data_finished()

        on_status_changed("Crashed!")

        play_error_notification()

        QApplication.alert(main_window)

        QMessageBox.warning(main_window, 'Warning', message, QMessageBox.Ok)

    def on_status_changed(status: str) -> None:
        data_extraction_status_value_label.setText(status)

    def on_finished() -> None:
        on_extract_data_finished()

        play_finish_notification()

        QApplication.alert(main_window)

        update_station_id_push_buttons()

    def on_error_to_event_list(message: str) -> None:
        event_list.append(lambda: on_error(message))

    def on_status_changed_to_event_list(status: str) -> None:
        event_list.append(lambda: on_status_changed(status))

    def on_finished_to_event_list() -> None:
        event_list.append(lambda: on_finished())

    def on_extract_data_push_button_click() -> None:
        on_extract_data_started()

        station_id = get_station_id()
        thread = Worker(
            handle_data_to_files,
            stations_info,
            station_id,
            on_error_to_event_list,
            on_status_changed_to_event_list,
            on_finished_to_event_list)
        thread_pool.start(thread)

    def busy_listener() -> None:
        update_enabled_push_buttons()

    update_station_id_push_buttons()

    station_id_line_edit.textChanged.connect(lambda text: update_station_id_push_buttons())
    extract_data_push_button.clicked.connect(on_extract_data_push_button_click)

    return busy_listener
