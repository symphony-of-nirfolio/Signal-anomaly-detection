import os
import json
import numpy as np

from handle_data.info import Info

common_path = "data"
stations_info_path = common_path + "/common_data.json"

stations_data_path = common_path + "/stations"


def init_files_and_directories_if_not_exist() -> None:
    if not os.path.exists(stations_info_path):
        os.mkdir(common_path)
        with open(stations_info_path, 'w') as stations_info_file:
            json.dump({}, stations_info_file)

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


def get_directory_path_for_station_data(station_id: str) -> str:
    return stations_data_path + "/" + station_id + "/data"


def create_directory_for_station(station_id: str) -> str:
    path = get_directory_path_for_station_data(station_id)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def get_directory_path_for_trained_model(station_id: str) -> str:
    return stations_data_path + "/" + station_id + "/model"


def create_directory_for_trained_model(station_id: str) -> str:
    path = get_directory_path_for_trained_model(station_id)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def _get_data_from_file(path: str, key: str, data: dict) -> None:
    try:
        current_data = np.fromfile(path, sep=',')
        current_data = np.reshape(current_data, (current_data.shape[0] // 4, 4))

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


def get_stations_data_from_file(station_id: str) -> dict:
    data_path = get_directory_path_for_station_data(station_id)

    min_year = 1800
    max_year = 2100

    min_month = 1
    max_month = 12

    data = {}

    for year in range(min_year, max_year):
        for month in range(min_month, max_month):
            key = "{}_{:02d}".format(year, month)
            path = "{}/{}".format(data_path, key)
            _get_data_from_file(path, key, data)

    return data
