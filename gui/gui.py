import sys

import matplotlib
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QMessageBox

from gui.main_window import Ui_main_window
from gui.worker import Worker
from handle_data.handle_data import handle_data_to_files

matplotlib.use('Qt5Agg')


def main_ui():
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()

    ui = Ui_main_window()
    ui.setupUi(main_window)

    station_id_line_edit = ui.station_id_line_edit
    min_max_temperature_check_box = ui.min_max_temperature_check_box
    precipitation_check_box = ui.precipitation_check_box

    get_data_push_button = ui.get_data_push_button
    status_value_label = ui.status_value_label

    thread_pool = QThreadPool()

    event_list = []

    def run_event():
        if len(event_list) > 0:
            function = event_list[0]
            function()

            event_list.pop(0)

    event_list_runner = QtCore.QTimer()
    event_list_runner.timeout.connect(run_event)
    event_list_runner.start(10)

    def on_error(message):
        QMessageBox.warning(main_window, 'Warning', message, QMessageBox.Ok)

    def on_status_changed(status):
        status_value_label.setText(status)

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
            on_status_changed)
        thread_pool.start(thread)

    get_data_push_button.clicked.connect(on_click)

    main_window.show()
    sys.exit(app.exec_())
