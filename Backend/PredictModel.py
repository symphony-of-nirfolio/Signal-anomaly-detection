import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from Backend.CustomGenerator import SequenceGenerator
from Backend.TrainModel import _create_model_CNN, _COLUMN_TO_STR, _SEASON_NUMBER, _COLUMNS_NUMBER, _SEASON_TO_MONTHS, _create_model_LSTM

import numpy as np
import concurrent
from threading import Lock


class Prediction:
    _instance = None
    _model = None
    _station = None
    _path_to_nn = None
    _predict_result = None
    _lock = None
    _RED = 0.025
    _YELLOW = 0.01
    _RANGE = 0.3

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def _load_nn_CNN(self, path_to_nn, station, col, season):
        self._path_to_nn = path_to_nn
        nn_file = path_to_nn + '/' + station + '/' + col + '/' + str(season) + '.h5'
        if os.path.exists(nn_file):
            model = _create_model_CNN()
            model.load_weights(nn_file)
            model.compile(loss='mean_squared_error', optimizer='adam')
            return model
        else:
            return None

    def _load_nn_LSTM(self, path_to_nn, station, col, season):
        self._path_to_nn = path_to_nn
        nn_file = path_to_nn + '/' + station + '/' + col + '/' + str(season) + '.h5'
        if os.path.exists(nn_file):
            model = _create_model_LSTM()
            model.load_weights(nn_file)
            model.compile(loss='mean_squared_error', optimizer='adam')
            return model
        else:
            return None

    def setup_model(self, path_to_nn, station):
        self._station = station
        self._model = {}
        for column in range(_COLUMNS_NUMBER - 1):
            col_str = _COLUMN_TO_STR[column]
            self._model[col_str] = {}
            for season in range(_SEASON_NUMBER):
                self._model[col_str][season] = self._load_nn_LSTM(path_to_nn, station, col_str, season)
        self._predict_result = {}
        self._lock = Lock()

    # give range of season for nn
    def _get_range(self, path_to_nn, station, column, season):
        data = np.fromfile(path_to_nn + '/' + station + '/' + _COLUMN_TO_STR[column] + '/nn_range', sep=',')
        data = np.reshape(data, (data.shape[0] // 3, 3))
        return data[season, 1], data[season, 2]

    def _prepare_data(self, data, path_to_nn, station, col, season):
        data = data[10000 > data]
        min_, max_ = self._get_range(path_to_nn, station, col, season)
        data = np.array([(item - min_) / (max_ - min_) * 2 - 1 for item in data])
        if len(data) < 28:
            data = np.append(data, np.zeros(28 - len(data)))
        return data

    def _shift(self, data, answer):
        res = np.empty(0)
        k = 0
        for item in data:
            if item > 10000:
                res = np.append(res, item)
            else:
                res = np.append(res, answer[k])
                k += 1

        return res

    def get_result(self, data, col, season):

        data_to_predict = self._prepare_data(data, self._path_to_nn, self._station, col, season)
        if len(data_to_predict) == 28:
            test_generator = SequenceGenerator(np.array([0]), 1, data_to_predict, 1, 28)
        else:
            test_generator = SequenceGenerator(np.array([0, len(data_to_predict) - 28]), 1, data_to_predict, 1, 28)

        results = self._model[_COLUMN_TO_STR[col]][season].predict(x=test_generator,
                                                                   steps=len(test_generator),
                                                                   verbose=0)
        results = np.reshape(results, (results.shape[0], results.shape[1]))
        if len(data_to_predict) == 28:
            answer = (results[0, :] - data_to_predict) ** 2
        else:
            answer = (results[0, :] - data_to_predict[:28]) ** 2
            answer = np.append(answer, (results[1, 2 * 28 - len(data_to_predict):] - data_to_predict[28:]) ** 2)

        color = 0
        if max(answer) > self.get_red():
            color = 2
        elif max(answer) > self.get_yellow():
            color = 1
        answer = self._shift(data, answer)

        return answer, color

    # concat data for neural network by lots of parts by size 28
    def _concat_local_data(self, data, column, season, WINDOW_size):
        min_value, max_value = self._get_range(self._path_to_nn, self._station, column, season)

        def _rearrange_data(data_to_rearrange):
            data_to_rearrange = data_to_rearrange[data_to_rearrange < 10000]
            return np.array([(item - min_value) / (max_value - min_value) * 2 - 1 for item in data_to_rearrange])

        def _split_on_window(data_to_split, year_to_split):
            if len(data_to_split) < WINDOW_size:
                split_data = np.append(data_to_split, np.zeros(WINDOW_size-len(data_to_split)))
                split_year = np.append(year_to_split, np.full((WINDOW_size - len(year_to_split)), -1))
                return split_data, split_year

            split_data = np.empty(0)
            split_year = np.empty(0)
            for i in range(len(data_to_split) // (WINDOW_size // 2)):
                pos = i * WINDOW_size // 2
                if pos + WINDOW_size <= len(data_to_split):
                    split_data = np.append(split_data, data_to_split[pos:pos + WINDOW_size])
                    split_year = np.append(split_year, year_to_split[pos:pos + WINDOW_size])
                elif pos + WINDOW_size // 2 != len(data_to_split):
                    split_data = np.append(split_data, data_to_split[pos:])
                    split_data = np.append(split_data, np.zeros(WINDOW_size - len(data_to_split) + pos))
                    split_year = np.append(split_year, year_to_split[pos:])
                    split_year = np.append(split_year, np.full((WINDOW_size - len(data_to_split) + pos), -1))

            return split_data, split_year

        months = _SEASON_TO_MONTHS[season]
        if season == 0:
            months = ('01', '02')
        concat = np.empty(0)
        year_concat = np.empty(0)
        prev_year = -1
        for year in data:
            merged = np.empty(0)
            merged_year_arr = np.empty(0)
            if int(year) - prev_year == 1:
                if '12' in data[str(prev_year)]:
                    merged = _rearrange_data(data[str(prev_year)]['12'])
                    merged_year_arr = np.full((len(merged)), int(year))
            else:
                if prev_year != -1 and '12' in data[str(prev_year)]:
                    merged = _rearrange_data(data[str(prev_year)]['12'])
                    merged_year_arr = np.full((len(merged)), int(year))
                    merged, merged_year_arr = _split_on_window(merged, merged_year_arr)
                    concat = np.append(concat, merged)
                    year_concat = np.append(year_concat, merged_year_arr)
                    merged = np.empty(0)
                    merged_year_arr = np.empty(0)

            for month in months:
                if month in data[year]:
                    current_month = _rearrange_data(data[year][month])
                    year_arr = np.full((len(current_month)), int(year))
                    merged = np.append(merged, current_month)
                    merged_year_arr = np.append(merged_year_arr, year_arr)

            merged, merged_year_arr = _split_on_window(merged, merged_year_arr)
            concat = np.append(concat, merged)
            year_concat = np.append(year_concat, merged_year_arr)
            prev_year = int(year)

        return concat, year_concat

    # get difference between input and output of nn
    def _get_difference(self, data_to_predict, results):
        results = np.reshape(results, (results.shape[0]*results.shape[1]))
        diff = (results - data_to_predict)**2
        return diff

    # save all results of
    def _save_to_dict(self, main_data, data_results, col, season):

        self._lock.acquire()
        if col not in self._predict_result:
            self._predict_result[col] = {}
        self._lock.release()

        self._predict_result[col][season] = {}
        current_pos = 0
        for year in main_data:
            self._predict_result[col][season][year] = {}

            for month in main_data[year]:
                ans_for_month = np.empty(0)
                for day in main_data[year][month]:
                    if day > 10000:
                        ans_for_month = np.append(ans_for_month, day)
                    else:
                        ans_for_month = np.append(ans_for_month, data_results[current_pos])
                        current_pos += 1

                temp = ans_for_month[ans_for_month < 10000]
                self._predict_result[col][season][year][month] = (ans_for_month, self._get_color(temp))

    # merge same WINDOW=14 parts
    def _merge_same_parts(self, data_to_predict, year_to_concat, results, _WINDOW):

        merged_predict = np.empty(0)
        merged_year = np.empty(0)
        merged_results = np.empty(0)

        i = 0
        while i < len(data_to_predict):
            current_year = year_to_concat[i]
            day = i

            while day < len(year_to_concat) and year_to_concat[day] == current_year and i + _WINDOW > day:
                merged_predict = np.append(merged_predict, data_to_predict[day])
                merged_year = np.append(merged_year, year_to_concat[day])
                merged_results = np.append(merged_results, results[day])
                day += 1

            i += _WINDOW
            while day + _WINDOW < len(year_to_concat) and year_to_concat[day + _WINDOW] == current_year:
                if day < i + _WINDOW:
                    merged_predict = np.append(merged_predict, data_to_predict[day])
                    merged_year = np.append(merged_year, year_to_concat[day])
                    merged_results = np.append(merged_results, max(results[day], results[day + _WINDOW]))
                    day += 1
                else:
                    i += 2*_WINDOW
                    day += _WINDOW

            while day < len(year_to_concat) and day < i + _WINDOW and year_to_concat[day] != -1:
                merged_predict = np.append(merged_predict, data_to_predict[day])
                merged_year = np.append(merged_year, year_to_concat[day])
                merged_results = np.append(merged_results, results[day])
                day += 1

            i += _WINDOW

        return merged_predict, merged_year, merged_results

    # predict for season and column CNN
    def _predict_model_for_season_CNN(self, data, nn_model, column, season):
        data_to_predict, year_concat = self._concat_local_data(data, column, season, 28)

        test_generator = SequenceGenerator(range(len(data_to_predict) // 28), 1, data_to_predict, 28, 28)
        results = nn_model.predict(x=test_generator,
                                   steps=len(test_generator),
                                   verbose=0)

        results = np.reshape(results, (results.shape[0], results.shape[1]))
        results = self._get_difference(data_to_predict, results)
        data_to_predict, year_concat, results = self._merge_same_parts(data_to_predict, year_concat, results, 14)

        self._save_to_dict(data, results, column, season)

    # predict for season and column LSTM
    def _predict_model_for_season_LSTM(self, data, nn_model, column, season):
        WINDOW_x = 28
        data_to_predict, year_concat = self._concat_local_data(data, column, season, WINDOW_x)

        test_generator = SequenceGenerator(range(len(data_to_predict) // WINDOW_x), 1, data_to_predict, WINDOW_x, WINDOW_x)
        results = nn_model.predict(x=test_generator,
                                   steps=len(test_generator),
                                   verbose=0)

        results = np.reshape(results, (results.shape[0], results.shape[1]))
        results = self._get_difference(data_to_predict, results)
        data_to_predict, year_concat, results = self._merge_same_parts(data_to_predict, year_concat, results, WINDOW_x // 2)

        self._save_to_dict(data, results, column, season)

    def _month_to_season(self, month):
        for i in range(4):
            if month in _SEASON_TO_MONTHS[i]:
                return i

    def _convert_to_np(self, current_data):
        temp = np.array(current_data)
        temp = np.reshape(temp, (temp.shape[0] // _COLUMNS_NUMBER, _COLUMNS_NUMBER))
        return temp

    # split all input data array on seasons and columns
    def _split_all(self, data, columns):

        col_season_data = {}
        for col in range(_COLUMNS_NUMBER-1):
            if columns[col]:
                col_season_data[col] = {}
                for i in range(4):
                    col_season_data[col][i] = {}

        for key in data:
            season = self._month_to_season(key[-2:])
            temp_data = self._convert_to_np(data[key])
            for col in range(_COLUMNS_NUMBER-1):
                if columns[col]:
                    if not key[:4] in col_season_data[col][season]:
                        col_season_data[col][season][key[:4]] = {}

                    col_season_data[col][season][key[:4]][key[-2:]] = temp_data[:, col + 1]

        return col_season_data

    def _get_color(self, values):
        if len(values) == 0:
            return -1
        value = max(values)
        if value >= self.get_red():
            return 2
        elif value >= self.get_yellow():
            return 1
        else:
            return 0

    def _merge_all(self, data, columns):
        merged = {}
        for key in data:
            season = self._month_to_season(key[-2:])
            temp_data = self._convert_to_np(data[key])
            temp_color = np.empty(0)
            for col in range(_COLUMNS_NUMBER-1):
                if columns[col]:
                    res = self._predict_result[col][season][key[:4]][key[-2:]]
                    temp_data[:, col + 1] = res[0]
                    temp_color = np.append(temp_color, res[1])
            temp_data = list(np.reshape(temp_data, (temp_data.shape[0]*temp_data.shape[1])))
            merged[key] = (temp_data, temp_color)
        return merged

    # result in CNN for multiple data
    def _get_result_multiple_CNN(self, data, columns):

        splitted_data = self._split_all(data, columns)
        self._predict_result = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            threads = []
            for season in range(_SEASON_NUMBER):
                for column in range(_COLUMNS_NUMBER - 1):
                    if columns[column]:
                        threads.append(executor.submit(self._predict_model_for_season_CNN,
                                                       splitted_data[column][season],
                                                       self._model[_COLUMN_TO_STR[column]][season],
                                                       column, season))
            concurrent.futures.wait(threads)

        return self._merge_all(data, columns)

    # result in LSTM for multiple data
    def _get_result_multiple_LSTM(self, data, columns):

        splitted_data = self._split_all(data, columns)
        self._predict_result = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            threads = []
            for season in range(_SEASON_NUMBER):
                for column in range(_COLUMNS_NUMBER - 1):
                    if columns[column]:
                        threads.append(executor.submit(self._predict_model_for_season_LSTM,
                                                       splitted_data[column][season],
                                                       self._model[_COLUMN_TO_STR[column]][season],
                                                       column, season))
            concurrent.futures.wait(threads)

        return self._merge_all(data, columns)

    # result for multiple data
    def get_result_multiple(self, data, columns):
        return self._get_result_multiple_LSTM(data, columns)

    def get_red(self):
        return self._RED

    def get_yellow(self):
        return self._YELLOW

    # get range of anomalies
    def get_range(self):
        return self._RANGE
