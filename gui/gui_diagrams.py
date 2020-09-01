from typing import Callable

from PyQt5 import QtWidgets

from gui.gui_available_observaion import set_observation, reset_observation
from gui.gui_diagrams_data_handle import gui_init_diagrams_data_handle
from gui.main_window import Ui_main_window
from handle_data.data_management import get_stations_data_from_file


def gui_init_diagrams(ui: Ui_main_window,
                      main_window: QtWidgets.QMainWindow,
                      stations_info: dict,
                      set_busy_by: Callable,
                      is_busy_by: Callable) -> (Callable, Callable):
    select_station_id_for_diagram_combo_box = ui.select_station_id_for_diagram_combo_box
    select_diagram_observation_vertical_layout = ui.select_diagram_observation_vertical_layout
    select_period_type_combo_box = ui.select_period_type_combo_box

    data = {}
    last_station_id = ""

    min_temperature_combo_box = None
    max_temperature_combo_box = None
    average_temperature_combo_box = None

    is_updating_station_id_combo_box = False

    def get_station_id() -> str:
        return select_station_id_for_diagram_combo_box.currentText()

    def update_station_id_combo_box():
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

    def update_diagram():
        pass

    def update_diagram_override():
        update_diagram()

    def load(station_id: str):
        nonlocal data, min_temperature_combo_box, max_temperature_combo_box, average_temperature_combo_box

        data = get_stations_data_from_file(station_id)

        select_period_type_combo_box.setCurrentIndex(0)

        reset_observation(select_diagram_observation_vertical_layout)
        min_temperature_combo_box, max_temperature_combo_box, average_temperature_combo_box = \
            set_observation(
                select_diagram_observation_vertical_layout,
                lambda state: update_diagram_override(),
                stations_info[station_id]["need_min"],
                stations_info[station_id]["need_max"],
                stations_info[station_id]["need_average"])

    def on_station_id_combo_box_selected(index: int):
        if is_updating_station_id_combo_box:
            return

        if index <= 0:
            select_period_type_combo_box.setCurrentIndex(0)
            reset_observation(select_diagram_observation_vertical_layout)
            set_busy_by("", is_diagram=True)
        else:
            station_id = get_station_id()
            if station_id != last_station_id:
                set_busy_by(station_id, is_diagram=True)
                load(station_id)

    def on_extract_finished():
        update_station_id_combo_box()

    def busy_listener():
        update_station_id_combo_box()

    def get_data():
        return data

    def need_show_min():
        if min_temperature_combo_box is not None:
            # noinspection PyUnresolvedReferences
            return min_temperature_combo_box.isChecked()
        return False

    def need_show_max():
        if max_temperature_combo_box is not None:
            # noinspection PyUnresolvedReferences
            return max_temperature_combo_box.isChecked()
        return False

    def need_show_average():
        if average_temperature_combo_box is not None:
            # noinspection PyUnresolvedReferences
            return average_temperature_combo_box.isChecked()
        return False

    update_station_id_combo_box()

    select_station_id_for_diagram_combo_box.currentIndexChanged.connect(on_station_id_combo_box_selected)

    update_diagram = gui_init_diagrams_data_handle(
        ui,
        main_window,
        get_data,
        need_show_min,
        need_show_max,
        need_show_average)

    return busy_listener, on_extract_finished
