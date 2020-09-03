from typing import Callable

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QMessageBox

from gui.custom_data_window import Ui_custom_data_window
from gui.gui_available_observaion import set_observation, reset_observation
from gui.gui_diagrams_data_handle import gui_init_diagrams_data_handle
from gui.main_window import Ui_main_window
from gui.window_with_close_listener import WindowWithCloseListener
from gui.worker import Worker
from handle_data.data_management import get_stations_data_from_file


def gui_init_diagrams(ui: Ui_main_window,
                      main_window: QtWidgets.QMainWindow,
                      event_list: list,
                      thread_pool: QThreadPool,
                      stations_info: dict,
                      set_busy_by: Callable[..., None],
                      is_busy_by: Callable[..., bool]) -> (Callable[[], None], Callable[[], None]):
    select_station_id_for_diagram_combo_box = ui.select_station_id_for_diagram_combo_box
    select_diagram_observations_group_box = ui.select_diagram_observations_group_box
    select_diagram_observation_vertical_layout = ui.select_diagram_observation_vertical_layout
    select_period_type_combo_box = ui.select_period_type_combo_box
    select_observation_for_anomaly_combo_box = ui.select_observation_for_anomaly_combo_box
    periods_list_widget = ui.periods_list_widget
    load_status_value_label = ui.load_status_value_label
    custom_data_push_button = ui.custom_data_push_button

    data = {}
    anomaly_data = {}
    is_trained = False
    trained_on = (False, False, False)
    last_station_id = ""

    min_temperature_combo_box = None
    max_temperature_combo_box = None
    average_temperature_combo_box = None

    custom_data_window = None
    custom_data_ui = None

    # noinspection PyUnusedLocal
    is_custom_data_window_open = False

    is_updating_station_id_combo_box = False

    def get_station_id() -> str:
        return select_station_id_for_diagram_combo_box.currentText()

    def update_station_id_combo_box() -> None:
        nonlocal is_updating_station_id_combo_box
        is_updating_station_id_combo_box = True

        index = select_station_id_for_diagram_combo_box.currentIndex()

        select_station_id_for_diagram_combo_box.clear()
        select_station_id_for_diagram_combo_box.addItem("(None)")

        i = 1
        for key in stations_info:
            select_station_id_for_diagram_combo_box.addItem(key)

            if is_busy_by(key, is_diagram=True):
                select_station_id_for_diagram_combo_box.model().item(i).setEnabled(False)

            i += 1

        if index < len(select_station_id_for_diagram_combo_box):
            select_station_id_for_diagram_combo_box.setCurrentIndex(index)
        else:
            select_station_id_for_diagram_combo_box.setCurrentIndex(len(select_station_id_for_diagram_combo_box) - 1)

        is_updating_station_id_combo_box = False

    def lock_components() -> None:
        select_station_id_for_diagram_combo_box.setEnabled(False)
        select_period_type_combo_box.setEnabled(False)
        select_observation_for_anomaly_combo_box.setEnabled(False)
        select_diagram_observations_group_box.setEnabled(False)
        periods_list_widget.setEnabled(False)

    def unlock_components() -> None:
        select_station_id_for_diagram_combo_box.setEnabled(True)
        select_period_type_combo_box.setEnabled(True)
        select_observation_for_anomaly_combo_box.setEnabled(True)
        select_diagram_observations_group_box.setEnabled(True)
        periods_list_widget.setEnabled(True)

    def on_load_started() -> None:
        lock_components()

    def on_load_finished() -> None:
        unlock_components()

    def on_error(message: str) -> None:
        on_load_finished()

        on_status_changed("Crashed!")

        QMessageBox.warning(main_window, 'Warning', message, QMessageBox.Ok)

    def on_status_changed(status: str) -> None:
        load_status_value_label.setText(status)

    def on_finished(loaded_data: dict,
                    loaded_anomaly_data: dict,
                    loaded_is_trained: bool,
                    loaded_trained_on: (bool, bool, bool)) -> None:
        nonlocal data, anomaly_data, is_trained, trained_on,\
            min_temperature_combo_box, max_temperature_combo_box, average_temperature_combo_box
        data = loaded_data
        anomaly_data = loaded_anomaly_data
        is_trained = loaded_is_trained
        trained_on = loaded_trained_on

        on_load_finished()

        select_period_type_combo_box.setCurrentIndex(0)

        station_id = get_station_id()

        reset_observation(select_diagram_observation_vertical_layout)
        min_temperature_combo_box, max_temperature_combo_box, average_temperature_combo_box = \
            set_observation(
                select_diagram_observation_vertical_layout,
                lambda state: update_diagram_override(),
                stations_info[station_id]["need_min"],
                stations_info[station_id]["need_max"],
                stations_info[station_id]["need_average"])

        select_observation_for_anomaly_combo_box.clear()
        select_observation_for_anomaly_combo_box.addItem("(None)")

        if stations_info[station_id]["is_trained"]:
            select_observation_for_anomaly_combo_box.setEnabled(True)

            if stations_info[station_id]["is_max_trained"]:
                select_observation_for_anomaly_combo_box.addItem("Max temperature")
            if stations_info[station_id]["is_average_trained"]:
                select_observation_for_anomaly_combo_box.addItem("Average temperature")
            if stations_info[station_id]["is_min_trained"]:
                select_observation_for_anomaly_combo_box.addItem("Min temperature")
        else:
            select_observation_for_anomaly_combo_box.setEnabled(False)

    def on_error_to_event_list(message: str) -> None:
        event_list.append(lambda: on_error(message))

    def on_status_changed_to_event_list(status: str) -> None:
        event_list.append(lambda: on_status_changed(status))

    def on_finished_to_event_list(loaded_data: dict,
                                  loaded_anomaly_data: dict,
                                  loaded_is_trained: bool,
                                  loaded_trained_on: (bool, bool, bool)) -> None:
        event_list.append(lambda: on_finished(loaded_data, loaded_anomaly_data, loaded_is_trained, loaded_trained_on))

    def update_diagram() -> None:
        pass

    def update_diagram_override() -> None:
        update_diagram()

    def load(station_id: str) -> None:
        on_load_started()

        thread = Worker(
            get_stations_data_from_file,
            stations_info,
            station_id,
            on_error_to_event_list,
            on_status_changed_to_event_list,
            on_finished_to_event_list)
        thread_pool.start(thread)

    def on_station_id_combo_box_selected(index: int) -> None:
        nonlocal last_station_id
        if is_updating_station_id_combo_box:
            return

        if index <= 0:
            select_period_type_combo_box.setCurrentIndex(0)
            reset_observation(select_diagram_observation_vertical_layout)
            set_busy_by("", is_diagram=True)
            last_station_id = ""
        else:
            station_id = get_station_id()
            if station_id != last_station_id:
                set_busy_by(station_id, is_diagram=True)
                load(station_id)
                last_station_id = station_id

    def on_custom_data_window_closed():
        nonlocal is_custom_data_window_open
        is_custom_data_window_open = False

        custom_data_push_button.setEnabled(True)

    def on_custom_data_push_button_clicked():
        nonlocal custom_data_window, custom_data_ui, is_custom_data_window_open
        custom_data_window = WindowWithCloseListener(on_custom_data_window_closed)
        custom_data_ui = Ui_custom_data_window()
        custom_data_ui.setupUi(custom_data_window)
        custom_data_window.show()

        is_custom_data_window_open = True
        custom_data_push_button.setEnabled(False)

        if not is_trained:
            custom_data_window.setEnabled(False)

    def on_extract_finished() -> None:
        update_station_id_combo_box()

    def busy_listener() -> None:
        update_station_id_combo_box()

    def get_data() -> dict:
        return data

    def is_trained_model() -> bool:
        return is_trained

    def get_anomaly_data() -> dict:
        return anomaly_data

    def get_trained_on() -> (bool, bool, bool):
        return trained_on

    def need_show_min() -> bool:
        if min_temperature_combo_box is not None:
            # noinspection PyUnresolvedReferences
            return min_temperature_combo_box.isChecked()
        return False

    def need_show_max() -> bool:
        if max_temperature_combo_box is not None:
            # noinspection PyUnresolvedReferences
            return max_temperature_combo_box.isChecked()
        return False

    def need_show_average() -> bool:
        if average_temperature_combo_box is not None:
            # noinspection PyUnresolvedReferences
            return average_temperature_combo_box.isChecked()
        return False

    def set_show_min(is_checked: bool) -> None:
        if min_temperature_combo_box is not None:
            # noinspection PyUnresolvedReferences
            min_temperature_combo_box.setChecked(is_checked)

    def set_show_max(is_checked: bool) -> None:
        if max_temperature_combo_box is not None:
            # noinspection PyUnresolvedReferences
            max_temperature_combo_box.setChecked(is_checked)

    def set_show_average(is_checked: bool) -> None:
        if average_temperature_combo_box is not None:
            # noinspection PyUnresolvedReferences
            average_temperature_combo_box.setChecked(is_checked)

    update_station_id_combo_box()

    select_station_id_for_diagram_combo_box.currentIndexChanged.connect(on_station_id_combo_box_selected)
    custom_data_push_button.clicked.connect(on_custom_data_push_button_clicked)

    update_diagram = gui_init_diagrams_data_handle(
        ui,
        main_window,
        get_data,
        get_anomaly_data,
        is_trained_model,
        get_trained_on,
        need_show_min,
        need_show_max,
        need_show_average,
        set_show_min,
        set_show_max,
        set_show_average)

    return busy_listener, on_extract_finished
