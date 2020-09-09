import os
import json
import threading
import time
from typing import Callable, Tuple

import numpy as np

from Backend.PredictModel import Prediction
from handle_data.info import Info, InfoJSONEncoder

common_path = "data"
stations_info_path = common_path + "/common_data.json"
audio_info_path = common_path + "/audio_data.json"

stations_data_path = common_path + "/stations"
model_data_path = common_path + "/models"


def init_files_and_directories_if_not_exist() -> None:
    if not os.path.exists(stations_info_path):
        os.mkdir(common_path)
        with open(stations_info_path, 'w') as stations_info_file:
            json.dump({}, stations_info_file)

    if not os.path.exists(audio_info_path):
        with open(audio_info_path, 'w') as audio_info_file:
            json.dump({"sound_effect_volume": 1.0, "music_volume": 0.4}, audio_info_file)

    if not os.path.exists(stations_data_path):
        os.mkdir(stations_data_path)


def get_stations_info_from_json() -> dict:
    with open(stations_info_path) as stations_info_file:
        data = json.load(stations_info_file)
        return data


def write_stations_info_to_json(stations_info: dict) -> None:
    with open(stations_info_path, 'w') as stations_info_file:
        json.dump(stations_info, stations_info_file)


def get_audio_info_from_json() -> dict:
    with open(audio_info_path) as audio_info_file:
        audio_info = json.load(audio_info_file)
        return audio_info


def write_audio_info_to_json(audio_info: dict) -> None:
    with open(audio_info_path, 'w') as audio_info_file:
        json.dump(audio_info, audio_info_file)


def get_directory_path_for_single_file_station_data(station_id: str) -> str:
    return stations_data_path + "/" + station_id


def get_file_path_for_single_file_station_data(station_id: str) -> str:
    return stations_data_path + "/" + station_id + "/data.json"


def create_directory_for_single_file_station_and_return_file_path(station_id: str) -> str:
    path = get_directory_path_for_single_file_station_data(station_id)
    if not os.path.exists(path):
        os.makedirs(path)
    return get_file_path_for_single_file_station_data(station_id)


def get_directory_path_for_trained_model() -> str:
    return model_data_path


def create_directory_for_trained_model() -> str:
    path = get_directory_path_for_trained_model()
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def _get_file_path_for_cashed_file_anomaly_data(station_id: str) -> str:
    return stations_data_path + "/" + station_id + "/cash_anomaly_data.json"


def _get_season_by_month(month: int):
    if month == 12 or month == 1 or month == 2:
        return 0
    if 3 <= month <= 5:
        return 1
    if 6 <= month <= 8:
        return 2
    if 9 <= month <= 11:
        return 3


def _save_to_json_file(path: str, data: dict) -> None:
    with open(path, 'w') as data_file:
        json.dump(data, data_file, cls=InfoJSONEncoder)


def _load_from_json_file(path: str) -> dict:
    with open(path) as data_file:
        data = json.load(data_file)
        return data


def _convert_to_data(json_data: dict) -> dict:
    data = {}
    for key in json_data:
        data[key] = list([Info.from_dict(info) for info in json_data[key]])

    return data


def _get_value_list_from_data(data: list, anomaly_text: str) -> np.array:
    value_list = []

    for info in data:
        if anomaly_text == "min":
            value_list.append(info.min)
        if anomaly_text == "max":
            value_list.append(info.max)
        if anomaly_text == "average":
            value_list.append(info.average)

    return np.array(value_list)


def _info_list_to_value_list(data: list) -> list:
    value_list = []

    for info in data:
        value_list.append(info.day)
        value_list.append(info.min)
        value_list.append(info.max)
        value_list.append(info.average)

    return value_list


def _info_dict_to_value_dict(data: dict) -> dict:
    value_data = {}

    for key in data:
        value_data[key] = _info_list_to_value_list(data[key])

    return value_data


def save_data_to_file(data: dict, path: str) -> None:
    converted_data = _info_dict_to_value_dict(data)

    _save_to_json_file(path, converted_data)


def _value_list_to_info_list(value_list: list) -> list:
    data = []

    for i in range(len(value_list) // 4):
        info = Info()
        info.day = value_list[i * 4 + 0]
        info.min = value_list[i * 4 + 1]
        info.max = value_list[i * 4 + 2]
        info.average = value_list[i * 4 + 3]
        data.append(info)

    return data


def load_data_from_file(path: str) -> dict:
    data = _load_from_json_file(path)

    converted_data = {}

    for key in data:
        converted_data[key] = _value_list_to_info_list(data[key])

    return converted_data


def get_anomaly_from_data(data: list, anomaly_text: str, season: int) -> dict:
    anomaly_data = {}
    prediction = Prediction.get_instance()

    col_index = 0
    if anomaly_text == "min":
        col_index = 0
    if anomaly_text == "max":
        col_index = 1
    if anomaly_text == "average":
        col_index = 2

    value_list = _get_value_list_from_data(data, anomaly_text)
    anomaly_array, zone = prediction.get_result(value_list, col_index, season)
    anomaly_data[anomaly_text] = (anomaly_array.tolist(), zone)

    return anomaly_data


def _calculate_anomaly_data(data: list,
                            key: str,
                            month: int,
                            anomaly_data: dict,
                            trained_on: (bool, bool, bool),
                            prediction: Prediction) -> None:
    anomaly_data[key] = {}
    if trained_on[0]:
        value_list = _get_value_list_from_data(data, "min")
        anomaly_array, zone = prediction.get_result(value_list, 0, _get_season_by_month(month))
        anomaly_data[key]["min"] = (anomaly_array.tolist(), zone)
    if trained_on[1]:
        value_list = _get_value_list_from_data(data, "max")
        anomaly_array, zone = prediction.get_result(value_list, 1, _get_season_by_month(month))
        anomaly_data[key]["max"] = (anomaly_array.tolist(), zone)
    if trained_on[2]:
        value_list = _get_value_list_from_data(data, "average")
        anomaly_array, zone = prediction.get_result(value_list, 2, _get_season_by_month(month))
        anomaly_data[key]["average"] = (anomaly_array.tolist(), zone)


def _try_get_stations_data_from_file(stations_info: dict,
                                     station_id: str,
                                     on_status_changed: Callable[[str], None],
                                     on_finished:
                                     Callable[[dict, dict, bool, Tuple[bool, bool, bool]], None]) -> None:
    model_path = get_directory_path_for_trained_model()

    need_to_load_anomaly_data = False

    prediction = Prediction.get_instance()
    is_trained = False
    trained_on = (False, False, False)
    if stations_info[station_id]["is_trained"]:
        prediction.setup_model(model_path, station_id)
        is_trained = True
        need_to_load_anomaly_data = True
        trained_on = (stations_info[station_id]["is_min_trained"],
                      stations_info[station_id]["is_max_trained"],
                      stations_info[station_id]["is_average_trained"])

    data = load_data_from_file(get_file_path_for_single_file_station_data(station_id))
    anomaly_data = {}

    if stations_info[station_id]["is_cashed_anomaly_data"]:
        anomaly_data = _load_from_json_file(_get_file_path_for_cashed_file_anomaly_data(station_id))
        need_to_load_anomaly_data = False

    if need_to_load_anomaly_data:
        value_data = _info_dict_to_value_dict(data)

        raw_anomaly_data = prediction.get_result_multiple(value_data, trained_on)

        for key in raw_anomaly_data:
            info_list = _value_list_to_info_list(raw_anomaly_data[key][0])
            offset = 0

            anomaly_data[key] = {}

            if trained_on[0]:
                anomaly_data[key]["min"] = (_get_value_list_from_data(info_list, "min").tolist(),
                                            int(raw_anomaly_data[key][1][offset]))
                offset += 1

            if trained_on[1]:
                anomaly_data[key]["max"] = (_get_value_list_from_data(info_list, "max").tolist(),
                                            int(raw_anomaly_data[key][1][offset]))
                offset += 1

            if trained_on[2]:
                anomaly_data[key]["average"] = (_get_value_list_from_data(info_list, "average").tolist(),
                                                int(raw_anomaly_data[key][1][offset]))

        _save_to_json_file(_get_file_path_for_cashed_file_anomaly_data(station_id), anomaly_data)
        stations_info[station_id]["is_cashed_anomaly_data"] = True

        write_stations_info_to_json(stations_info)

    on_status_changed("Finished")
    on_finished(data, anomaly_data, is_trained, trained_on)


def get_stations_data_from_file(stations_info: dict,
                                station_id: str,
                                on_error: Callable[[str], None],
                                on_status_changed: Callable[[str], None],
                                on_finished:
                                Callable[[dict, dict, bool, Tuple[bool, bool, bool]], None]) -> None:
    is_loading_lock = threading.Lock()
    is_loading = True
    statuses = ["Loading", "Loading.", "Loading..", "Loading..."]

    def status_update():
        current_index = 0

        is_loading_lock.acquire()
        while is_loading:
            is_loading_lock.release()

            on_status_changed(statuses[current_index])

            current_index += 1
            if current_index == len(statuses):
                current_index = 0

            time.sleep(0.5)

            is_loading_lock.acquire()

        is_loading_lock.release()

    status_updater = threading.Thread(target=status_update)
    status_updater.start()

    # noinspection PyBroadException
    try:
        _try_get_stations_data_from_file(stations_info,
                                         station_id,
                                         on_status_changed,
                                         on_finished)
    except:
        is_loading_lock.acquire()
        is_loading = False
        is_loading_lock.release()

        status_updater.join()

        on_error("Load crashed")

    is_loading_lock.acquire()
    is_loading = False
    is_loading_lock.release()

    status_updater.join()
