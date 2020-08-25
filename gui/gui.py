import sys

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QMessageBox

from gui.gui_diagrams import show_min_max_diagram, show_precipitation_diagram, remove_diagrams
from gui.main_window import Ui_main_window
from gui.worker import Worker
from handle_data.handle_data import handle_data_to_files


def main_ui():
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()

    ui = Ui_main_window()
    ui.setupUi(main_window)

    station_id_line_edit = ui.station_id_line_edit
    min_max_temperature_check_box = ui.min_max_temperature_check_box
    precipitation_check_box = ui.precipitation_check_box

    extract_data_push_button = ui.extract_data_push_button
    data_extraction_status_value_label = ui.data_extraction_status_value_label
    diagram_frame = ui.diagram_frame
    select_period_type_combo_box = ui.select_period_type_combo_box
    select_period_combo_box = ui.select_period_combo_box
    select_observation_combo_box = ui.select_observation_combo_box

    diagram_vertical_layout = ui.diagram_vertical_layout

    thread_pool = QThreadPool()
    event_list = []
    data = {}
    current_data_list = []
    current_period_type_index = 0
    current_observation_index = 0
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

    def on_error(message):
        QMessageBox.warning(main_window, 'Warning', message, QMessageBox.Ok)

    def on_status_changed(status):
        data_extraction_status_value_label.setText(status)

    def on_finished(extracted_data):
        nonlocal data
        data = extracted_data

        diagram_frame.setEnabled(True)
        select_observation_combo_box.clear()
        select_observation_combo_box.addItem("(None)")

        if min_max_temperature_check_box.isChecked():
            select_observation_combo_box.addItem(min_max_temperature_check_box.text())
        if precipitation_check_box.isChecked():
            select_observation_combo_box.addItem(precipitation_check_box.text())

    def on_click():
        station_id = station_id_line_edit.text()
        need_min_max_temperature = min_max_temperature_check_box.isChecked()
        need_precipitation = precipitation_check_box.isChecked()
        thread = Worker(
            handle_data_to_files,
            station_id,
            need_min_max_temperature,
            need_precipitation,
            event_list,
            on_error,
            on_status_changed,
            on_finished)
        thread_pool.start(thread)

    def reset_period_combo_box():
        select_period_combo_box.clear()
        select_period_combo_box.addItem("(None)")

        current_data_list.clear()
        current_data_list.append(None)

    def fill_periods_by_months():
        for key in data:
            select_period_combo_box.addItem(key + "m")
            current_data_list.append(data[key])

    def update_diagram():
        remove_diagrams(diagram_vertical_layout)

        if current_observation_index == 1 and current_period_type_index == 1 and current_period_index > 0:
            show_min_max_diagram(main_window, diagram_vertical_layout, current_data_list[current_period_index])
        elif current_observation_index == 2 and current_period_type_index == 1 and current_period_index > 0:
            show_precipitation_diagram(main_window, diagram_vertical_layout, current_data_list[current_period_index])

    def on_period_type_combo_box_index_changed(index):
        nonlocal current_period_type_index
        current_period_type_index = index

        reset_period_combo_box()

        if index == 1:
            fill_periods_by_months()

    def on_period_combo_box_index_changed(index):
        nonlocal current_period_index
        current_period_index = index

        update_diagram()

    def on_observation_combo_box_index_changed(index):
        nonlocal current_observation_index
        current_observation_index = index

        update_diagram()

    extract_data_push_button.clicked.connect(on_click)

    select_period_type_combo_box.currentIndexChanged.connect(on_period_type_combo_box_index_changed)
    select_period_combo_box.currentIndexChanged.connect(on_period_combo_box_index_changed)
    select_observation_combo_box.currentIndexChanged.connect(on_observation_combo_box_index_changed)

    main_window.show()
    sys.exit(app.exec_())
