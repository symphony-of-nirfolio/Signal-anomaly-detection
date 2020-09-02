import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from Backend.CustomGenerator import SequenceGenerator
from Backend.TrainModel import _create_model, _COLUMN_TO_STR, _SEASON_NUMBER, _COLUMNS_NUMBER
from Backend.TrainModel import _MIN_TEMPERATURE, _MAX_TEMPERATURE

import numpy as np


class Prediction:
    _instance = None
    _model = None
    _station = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def _load_nn(self, path_to_nn, station, col, season):
        nn_file = path_to_nn + '/' + station + '/' + col + '/' + str(season) + '.h5'
        if os.path.exists(nn_file):
            model = _create_model()
            model.load_weights(nn_file)
            model.compile(loss='mean_squared_error', optimizer='adam')
            return model
        else:
            return None

    def setup_model(self, path_to_nn, station):
        self._station = station
        self._model = {}
        for column in range(_COLUMNS_NUMBER-1):
            col_str = _COLUMN_TO_STR[column]
            self._model[col_str] = {}
            for season in range(_SEASON_NUMBER):
                self._model[col_str][season] = self._load_nn(path_to_nn, station, col_str, season)

    def _prepare_data(self, data):
        data = data[10000 > data]
        min_ = _MIN_TEMPERATURE
        max_ = _MAX_TEMPERATURE
        data = np.array([(item - min_)/(max_ - min_)*2 - 1 for item in data])
        if len(data) < 28:
            data = np.append(data, np.zeros(28-len(data)))
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

        data_to_predict = self._prepare_data(data)
        if len(data_to_predict) == 28:
            test_generator = SequenceGenerator(np.array([0]), 1, data_to_predict, 1)
        else:
            test_generator = SequenceGenerator(np.array([0, len(data_to_predict)-28]), 1, data_to_predict, 1)

        results = self._model[_COLUMN_TO_STR[col]][season].predict(x=test_generator,
                                                                   steps=len(test_generator),
                                                                   verbose=0)
        if len(data_to_predict) == 28:
            answer = (results[0, :] - data_to_predict)**2
        else:
            answer = (results[0, :] - data_to_predict[:28])**2
            answer = np.append(answer, (results[1, 2*28 - len(data_to_predict):] - data_to_predict[28:])**2)

        answer = self._shift(data_to_predict, answer)

        if max(answer) > 0.006:
            return answer, 2
        elif max(answer) > 0.003:
            return answer, 1
        else:
            return answer, 0
