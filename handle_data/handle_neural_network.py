import _thread
import time
from typing import Callable

from Backend.TrainModel import train
from handle_data.data_management import create_directory_for_station, create_directory_for_trained_model


def train_model(station_id: str,
                on_error: Callable[[str], None],
                on_status_changed: Callable[[str], None],
                on_finished: Callable[[bool, bool, bool], None],
                need_min: bool,
                need_max: bool,
                need_average: bool) -> None:
    path_to_data = create_directory_for_station(station_id)
    path_to_save = create_directory_for_trained_model()

    is_training = True
    current_index = 0
    statuses = ["Training", "Training.", "Training..", "Training..."]

    def status_update():
        nonlocal current_index
        while is_training:
            on_status_changed(statuses[current_index])
            time.sleep(0.5)
            current_index += 1
            if current_index == len(statuses):
                current_index = 0

    _thread.start_new_thread(status_update, ())

    # noinspection PyBroadException
    try:
        train(station_id, path_to_data, (need_min, need_max, need_average), path_to_save)
    except:
        is_training = False

        on_error("Train crashed")
        return

    is_training = False

    on_status_changed("Finished")
    on_finished(need_min, need_max, need_average)
