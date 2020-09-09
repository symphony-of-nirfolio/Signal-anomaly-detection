import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from keras.layers import Conv1D, GlobalMaxPool1D, Dense, MaxPooling1D, Flatten, Dropout, UpSampling1D
from keras.models import Model, Sequential
from keras.callbacks import EarlyStopping, ModelCheckpoint
from Backend.CustomGenerator import SequenceGenerator

import random
import numpy as np
import shutil
from matplotlib import pyplot as plt
import json
import concurrent

_COLUMNS_NUMBER = 4
_COLUMN_TO_STR = ('min', 'max', 'average')
_SEASON_NUMBER = 4
_SEASON_TO_MONTHS = (('01', '02', '12'), ('03', '04', '05'), ('06', '07', '08'), ('09', '10', '11'))
_MIN_YEAR = 1800
_MAX_YEAR = 2020
_MIN_TEMPERATURE = 265
_MAX_TEMPERATURE = 320
_SCALE_DATA = 8

_BATCH_SIZE = 8
_IN_X = 28
_IN_Y = 1
_EPOCHS = 200


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


def _merge_data_for_season_json(season, all_data, column):
    merged_data = np.empty(0)

    months = _SEASON_TO_MONTHS[season]
    for key in all_data:
        if key[-2:] in months:
            cur_data = np.array(all_data[key])
            cur_data = np.reshape(cur_data, (cur_data.shape[0] // _COLUMNS_NUMBER, _COLUMNS_NUMBER))
            if not cur_data.shape[0] == 0:
                merged_data = np.append(merged_data, cur_data[:, column])

    return merged_data


def _rid_of_anomalies(data, path_to_nn, station, col, season):
    data = data[data < 1000]
    data = data[data > 0]
    plt.clf()
    res = plt.boxplot(data, vert=False)
    min_season_value = min(data)-1
    max_season_value = max(data)+1
    min_value = res['caps'][0].get_data()[0][0]
    max_value = res['caps'][1].get_data()[0][0]
    plt.clf()
    plt.close()
    # plt.show()
    data = data[data >= min_value]
    data = data[data <= max_value]
    data = np.array([(item - min_season_value)/(max_season_value - min_season_value)*2 - 1 for item in data])
    # print(min(data), max(data))

    file = open(path_to_nn + '/' + station + '/' + _COLUMN_TO_STR[col] + '/nn_range', 'a')
    if season == 3:
        file.write(str(season) + ',' + str(min_season_value) + ',' + str(max_season_value))
    else:
        file.write(str(season) + ',' + str(min_season_value) + ',' + str(max_season_value) + ',')
    file.close()

    return data


def _save_temp_data(path, station_id, season, column, data):
    data.tofile(path + '/' + station_id + '/' + str(season) + '_' + str(column) + '.dat', sep=',')


def _read_json_file(path_to_data):
    with open(path_to_data, 'r') as j:
        json_data = json.load(j)
        return json_data


def _prepare_all_data_single_file(station_id, path_to_data, columns, path_to_save):
    _create_directory_for_nn(station_id, columns, path_to_save)

    all_data = _read_json_file(path_to_data)
    for col in range(len(columns)):
        if columns[col]:
            for season in range(_SEASON_NUMBER):
                data = _merge_data_for_season_json(season, all_data, col + 1)
                data = _rid_of_anomalies(data, path_to_save, station_id, col, season)
                _save_temp_data(path_to_save, station_id, season, col, data)


def _create_model():
    model = Sequential()
    '''
    model.add(Conv1D(filters=4, kernel_size=5, padding='same', activation='tanh', input_shape=(_IN_X, _IN_Y)))
    model.add(MaxPooling1D(4))
    model.add(Conv1D(filters=8, kernel_size=3, padding='same', activation='tanh'))
    model.add(GlobalMaxPool1D())
    model.add(Dense(units=_IN_X, activation='tanh'))
    '''
    model.add(Conv1D(filters=32, kernel_size=3, padding='same', activation='tanh', input_shape=(_IN_X, _IN_Y)))
    model.add(MaxPooling1D(2))
    model.add(Conv1D(filters=64, kernel_size=3, padding='same', activation='tanh'))
    model.add(MaxPooling1D(2))
    model.add(Conv1D(filters=128, kernel_size=3, padding='same', activation='tanh'))

    model.add(Conv1D(filters=128, kernel_size=3, padding='same', activation='tanh'))
    model.add(UpSampling1D(2))
    model.add(Conv1D(filters=64, kernel_size=3, padding='same', activation='tanh'))
    model.add(UpSampling1D(2))
    model.add(Conv1D(filters=1, kernel_size=3, padding='same', activation='tanh'))
    # model.summary()
    '''
    model.add(Conv1D(filters=8, kernel_size=3, padding='same', activation='tanh', input_shape=(_IN_X, _IN_Y)))
    model.add(MaxPooling1D(2))
    model.add(Conv1D(filters=16, kernel_size=3, padding='same', activation='tanh'))
    model.add(MaxPooling1D(2))
    model.add(Flatten())
    model.add(Dense(units=10, activation='tanh'))
    model.add(Dense(units=_IN_X, activation='tanh'))
    '''
    return model


def _get_model():
    model = _create_model()
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model


def _get_samples(dataset_len):
    dataset_len = dataset_len//8 - 4
    all_samples = [i for i in range(dataset_len)]
    random.shuffle(all_samples)
    train_size = (int(0.7*dataset_len)//8 + 1)*8
    valid_size = ((dataset_len - train_size)//8)*8
    train_samples = all_samples[:train_size]
    valid_samples = all_samples[train_size:train_size+valid_size]
    return train_samples, valid_samples


def _train_model_for_season(path_to_save, station_id, season, column):
    data_for_learn = np.fromfile(path_to_save + '/' + station_id + '/' + str(season) + '_' + str(column) + '.dat',
                                 sep=',')

    model = _get_model()
    train_samples, valid_samples = _get_samples(len(data_for_learn))
    train_generator = SequenceGenerator(train_samples, _BATCH_SIZE, data_for_learn, _SCALE_DATA)
    valid_generator = SequenceGenerator(valid_samples, _BATCH_SIZE, data_for_learn, _SCALE_DATA)
    # print(len(data_for_learn))
    early_stopper = EarlyStopping(patience=5, verbose=0)
    nn_save_path = path_to_save + '/' + station_id + '/' + _COLUMN_TO_STR[column] + '/' + str(season) + '.h5'
    check_pointer = ModelCheckpoint(nn_save_path, verbose=0, save_best_only=True)

    model.fit(x=train_generator,
              steps_per_epoch=len(train_generator),
              epochs=_EPOCHS,
              verbose=0,
              validation_data=valid_generator,
              validation_steps=len(valid_generator),
              callbacks=[check_pointer, early_stopper])


def _delete_temp_data(path_to_save, station_id, columns):
    for season in range(_SEASON_NUMBER):
        for i in range(len(columns)):
            if columns[i]:
                os.remove(path_to_save + '/' + station_id + '/' + str(season) + '_' + str(i) + '.dat')


def train_single_file(station_id, path_to_data, columns, path_to_save):

    _prepare_all_data_single_file(station_id, path_to_data, columns, path_to_save)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        threads = []
        for season in range(_SEASON_NUMBER):
            for i in range(len(columns)):
                if columns[i]:
                    threads.append(executor.submit(_train_model_for_season,
                                                   path_to_save, station_id, season, i))
        concurrent.futures.wait(threads)

    _delete_temp_data(path_to_save, station_id, columns)

