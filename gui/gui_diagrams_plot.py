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


def _show_diagram_by_points_function(main_window: QtWidgets.QMainWindow,
                                     vertical_layout: QtWidgets.QVBoxLayout,
                                     data: Any,
                                     get_points:
                                     Callable[[Any, Callable[[list, float], Tuple[list, list]]], Tuple[list, list]],
                                     need_min_temperature=False,
                                     need_max_temperature=False,
                                     need_average_temperature=False) -> None:
    figure_canvas = _create_diagram_canvas(main_window, vertical_layout)

    size = 0
    days = []
    observations = []
    colors = []
    labels = []

    if need_max_temperature:
        days_form_max, max_temperature = get_points(data, _get_max_points)
        days.append(days_form_max)
        observations.append(max_temperature)
        colors.append('r')
        labels.append("Max")
        size += 1

    if need_average_temperature:
        days_form_average, average_temperature = get_points(data, _get_average_points)
        days.append(days_form_average)
        observations.append(average_temperature)
        colors.append('m')
        labels.append("Average")
        size += 1

    if need_min_temperature:
        days_form_min, min_temperature = get_points(data, _get_min_points)
        days.append(days_form_min)
        observations.append(min_temperature)
        colors.append('y')
        labels.append("Min")
        size += 1

    for i in range(size):
        figure_canvas.axes.plot(days[i], observations[i], colors[i])
    figure_canvas.axes.legend(labels)


def show_diagram_by_month(main_window: QtWidgets.QMainWindow,
                          vertical_layout: QtWidgets.QVBoxLayout,
                          data: list,
                          need_min_temperature=False,
                          need_max_temperature=False,
                          need_average_temperature=False) -> None:
    _show_diagram_by_points_function(main_window, vertical_layout, data, _get_points_by_month,
                                     need_min_temperature=need_min_temperature,
                                     need_max_temperature=need_max_temperature,
                                     need_average_temperature=need_average_temperature)


def show_diagram_by_several_months(main_window: QtWidgets.QMainWindow,
                                   vertical_layout: QtWidgets.QVBoxLayout,
                                   data: dict,
                                   need_min_temperature=False,
                                   need_max_temperature=False,
                                   need_average_temperature=False) -> None:
    _show_diagram_by_points_function(main_window, vertical_layout, data, _get_points_by_several_months,
                                     need_min_temperature=need_min_temperature,
                                     need_max_temperature=need_max_temperature,
                                     need_average_temperature=need_average_temperature)


def show_diagram_by_several_all_data(main_window: QtWidgets.QMainWindow,
                                     vertical_layout: QtWidgets.QVBoxLayout,
                                     data: dict,
                                     need_min_temperature=False,
                                     need_max_temperature=False,
                                     need_average_temperature=False) -> None:
    _show_diagram_by_points_function(main_window, vertical_layout, data, _get_points_by_all_data,
                                     need_min_temperature=need_min_temperature,
                                     need_max_temperature=need_max_temperature,
                                     need_average_temperature=need_average_temperature)
