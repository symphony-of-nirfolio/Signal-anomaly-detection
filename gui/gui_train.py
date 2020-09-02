from typing import Callable

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QMessageBox

from gui.gui_available_observaion import reset_observation, set_observation
from gui.main_window import Ui_main_window
from gui.worker import Worker
from handle_data.data_management import write_stations_info_to_json
from handle_data.handle_neural_network import train_model


def gui_init_train(ui: Ui_main_window,
                   main_window: QtWidgets.QMainWindow,
                   event_list: list,
                   thread_pool: QThreadPool,
                   stations_info: dict,
                   set_busy_by: Callable[..., None],
                   is_busy_by: Callable[..., bool]) -> (Callable[[], None], Callable[[], None]):
    select_station_id_for_training_combo_box = ui.select_station_id_for_training_combo_box
    select_training_observation_vertical_layout = ui.select_training_observation_vertical_layout
    select_training_observations_group_box = ui.select_training_observations_group_box
    train_push_button = ui.train_push_button
    training_status_value_label = ui.training_status_value_label

    min_temperature_combo_box = None
    max_temperature_combo_box = None
    average_temperature_combo_box = None

    is_training = False

    def get_station_id() -> str:
        return select_station_id_for_training_combo_box.currentText()

    def update_enabled_train_button() -> None:
        if is_training:
            train_push_button.setEnabled(False)
            return

        station_id = get_station_id()

        if station_id == "(None)" or station_id == "":
            train_push_button.setEnabled(False)
        else:
            if is_busy_by(station_id, is_train=True):
                train_push_button.setEnabled(False)
            else:
                train_push_button.setEnabled(True)

    def lock_components() -> None:
        select_training_observations_group_box.setEnabled(False)
        select_station_id_for_training_combo_box.setEnabled(False)

    def unlock_components() -> None:
        select_training_observations_group_box.setEnabled(True)
        select_station_id_for_training_combo_box.setEnabled(True)

    def on_train_started() -> None:
        nonlocal is_training
        is_training = True

        lock_components()

        station_id = get_station_id()
        set_busy_by(station_id, is_train=True)

    def on_train_finished() -> None:
        nonlocal is_training
        is_training = False

        unlock_components()

        set_busy_by("", is_train=True)

    def update_station_id_combo_box() -> None:
        index = select_station_id_for_training_combo_box.currentIndex()

        select_station_id_for_training_combo_box.clear()
        select_station_id_for_training_combo_box.addItem("(None)")

        for key in stations_info:
            select_station_id_for_training_combo_box.addItem(key)

        if index < len(select_station_id_for_training_combo_box):
            select_station_id_for_training_combo_box.setCurrentIndex(index)
        else:
            select_station_id_for_training_combo_box.setCurrentIndex(len(select_station_id_for_training_combo_box) - 1)

    def update_train_button() -> None:
        nonlocal min_temperature_combo_box, max_temperature_combo_box, average_temperature_combo_box

        update_enabled_train_button()

        station_id = get_station_id()

        reset_observation(select_training_observation_vertical_layout)

        if station_id == "(None)" or station_id == "":
            train_push_button.setText("Train")
        else:
            if stations_info[station_id]["is_trained"]:
                train_push_button.setText("Retrain")

                min_temperature_combo_box, max_temperature_combo_box, average_temperature_combo_box =\
                    set_observation(
                        select_training_observation_vertical_layout,
                        lambda state: None,
                        stations_info[station_id]["need_min"],
                        stations_info[station_id]["need_max"],
                        stations_info[station_id]["need_average"],
                        is_min_checked=stations_info[station_id]["is_min_trained"],
                        is_max_checked=stations_info[station_id]["is_max_trained"],
                        is_average_checked=stations_info[station_id]["is_average_trained"])
            else:
                train_push_button.setText("Train")

                min_temperature_combo_box, max_temperature_combo_box, average_temperature_combo_box =\
                    set_observation(
                        select_training_observation_vertical_layout,
                        lambda state: None,
                        stations_info[station_id]["need_min"],
                        stations_info[station_id]["need_max"],
                        stations_info[station_id]["need_average"])

    # noinspection PyUnusedLocal
    def on_station_id_combo_box_selected(index: int) -> None:
        update_train_button()

    def on_error(message: str) -> None:
        on_train_finished()
        QMessageBox.warning(main_window, 'Warning', message, QMessageBox.Ok)

    def on_status_changed(status: str) -> None:
        training_status_value_label.setText(status)

    def on_finished(need_min: bool, need_max: bool, need_average: bool) -> None:
        on_train_finished()

        station_id = get_station_id()
        stations_info[station_id]["is_trained"] = True
        stations_info[station_id]["is_min_trained"] = need_min
        stations_info[station_id]["is_max_trained"] = need_max
        stations_info[station_id]["is_average_trained"] = need_average
        stations_info[station_id]["is_cashed_data"] = False
        stations_info[station_id]["is_cashed_anomaly_data"] = False

        write_stations_info_to_json(stations_info)

    def on_error_to_event_list(message: str) -> None:
        event_list.append(lambda: on_error(message))

    def on_status_changed_to_event_list(status: str) -> None:
        event_list.append(lambda: on_status_changed(status))

    def on_finished_to_event_list(need_min: bool, need_max: bool, need_average: bool) -> None:
        event_list.append(lambda: on_finished(need_min, need_max, need_average))

    def on_train_push_button_clicked() -> None:
        on_train_started()

        need_min_temperature = False
        if min_temperature_combo_box is not None:
            # noinspection PyUnresolvedReferences
            need_min_temperature = min_temperature_combo_box.isChecked()

        need_max_temperature = False
        if max_temperature_combo_box is not None:
            # noinspection PyUnresolvedReferences
            need_max_temperature = max_temperature_combo_box.isChecked()

        need_average_temperature = False
        if average_temperature_combo_box is not None:
            # noinspection PyUnresolvedReferences
            need_average_temperature = average_temperature_combo_box.isChecked()

        station_id = get_station_id()
        thread = Worker(
            train_model,
            station_id,
            on_error_to_event_list,
            on_status_changed_to_event_list,
            on_finished_to_event_list,
            need_min_temperature,
            need_max_temperature,
            need_average_temperature)
        thread_pool.start(thread)

    def on_extract_finished() -> None:
        update_station_id_combo_box()

    def busy_listener() -> None:
        update_enabled_train_button()

    update_station_id_combo_box()

    select_station_id_for_training_combo_box.currentIndexChanged.connect(on_station_id_combo_box_selected)
    train_push_button.clicked.connect(on_train_push_button_clicked)

    return busy_listener, on_extract_finished
