import numpy as np
import os
import shutil

_column_to_str = ['min', 'max', 'average']


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
            temp_path = all_path + _column_to_str[i]
            if os.path.exists(temp_path):
                shutil.rmtree(temp_path)
            os.mkdir(temp_path)


def _prepare_all_data(station_id, columns, path_to_save):
    _create_directory_for_nn(station_id, columns, path_to_save)
    

def train(station_id, path_to_data, columns, path_to_save):
    _prepare_all_data(station_id, columns, path_to_save)


train('ui123', None, (0, 1, 0), 'nn')

