import sys

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QMessageBox

from gui.gui_available_observaion import reset_observation, set_observation
from gui.gui_diagrams import show_diagram_by_month, show_diagram_by_several_months, show_diagram_by_several_all_data, \
    remove_diagrams
from gui.main_window import Ui_main_window
from gui.worker import Worker
from handle_data.data_management import get_stations_info_from_json, init_files_and_directories_if_not_exist, \
    get_stations_data_from_file
from handle_data.handle_data import handle_data_to_files


def main_ui():
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()

    ui = Ui_main_window()
    ui.setupUi(main_window)

    station_id_line_edit = ui.station_id_line_edit
    extract_data_push_button = ui.extract_data_push_button
    load_from_files_push_button = ui.load_from_files_push_button
    data_extraction_status_value_label = ui.data_extraction_status_value_label
    select_diagram_observation_vertical_layout = ui.select_diagram_observation_vertical_layout
    diagram_frame = ui.diagram_frame
    select_period_type_combo_box = ui.select_period_type_combo_box
    select_period_combo_box = ui.select_period_combo_box
    select_training_observation_vertical_layout = ui.select_training_observation_vertical_layout

    diagram_vertical_layout = ui.diagram_vertical_layout

    init_files_and_directories_if_not_exist()
    stations_info = get_stations_info_from_json()

    thread_pool = QThreadPool()
    event_list = []
    data = {}

    # Will be used in the future
    # noinspection PyUnusedLocal
    min_temperature_training_combo_box = None
    # noinspection PyUnusedLocal
    max_temperature_training_combo_box = None
    # noinspection PyUnusedLocal
    average_temperature_training_combo_box = None

    min_temperature_diagram_combo_box = None
    max_temperature_diagram_combo_box = None
    average_temperature_diagram_combo_box = None
    contain_min_temperature = False
    contain_max_temperature = False
    contain_average_temperature = False
    current_data_list = []
    current_period_type_index = 0
    current_period_index = 0

    def run_event():
        if len(event_list) > 0:
            function = event_list[0]
            function()

            event_list.pop(0)

    event_list_runner = QtCore.QTimer()
    # noinspection PyUnresolvedReferences
    event_list_runner.timeout.connect(run_event)
    event_list_runner.start(10)

    def is_current_station_id_in_stations_info():
        station_id = station_id_line_edit.text()
        return station_id in stations_info

    def update_station_id_push_buttons():
        if is_current_station_id_in_stations_info():
            extract_data_push_button.setText("Update to latest")
            load_from_files_push_button.setEnabled(True)
        else:
            extract_data_push_button.setText("Extract data")
            load_from_files_push_button.setEnabled(False)

    def on_error(message):
        QMessageBox.warning(main_window, 'Warning', message, QMessageBox.Ok)

    def on_status_changed(status):
        data_extraction_status_value_label.setText(status)

    def diagram_combo_box_update_diagram():
        pass

    def on_finished(extracted_data, contain_min, contain_max, contain_average):
        nonlocal data, contain_min_temperature, contain_max_temperature, contain_average_temperature, \
            min_temperature_training_combo_box, max_temperature_training_combo_box,\
            average_temperature_training_combo_box, min_temperature_diagram_combo_box,\
            max_temperature_diagram_combo_box, average_temperature_diagram_combo_box
        data = extracted_data
        contain_min_temperature = contain_min
        contain_max_temperature = contain_max
        contain_average_temperature = contain_average

        reset_observation(select_training_observation_vertical_layout)
        min_temperature_training_combo_box, max_temperature_training_combo_box,\
            average_temperature_training_combo_box =\
            set_observation(
                select_training_observation_vertical_layout,
                lambda state: None,
                contain_min_temperature,
                contain_max_temperature,
                contain_average_temperature)

        reset_observation(select_diagram_observation_vertical_layout)
        min_temperature_diagram_combo_box, max_temperature_diagram_combo_box,\
            average_temperature_diagram_combo_box =\
            set_observation(
                select_diagram_observation_vertical_layout,
                lambda state: diagram_combo_box_update_diagram(),
                contain_min_temperature,
                contain_max_temperature,
                contain_average_temperature)

        diagram_frame.setEnabled(True)

    def on_extract_data_push_button_click():
        diagram_frame.setEnabled(False)
        reset_observation(select_training_observation_vertical_layout)
        reset_observation(select_diagram_observation_vertical_layout)
        
        station_id = station_id_line_edit.text()
        thread = Worker(
            handle_data_to_files,
            stations_info,
            station_id,
            event_list,
            on_error,
            on_status_changed,
            on_finished)
        thread_pool.start(thread)

    def on_load_data_from_files_push_button_click():
        station_id = station_id_line_edit.text()
        loaded_data = get_stations_data_from_file(station_id)
        on_finished(
            loaded_data,
            stations_info[station_id]['need_min'],
            stations_info[station_id]['need_max'],
            stations_info[station_id]['need_average'])

    def reset_period_combo_box():
        select_period_combo_box.clear()
        select_period_combo_box.addItem("(None)")

        current_data_list.clear()
        current_data_list.append(None)

    def fill_periods_by_months():
        for key in data:
            select_period_combo_box.addItem(key + "m")
            current_data_list.append(data[key])

    def split_data_by_years_and_months():
        years_and_months_data = {}

        for key in data:
            year = key[:4]
            month = key[-2:]

            if year in years_and_months_data:
                years_and_months_data[year][month] = (data[key], year)
            else:
                years_and_months_data[year] = {month: (data[key], year)}
        return years_and_months_data

    def get_seasons(years_and_months_data, seasons_data):
        for key in years_and_months_data:
            current_data = years_and_months_data[key]

            last_winter = {}
            last_winter_name = str(int(key) - 1) + "-" + key + "_winter"
            if last_winter_name in seasons_data:
                last_winter = seasons_data[last_winter_name]

            if "01" in current_data:
                last_winter["01"] = current_data["01"]
            if "02" in current_data:
                last_winter["02"] = current_data["02"]

            if len(last_winter) > 0:
                seasons_data[last_winter_name] = last_winter

            spring = {}

            if "03" in current_data:
                spring["03"] = current_data["03"]
            if "04" in current_data:
                spring["04"] = current_data["04"]
            if "05" in current_data:
                spring["05"] = current_data["05"]

            if len(spring) > 0:
                seasons_data[key + "_spring"] = spring

            summer = {}

            if "06" in current_data:
                summer["06"] = current_data["06"]
            if "07" in current_data:
                summer["07"] = current_data["07"]
            if "08" in current_data:
                summer["08"] = current_data["08"]

            if len(summer) > 0:
                seasons_data[key + "_summer"] = summer

            fall = {}

            if "09" in current_data:
                fall["09"] = current_data["09"]
            if "10" in current_data:
                fall["10"] = current_data["10"]
            if "11" in current_data:
                fall["11"] = current_data["11"]

            if len(fall) > 0:
                seasons_data[key + "_fall"] = fall

            winter = {}
            winter_name = key + "-" + str(int(key) + 1) + "_winter"

            if "12" in current_data:
                winter["12"] = current_data["12"]

            if len(winter) > 0:
                seasons_data[winter_name] = winter

    def fill_periods_by_season():
        years_and_months_data = split_data_by_years_and_months()
        seasons_data = {}
        get_seasons(years_and_months_data, seasons_data)

        for key in seasons_data:
            select_period_combo_box.addItem(key)
            current_data_list.append(seasons_data[key])

    def fill_periods_by_years():
        years_and_months_data = split_data_by_years_and_months()

        for key in years_and_months_data:
            select_period_combo_box.addItem(key + "y")
            current_data_list.append(years_and_months_data[key])

    def fill_periods_by_all_data():
        years_and_months_data = split_data_by_years_and_months()

        select_period_combo_box.addItem("All")
        current_data_list.append(years_and_months_data)

    def update_diagram():
        remove_diagrams(diagram_vertical_layout)

        need_min_temperature = False
        if min_temperature_diagram_combo_box is not None:
            # noinspection PyUnresolvedReferences
            need_min_temperature = min_temperature_diagram_combo_box.isChecked()

        need_max_temperature = False
        if max_temperature_diagram_combo_box is not None:
            # noinspection PyUnresolvedReferences
            need_max_temperature = max_temperature_diagram_combo_box.isChecked()

        need_average_temperature = False
        if average_temperature_diagram_combo_box is not None:
            # noinspection PyUnresolvedReferences
            need_average_temperature = average_temperature_diagram_combo_box.isChecked()

        if not need_min_temperature and not need_max_temperature and not need_average_temperature:
            return

        current_data = (main_window, diagram_vertical_layout, {}, need_min_temperature, need_max_temperature,
                        need_average_temperature)
        if current_period_index > 0:
            current_data = (main_window, diagram_vertical_layout, current_data_list[current_period_index],
                            need_min_temperature, need_max_temperature, need_average_temperature)

        if current_period_type_index == 1 and current_period_index > 0:
            show_diagram_by_month(*current_data)

        elif current_period_type_index == 2 and current_period_index > 0:
            show_diagram_by_several_months(*current_data)

        elif current_period_type_index == 3 and current_period_index > 0:
            show_diagram_by_several_months(*current_data)

        elif current_period_type_index == 4 and current_period_index > 0:
            show_diagram_by_several_all_data(*current_data)

    def on_period_type_combo_box_index_changed(index):
        nonlocal current_period_type_index
        current_period_type_index = index

        reset_period_combo_box()

        if index == 1:
            fill_periods_by_months()
        elif index == 2:
            fill_periods_by_season()
        elif index == 3:
            fill_periods_by_years()
        elif index == 4:
            fill_periods_by_all_data()

    def on_period_combo_box_index_changed(index):
        nonlocal current_period_index
        current_period_index = index

        update_diagram()

    diagram_combo_box_update_diagram = update_diagram

    extract_data_push_button.clicked.connect(on_extract_data_push_button_click)
    load_from_files_push_button.clicked.connect(on_load_data_from_files_push_button_click)

    select_period_type_combo_box.currentIndexChanged.connect(on_period_type_combo_box_index_changed)
    select_period_combo_box.currentIndexChanged.connect(on_period_combo_box_index_changed)

    station_id_line_edit.textChanged.connect(lambda text: update_station_id_push_buttons())

    update_station_id_push_buttons()

    main_window.show()
    sys.exit(app.exec_())
