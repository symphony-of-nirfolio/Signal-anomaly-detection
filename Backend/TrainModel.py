import numpy as np
import os
import shutil
from matplotlib import pyplot as plt

_COLUMNS_NUMBER = 4
_COLUMN_TO_STR = ('min', 'max', 'average')
_SEASON_NUMBER = 4
_SEASON_TO_MONTHS = (('01', '02', '12'), ('03', '04', '05'), ('06', '07', '08'), ('09', '10', '11'))
_MIN_YEAR = 1800
_MAX_YEAR = 2020
_MIN_TEMPERATURE = 265
_MAX_TEMPERATURE = 320


def _create_directory_for_nn(station_id, columns, path_to_save):
    all_path = path_to_save
    if not os.path.exists(path_to_save):
        os.mkdir(path_to_save)

    all_path += '/' + station_id
    if not os.path.exists(all_path):
        os.mkdir(all_path)

    all_path += '/'
    for i in range(len(columns)):
        if columns[i]:
            temp_path = all_path + _COLUMN_TO_STR[i]
            if os.path.exists(temp_path):
                shutil.rmtree(temp_path)
            os.mkdir(temp_path)


def _read_from_file(file_name, values_len):
    try:
        data = np.fromfile(file_name, sep=',')
        return np.reshape(data, (data.shape[0] // values_len, values_len))
    except:
        return np.array([])


def _merge_data_for_season(season, path_to_data, column):
    merged_data = np.empty(0)
    months = _SEASON_TO_MONTHS[season]
    for year in range(_MIN_YEAR, _MAX_YEAR, 1):
        for month in months:
            month_file = path_to_data + '/' + str(year) + '_' + month
            cur_data = _read_from_file(month_file, _COLUMNS_NUMBER)
            if not cur_data.shape[0] == 0:
                merged_data = np.append(merged_data, cur_data[:, column])

    return merged_data


def _rid_of_anomalies(data):
    data = data[data < 1000]
    plt.clf()
    res = plt.boxplot(data, vert=False)
    min_ = min(data) - 10
    max_ = max(data) + 10
    min_value = res['caps'][0].get_data()[0][0]
    max_value = res['caps'][1].get_data()[0][0]
    plt.show()
    data = data[data >= min_value]
    data = data[data <= max_value]
    data = np.array([(item - min_)/(max_ - min_) for item in data])
    return data


def _save_temp_data(path, station_id, season, column, data):
    data.tofile(path + '/' + station_id + '/' + str(season) + '_' + str(column) + '.dat', sep=',')


def _prepare_all_data(station_id, path_to_data, columns, path_to_save):
    _create_directory_for_nn(station_id, columns, path_to_save)

    for season in range(_SEASON_NUMBER):
        for i in range(len(columns)):
            if columns[i]:
                data = _merge_data_for_season(season, path_to_data, i + 1)
                data = _rid_of_anomalies(data)
                _save_temp_data(path_to_save, station_id, season, i, data)


def train(station_id, path_to_data, columns, path_to_save):
    _prepare_all_data(station_id, path_to_data, columns, path_to_save)

    

train('ui123', 'data', (0, 1, 0), 'nn')
