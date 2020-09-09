import threading
import time
from typing import Callable

from Backend.TrainModel import train_single_file
from handle_data.data_management import create_directory_for_trained_model, \
    get_file_path_for_single_file_station_data


def train_model(station_id: str,
                on_error: Callable[[str], None],
                on_status_changed: Callable[[str], None],
                on_finished: Callable[[bool, bool, bool], None],
                need_min: bool,
                need_max: bool,
                need_average: bool) -> None:
    path_to_data = get_file_path_for_single_file_station_data(station_id)
    path_to_save = create_directory_for_trained_model()

    is_training_lock = threading.Lock()
    is_training = True
    statuses = ["Training", "Training.", "Training..", "Training..."]

    def status_update():
        current_index = 0

        is_training_lock.acquire()
        while is_training:
            is_training_lock.release()

            on_status_changed(statuses[current_index])

            current_index += 1
            if current_index == len(statuses):
                current_index = 0

            time.sleep(0.5)

            is_training_lock.acquire()

        is_training_lock.release()

    status_updater = threading.Thread(target=status_update)
    status_updater.start()

    # noinspection PyBroadException
    try:
        train_single_file(station_id, path_to_data, (need_min, need_max, need_average), path_to_save)
    except:
        is_training_lock.acquire()
        is_training = False
        is_training_lock.release()

        status_updater.join()

        on_error("Train crashed")
        return

    is_training_lock.acquire()
    is_training = False
    is_training_lock.release()

    status_updater.join()

    on_status_changed("Finished")
    on_finished(need_min, need_max, need_average)
