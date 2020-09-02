import sys

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThreadPool

from gui.gui_data_extraction import gui_init_data_extraction
from gui.gui_diagrams import gui_init_diagrams
from gui.gui_train import gui_init_train
from gui.main_window import Ui_main_window
from handle_data.data_management import get_stations_info_from_json, init_files_and_directories_if_not_exist


def main_ui() -> None:
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()

    ui = Ui_main_window()
    ui.setupUi(main_window)

    init_files_and_directories_if_not_exist()
    stations_info = get_stations_info_from_json()

    thread_pool = QThreadPool()
    event_list = []

    def run_event() -> None:
        if len(event_list) > 0:
            function = event_list[0]
            function()

            event_list.pop(0)

    event_list_runner = QtCore.QTimer()
    # noinspection PyUnresolvedReferences
    event_list_runner.timeout.connect(run_event)
    event_list_runner.start(10)

    busy_by_data_extract = ""
    busy_by_train = ""
    busy_by_diagram = ""

    busy_listeners = []
    on_extract_finished = []

    def set_busy_by(station_id: str, is_data_extract=False, is_train=False, is_diagram=False) -> None:
        nonlocal busy_by_data_extract, busy_by_train, busy_by_diagram

        if is_data_extract:
            busy_by_data_extract = station_id
        if is_train:
            busy_by_train = station_id
        if is_diagram:
            busy_by_diagram = station_id

        [busy_listener() for busy_listener in busy_listeners]

    def is_busy_by(station_id: str, is_data_extract=False, is_train=False, is_diagram=False) -> bool:
        if not is_data_extract and busy_by_data_extract != "" and busy_by_data_extract == station_id:
            return True
        if not is_train and busy_by_train != "" and busy_by_train == station_id:
            return True
        if not is_diagram and busy_by_diagram != "" and busy_by_diagram == station_id:
            return True
        return False

    busy_listener_by_train, on_extract_finished_for_train =\
        gui_init_train(
            ui,
            main_window,
            event_list,
            thread_pool,
            stations_info,
            set_busy_by,
            is_busy_by)

    busy_listeners.append(busy_listener_by_train)
    on_extract_finished.append(on_extract_finished_for_train)

    busy_listener_by_diagrams, on_extract_finished_for_diagrams =\
        gui_init_diagrams(
            ui,
            main_window,
            event_list,
            thread_pool,
            stations_info,
            set_busy_by,
            is_busy_by)

    busy_listeners.append(busy_listener_by_diagrams)
    on_extract_finished.append(on_extract_finished_for_diagrams)

    busy_listener_by_data_extract =\
        gui_init_data_extraction(
            ui,
            main_window,
            event_list,
            thread_pool,
            stations_info,
            set_busy_by,
            is_busy_by,
            on_extract_finished)

    busy_listeners.append(busy_listener_by_data_extract)

    main_window.show()
    sys.exit(app.exec_())
