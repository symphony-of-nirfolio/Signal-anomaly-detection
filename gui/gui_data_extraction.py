from typing import Callable

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QMessageBox

from gui.main_window import Ui_main_window
from gui.worker import Worker
from handle_data.handle_data import handle_data_to_files


def gui_init_data_extraction(ui: Ui_main_window,
                             main_window: QtWidgets.QMainWindow,
                             event_list: list,
                             thread_pool: QThreadPool,
                             stations_info: dict,
                             set_busy_by: Callable,
                             is_busy_by: Callable,
                             on_extract_finished: list) -> Callable:
    station_id_line_edit = ui.station_id_line_edit
    extract_data_push_button = ui.extract_data_push_button
    data_extraction_status_value_label = ui.data_extraction_status_value_label

    is_extracting_data = False

    def get_station_id():
        return station_id_line_edit.text()

    def is_current_station_id_in_stations_info():
        station_id = get_station_id()
        return station_id in stations_info

    def update_enabled_push_buttons():
        if is_extracting_data:
            extract_data_push_button.setEnabled(False)
            return

        if is_current_station_id_in_stations_info():
            station_id = get_station_id()
            if is_busy_by(station_id, is_data_extract=True):
                extract_data_push_button.setEnabled(False)
            else:
                extract_data_push_button.setEnabled(True)
        else:
            extract_data_push_button.setEnabled(True)

    def lock_components():
        station_id_line_edit.setEnabled(False)

    def unlock_components():
        station_id_line_edit.setEnabled(True)

    def on_extract_data_started():
        nonlocal is_extracting_data
        is_extracting_data = True

        lock_components()

        station_id = get_station_id()
        set_busy_by(station_id, is_data_extract=True)

    def on_extract_data_finished():
        nonlocal is_extracting_data
        is_extracting_data = False

        unlock_components()

        set_busy_by("", is_data_extract=True)

        [listener() for listener in on_extract_finished]

    def update_station_id_push_buttons():
        update_enabled_push_buttons()

        if is_current_station_id_in_stations_info():
            extract_data_push_button.setText("Update to latest")
        else:
            extract_data_push_button.setText("Extract data")

    def on_error(message):
        on_extract_data_finished()

        QMessageBox.warning(main_window, 'Warning', message, QMessageBox.Ok)

    def on_status_changed(status):
        data_extraction_status_value_label.setText(status)

    def on_finished():
        on_extract_data_finished()

        update_station_id_push_buttons()

    def on_error_to_event_list(message):
        event_list.append(lambda: on_error(message))

    def on_status_changed_to_event_list(status):
        event_list.append(lambda: on_status_changed(status))

    def on_finished_to_event_list():
        event_list.append(lambda: on_finished())

    def on_extract_data_push_button_click():
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

    def busy_listener():
        update_enabled_push_buttons()

    update_station_id_push_buttons()

    station_id_line_edit.textChanged.connect(lambda text: update_station_id_push_buttons())
    extract_data_push_button.clicked.connect(on_extract_data_push_button_click)

    return busy_listener
