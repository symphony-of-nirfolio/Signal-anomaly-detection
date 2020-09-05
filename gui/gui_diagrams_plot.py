from typing import Callable, Any, Tuple

import matplotlib
from datetime import date

from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from handle_data.info import Info

matplotlib.use('Qt5Agg')


def remove_diagrams(vertical_layout: QtWidgets.QVBoxLayout) -> None:
    for i in reversed(range(vertical_layout.count())):
        vertical_layout.itemAt(i).widget().deleteLater()


def _create_diagram_canvas(main_window: QtWidgets.QMainWindow,
                           vertical_layout: QtWidgets.QVBoxLayout) -> FigureCanvasQTAgg:
    figure = Figure(figsize=(5, 4), dpi=100)
    figure_canvas = FigureCanvasQTAgg(figure)
    figure_canvas.axes = figure.add_subplot(111)

    toolbar = NavigationToolbar2QT(figure_canvas, main_window)

    vertical_layout.addWidget(figure_canvas)
    vertical_layout.addWidget(toolbar)

    return figure_canvas


def _get_min_form_info(info: Info) -> float:
    return info.min


def _get_max_form_info(info: Info) -> float:
    return info.max


def _get_average_from_info(info: Info) -> float:
    return info.average


def _get_data_points(data: list,
                     offset: float,
                     get_data_from_info: Callable[[Info], float],
                     data_offset=0.0) -> (list, list):
    days = []
    observations = []

    for info in data:
        observation = get_data_from_info(info)
        if observation < 100000.0:
            days.append(info.day + offset)
            observations.append(observation + data_offset)

    return days, observations


def _get_min_points(data: list, offset: float) -> (list, list):
    return _get_data_points(data, offset, _get_min_form_info, data_offset=-273.15)


def _get_max_points(data: list, offset: float) -> (list, list):
    return _get_data_points(data, offset, _get_max_form_info, data_offset=-273.15)


def _get_average_points(data: list, offset: float) -> (list, list):
    return _get_data_points(data, offset, _get_average_from_info, data_offset=-273.15)


def _get_points_by_month(data: list,
                         get_points: Callable[[list, float], Tuple[list, list]]) -> (list, list):
    return get_points(data, 0)


def _calculate_offset(year: str, month: str) -> int:
    month_begin = date(int(year), int(month), 1)
    next_month_begin = date(
        int(year) if month != "12" else int(year) + 1,
        int(month) + 1 if month != "12" else 1,
        1)

    days = (next_month_begin - month_begin).days
    return days


def _get_points_by_several_months(data: dict,
                                  get_points: Callable[[list, float], Tuple[list, list]]) -> (list, list):
    days_all = []
    observations_all = []

    offset = 0
    for key in data:
        days, observations = get_points(data[key][0], offset)
        days_all += days
        observations_all += observations

        offset += _calculate_offset(data[key][1], key)

    return days_all, observations_all


def _get_points_by_all_data(data: dict,
                            get_points: Callable[[list, float], Tuple[list, list]]) -> (list, list):
    days_all = []
    observations_all = []

    offset = 0
    for year in data:
        current_data = data[year]

        for key in current_data:
            days, observations = get_points(current_data[key][0], offset)
            days_all += days
            observations_all += observations

            offset += _calculate_offset(current_data[key][1], key)

    return days_all, observations_all


def _get_days(data: list, offset) -> list:
    return list([info.day + offset for info in data])


def _get_days_by_month(data: list) -> list:
    return _get_days(data, 0)


def _get_days_by_several_months(data: dict) -> list:
    days_all = []

    offset = 0
    for key in data:
        days = _get_days(data[key][0], offset)
        days_all += days

        offset += _calculate_offset(data[key][1], key)

    return days_all


def _get_days_by_all_data(data: dict) -> list:
    days_all = []

    offset = 0
    for year in data:
        current_data = data[year]

        for key in current_data:
            days = _get_days(current_data[key][0], offset)
            days_all += days

            offset += _calculate_offset(current_data[key][1], key)

    return days_all


def _get_anomaly_points_by_month(anomaly_data: dict, anomaly_text: str) -> list:
    return anomaly_data[anomaly_text][0]


def _get_anomaly_points_by_several_months(anomaly_data: dict, anomaly_text: str) -> list:
    observations_all = []

    for key in anomaly_data[anomaly_text][0]:
        current_anomaly_data = anomaly_data[anomaly_text][0][key][0]
        observations = current_anomaly_data[anomaly_text][0]
        observations_all += observations

    return observations_all


def _get_anomaly_points_by_all_data(anomaly_data: dict, anomaly_text: str) -> list:
    observations_all = []

    for year in anomaly_data[anomaly_text][0]:
        current_anomaly_data = anomaly_data[anomaly_text][0][year]

        for key in current_anomaly_data:
            observations = current_anomaly_data[key][0][anomaly_text][0]
            observations_all += observations

    return observations_all


def trim_anomaly_data(days: list, anomaly_data: list) -> (list, list):
    new_days = []
    new_anomaly_data = []

    if len(days) != len(anomaly_data):
        print("Bad data")
        return

    for i in range(len(days)):
        if anomaly_data[i] < 10000.0:
            new_days.append(days[i])
            new_anomaly_data.append(anomaly_data[i])

    return new_days, new_anomaly_data


def _add_anomaly_line_to_axes(start_day: float, end_day: float,
                              start_observation: float, end_observation: float,
                              axes: Any) -> None:
    if start_day == end_day:
        print("Bad data: start_day = end_day!")
        return

    # y = k * x + c
    k = (end_observation - start_observation) / (end_day - start_day)
    c = end_observation - k * end_day

    def get_x(y: float):
        return (y - c) / k

    def try_add_zone_to_axes(zone_x: Tuple[float, float], zone_y: Tuple[float, float], color: str, linewidth: int):
        if zone_x[1] < start_day:
            return
        if zone_x[0] > end_day:
            return

        if zone_x[1] < end_day:
            end_point = (zone_x[1], zone_y[1])
        else:
            end_point = (end_day, end_observation)

        if zone_x[0] > start_day:
            start_point = (zone_x[0], zone_y[0])
        else:
            start_point = (start_day, start_observation)

        axes.plot([start_point[0], end_point[0]], [start_point[1], end_point[1]], color, linewidth=linewidth)

    red_zone_y = (0.06, 100.0) if k > 0.0 else (100.0, 0.06)
    yellow_zone_y = (0.03, 0.06) if k > 0.0 else (0.06, 0.03)

    red_zone_x = (get_x(red_zone_y[0]), get_x(red_zone_y[1]))
    yellow_zone_x = (get_x(yellow_zone_y[0]), get_x(yellow_zone_y[1]))

    try_add_zone_to_axes(yellow_zone_x, yellow_zone_y, 'orange', 2)
    try_add_zone_to_axes(red_zone_x, red_zone_y, 'r', 2)


def _add_anomaly_to_axes(anomaly_days: list, anomaly_observations: list, axes: Any, line_width=2) -> None:
    if len(anomaly_days) == 0:
        return

    axes.plot(anomaly_days, anomaly_observations, 'g', linewidth=line_width)

    for i in range(1, len(anomaly_days)):
        _add_anomaly_line_to_axes(anomaly_days[i - 1], anomaly_days[i],
                                  anomaly_observations[i - 1], anomaly_observations[i],
                                  axes)


def _show_diagram_by_points_function(main_window: QtWidgets.QMainWindow,
                                     vertical_layout: QtWidgets.QVBoxLayout,
                                     data: Any,
                                     anomaly_data: dict,
                                     anomaly_text: str,
                                     title: str,
                                     get_points:
                                     Callable[[Any, Callable[[list, float], Tuple[list, list]]], Tuple[list, list]],
                                     get_days: Callable[[Any], list],
                                     get_anomaly_point: Callable[[dict, str], list],
                                     need_min_temperature=False,
                                     need_max_temperature=False,
                                     need_average_temperature=False) -> None:
    figure_canvas = _create_diagram_canvas(main_window, vertical_layout)

    size = 0
    days = []
    anomaly_days = []
    observations = []
    anomaly_observations = []
    colors = []
    labels = []

    if need_max_temperature:
        days_form_max, max_temperature = get_points(data, _get_max_points)
        days.append(days_form_max)
        observations.append(max_temperature)
        colors.append('.-c')
        labels.append("Max")

        if anomaly_text == 'max':
            anomaly_observations = get_anomaly_point(anomaly_data, anomaly_text)
            anomaly_days = get_days(data)

        size += 1

    if need_average_temperature:
        days_form_average, average_temperature = get_points(data, _get_average_points)
        days.append(days_form_average)
        observations.append(average_temperature)
        colors.append('.-m')
        labels.append("Average")

        if anomaly_text == 'average':
            anomaly_observations = get_anomaly_point(anomaly_data, anomaly_text)
            anomaly_days = get_days(data)

        size += 1

    if need_min_temperature:
        days_form_min, min_temperature = get_points(data, _get_min_points)
        days.append(days_form_min)
        observations.append(min_temperature)
        colors.append('.-b')
        labels.append("Min")

        if anomaly_text == 'min':
            anomaly_observations = get_anomaly_point(anomaly_data, anomaly_text)
            anomaly_days = get_days(data)

        size += 1

    figure_canvas.axes.set_title(title)
    figure_canvas.axes.set_ylabel('temperature', color='tab:blue')
    figure_canvas.axes.set_xlabel('days')
    min_observation = 1000
    max_observation = -1000
    for i in range(size):
        figure_canvas.axes.plot(days[i], observations[i], colors[i])
        if len(observations[i]) > 0:
            min_observation = min(min_observation, min(observations[i]))
            max_observation = max(max_observation, max(observations[i]))

    delta = max_observation - min_observation
    delta = max(1.0, delta)

    figure_canvas.axes.set_ylim([min_observation - delta * 0.4, max_observation + delta * 0.1])
    figure_canvas.axes.legend(labels)

    if anomaly_text != 'none':
        anomaly_days, anomaly_observations = trim_anomaly_data(anomaly_days, anomaly_observations)

        if len(anomaly_days) != len(anomaly_observations):
            return

        anomaly_axes = figure_canvas.axes.twinx()
        anomaly_axes.set_ylabel('anomaly', color='tab:red')
        _add_anomaly_to_axes(anomaly_days, anomaly_observations, anomaly_axes)
        anomaly_axes.set_ylim([0.0, 0.2])


def show_diagram_by_month(main_window: QtWidgets.QMainWindow,
                          vertical_layout: QtWidgets.QVBoxLayout,
                          data: list,
                          anomaly_data: dict,
                          anomaly_text: str,
                          title: str,
                          need_min_temperature=False,
                          need_max_temperature=False,
                          need_average_temperature=False) -> None:
    _show_diagram_by_points_function(main_window, vertical_layout, data, anomaly_data, anomaly_text, title,
                                     _get_points_by_month,
                                     _get_days_by_month,
                                     _get_anomaly_points_by_month,
                                     need_min_temperature=need_min_temperature,
                                     need_max_temperature=need_max_temperature,
                                     need_average_temperature=need_average_temperature)


def show_diagram_by_several_months(main_window: QtWidgets.QMainWindow,
                                   vertical_layout: QtWidgets.QVBoxLayout,
                                   data: dict,
                                   anomaly_data: dict,
                                   anomaly_text: str,
                                   title: str,
                                   need_min_temperature=False,
                                   need_max_temperature=False,
                                   need_average_temperature=False) -> None:
    _show_diagram_by_points_function(main_window, vertical_layout, data, anomaly_data, anomaly_text, title,
                                     _get_points_by_several_months,
                                     _get_days_by_several_months,
                                     _get_anomaly_points_by_several_months,
                                     need_min_temperature=need_min_temperature,
                                     need_max_temperature=need_max_temperature,
                                     need_average_temperature=need_average_temperature)


def show_diagram_by_several_all_data(main_window: QtWidgets.QMainWindow,
                                     vertical_layout: QtWidgets.QVBoxLayout,
                                     data: dict,
                                     anomaly_data: dict,
                                     anomaly_text: str,
                                     title: str,
                                     need_min_temperature=False,
                                     need_max_temperature=False,
                                     need_average_temperature=False) -> None:
    _show_diagram_by_points_function(main_window, vertical_layout, data, anomaly_data, anomaly_text, title,
                                     _get_points_by_all_data,
                                     _get_days_by_all_data,
                                     _get_anomaly_points_by_all_data,
                                     need_min_temperature=need_min_temperature,
                                     need_max_temperature=need_max_temperature,
                                     need_average_temperature=need_average_temperature)
