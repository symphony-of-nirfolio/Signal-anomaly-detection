import queue
import sys

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThreadPool

from audio.audio_manager import audio_manager
from gui.gui_creditor import gui_init_creditor
from gui.gui_data_extraction import gui_init_data_extraction
from gui.gui_diagrams import gui_init_diagrams
from gui.gui_settings import gui_init_settings
from gui.gui_train import gui_init_train
from gui.gui_tutorial import gui_init_usa_tutorial, gui_init_all_other_tutorial
from gui.main_window import Ui_main_window
from gui.window_with_close_listener import WindowWithCloseListener
from handle_data.data_management import get_stations_info_from_json, init_files_and_directories_if_not_exist


def main_ui() -> None:
    app = QtWidgets.QApplication(sys.argv)

    close_listeners = []

    def run_listeners():
        [listener() for listener in close_listeners]

    main_window = WindowWithCloseListener(run_listeners)

    ui = Ui_main_window()
    ui.setupUi(main_window)

    init_files_and_directories_if_not_exist()
    stations_info = get_stations_info_from_json()
    play_finish_notification, play_error_notification, get_sound_effect_volume, get_music_volume,\
        set_sound_effect_volume, set_music_volume, audio_manager_close_listener = audio_manager()
    close_listeners.append(audio_manager_close_listener)

    thread_pool = QThreadPool()
    event_list = queue.Queue(maxsize=16)

    def run_event() -> None:
        if not event_list.empty():
            function = event_list.get()
            function()

            event_list.task_done()

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

    def is_busy_by(station_id: str, is_data_extract=False, is_train=False, is_diagram=False) -> (bool, str):
        if not is_data_extract and busy_by_data_extract != "" and busy_by_data_extract == station_id:
            return True, "Station is busy by data extraction"
        if not is_train and busy_by_train != "" and busy_by_train == station_id:
            return True, "Station is busy by training"
        if not is_diagram and busy_by_diagram != "" and busy_by_diagram == station_id:
            return True, "Station is busy by diagrams"
        return False, ""

    busy_listener_by_train, on_extract_finished_for_train =\
        gui_init_train(
            ui,
            main_window,
            event_list,
            thread_pool,
            stations_info,
            set_busy_by,
            is_busy_by,
            play_finish_notification,
            play_error_notification)

    busy_listeners.append(busy_listener_by_train)
    on_extract_finished.append(on_extract_finished_for_train)

    busy_listener_by_diagrams, on_extract_finished_for_diagrams, diagram_close_listener =\
        gui_init_diagrams(
            ui,
            main_window,
            event_list,
            thread_pool,
            stations_info,
            set_busy_by,
            is_busy_by,
            play_finish_notification,
            play_error_notification)

    busy_listeners.append(busy_listener_by_diagrams)
    on_extract_finished.append(on_extract_finished_for_diagrams)
    close_listeners.append(diagram_close_listener)

    busy_listener_by_data_extract =\
        gui_init_data_extraction(
            ui,
            main_window,
            event_list,
            thread_pool,
            stations_info,
            set_busy_by,
            is_busy_by,
            on_extract_finished,
            play_finish_notification,
            play_error_notification)

    busy_listeners.append(busy_listener_by_data_extract)

    creditor_close_listener = gui_init_creditor(ui)
    close_listeners.append(creditor_close_listener)

    usa_tutorial_close_listener = gui_init_usa_tutorial(ui)
    close_listeners.append(usa_tutorial_close_listener)

    all_other_tutorial_close_listener = gui_init_all_other_tutorial(ui)
    close_listeners.append(all_other_tutorial_close_listener)

    settings_close_listener = gui_init_settings(ui,
                                                get_sound_effect_volume,
                                                get_music_volume,
                                                set_sound_effect_volume,
                                                set_music_volume)
    close_listeners.append(settings_close_listener)

    main_window.show()
    sys.exit(app.exec_())
