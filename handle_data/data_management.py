import _thread
import os
import json
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
        print(data)
        return data


def write_stations_info_to_json(stations_info: dict) -> None:
    with open(stations_info_path, 'w') as stations_info_file:
        json.dump(stations_info, stations_info_file)


def get_audio_info_from_json() -> dict:
    with open(audio_info_path) as audio_info_file:
        audio_info = json.load(audio_info_file)
        print(audio_info)
        return audio_info


def write_audio_info_to_json(audio_info: dict) -> None:
    with open(audio_info_path, 'w') as audio_info_file:
        json.dump(audio_info, audio_info_file)


def get_directory_path_for_station_data(station_id: str) -> str:
    return stations_data_path + "/" + station_id + "/data"


def create_directory_for_station(station_id: str) -> str:
    path = get_directory_path_for_station_data(station_id)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def get_directory_path_for_trained_model() -> str:
    return model_data_path


def create_directory_for_trained_model() -> str:
    path = get_directory_path_for_trained_model()
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def get_file_path_for_one_file_data(station_id: str) -> str:
    return stations_data_path + "/" + station_id + "/cash_data"


def get_file_path_for_one_file_anomaly_data(station_id: str) -> str:
    return stations_data_path + "/" + station_id + "/cash_anomaly_data"


def _get_season_by_month(month: int):
    if month == 12 or month == 1 or month == 2:
        return 0
    if 3 <= month <= 5:
        return 1
    if 6 <= month <= 8:
        return 2
    if 9 <= month <= 11:
        return 3


def _get_data_from_file(path: str,
                        key: str,
                        month: int,
                        data: dict,
                        anomaly_data: dict,
                        is_trained: bool,
                        trained_on: (bool, bool, bool),
                        prediction: Prediction) -> None:
    try:
        current_data = np.fromfile(path, sep=',')
        current_data = np.reshape(current_data, (current_data.shape[0] // 4, 4))
        if is_trained:
            anomaly_data[key] = {}
            if trained_on[0]:
                anomaly_array, zone = prediction.get_result(current_data[:, 1], 0, _get_season_by_month(month))
                anomaly_data[key]["min"] = (anomaly_array.tolist(), zone)
            if trained_on[1]:
                anomaly_array, zone = prediction.get_result(current_data[:, 2], 1, _get_season_by_month(month))
                anomaly_data[key]["max"] = (anomaly_array.tolist(), zone)
            if trained_on[2]:
                anomaly_array, zone = prediction.get_result(current_data[:, 3], 2, _get_season_by_month(month))
                anomaly_data[key]["average"] = (anomaly_array.tolist(), zone)

        info_by_month = []
        for i in range(current_data.shape[0]):
            info = Info()
            info.day = current_data[i][0]
            info.min = current_data[i][1]
            info.max = current_data[i][2]
            info.average = current_data[i][3]

            info_by_month.append(info)

        data[key] = info_by_month
    finally:
        return


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


# noinspection PyUnusedLocal
def get_stations_data_from_file(stations_info: dict,
                                station_id: str,
                                on_error: Callable[[str], None],
                                on_status_changed: Callable[[str], None],
                                on_finished:
                                Callable[[dict, dict, bool, Tuple[bool, bool, bool]], None]) -> (dict, dict):
    data_path = get_directory_path_for_station_data(station_id)
    model_path = get_directory_path_for_trained_model()

    is_loading = True
    current_index = 0
    statuses = ["Loading", "Loading.", "Loading..", "Loading..."]

    def status_update():
        nonlocal current_index
        while is_loading:
            on_status_changed(statuses[current_index])
            time.sleep(0.5)
            current_index += 1
            if current_index == len(statuses):
                current_index = 0

    _thread.start_new_thread(status_update, ())

    min_year = 1800
    max_year = 2100

    min_month = 1
    max_month = 12

    need_to_load_data = True
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

    data = {}
    anomaly_data = {}

    if stations_info[station_id]["is_cashed_data"]:
        data = _convert_to_data(_load_from_json_file(get_file_path_for_one_file_data(station_id)))
        need_to_load_data = False

    if stations_info[station_id]["is_cashed_anomaly_data"]:
        anomaly_data = _load_from_json_file(get_file_path_for_one_file_anomaly_data(station_id))
        need_to_load_anomaly_data = False

    if need_to_load_data or need_to_load_anomaly_data:
        for year in range(min_year, max_year):
            for month in range(min_month, max_month):
                key = "{}_{:02d}".format(year, month)
                path = "{}/{}".format(data_path, key)
                _get_data_from_file(path, key, month, data, anomaly_data, is_trained, trained_on, prediction)

        _save_to_json_file(get_file_path_for_one_file_data(station_id), data)
        stations_info[station_id]["is_cashed_data"] = True

        if is_trained:
            _save_to_json_file(get_file_path_for_one_file_anomaly_data(station_id), anomaly_data)
            stations_info[station_id]["is_cashed_anomaly_data"] = True

        write_stations_info_to_json(stations_info)

    is_loading = False

    on_status_changed("Finished")
    on_finished(data, anomaly_data, is_trained, trained_on)
