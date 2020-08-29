import matplotlib
from datetime import date
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

matplotlib.use('Qt5Agg')


def remove_diagrams(vertical_layout):
    for i in reversed(range(vertical_layout.count())):
        vertical_layout.itemAt(i).widget().deleteLater()


def create_diagram_canvas(main_window, vertical_layout):
    figure = Figure(figsize=(5, 4), dpi=100)
    figure_canvas = FigureCanvasQTAgg(figure)
    figure_canvas.axes = figure.add_subplot(111)

    toolbar = NavigationToolbar2QT(figure_canvas, main_window)

    vertical_layout.addWidget(figure_canvas)
    vertical_layout.addWidget(toolbar)

    return figure_canvas


def get_min_form_info(info):
    return info.min


def get_max_form_info(info):
    return info.max


def get_average_from_info(info):
    return info.average


def get_data_points(data, offset, get_data_from_info, data_offset=0.0):
    days = []
    observations = []

    for info in data:
        observation = get_data_from_info(info)
        if observation < 100000.0:
            days.append(info.day + offset)
            observations.append(observation + data_offset)

    return days, observations


def get_min_points(data, offset):
    return get_data_points(data, offset, get_min_form_info, data_offset=-273.15)


def get_max_points(data, offset):
    return get_data_points(data, offset, get_max_form_info, data_offset=-273.15)


def get_average_points(data, offset):
    return get_data_points(data, offset, get_average_from_info, data_offset=-273.15)


def get_points_by_month(data, get_points):
    return get_points(data, 0)


def calculate_offset(year, month):
    month_begin = date(int(year), int(month), 1)
    next_month_begin = date(
        int(year) if month != "12" else int(year) + 1,
        int(month) + 1 if month != "12" else 1,
        1)

    days = (next_month_begin - month_begin).days
    return days


def get_points_by_several_months(data, get_points):
    days_all = []
    observations_all = []

    offset = 0
    for key in data:
        days, observations = get_points(data[key][0], offset)
        days_all += days
        observations_all += observations

        offset += calculate_offset(data[key][1], key)

    return days_all, observations_all


def get_points_by_all_data(data, get_points):
    days_all = []
    observations_all = []

    offset = 0
    for year in data:
        current_data = data[year]

        for key in current_data:
            days, observations = get_points(current_data[key][0], offset)
            days_all += days
            observations_all += observations

            offset += calculate_offset(current_data[key][1], key)

    return days_all, observations_all


def show_diagram_by_points_function(main_window, vertical_layout, data, get_points,
                                    need_min_temperature=False,
                                    need_max_temperature=False,
                                    need_average_temperature=False):
    figure_canvas = create_diagram_canvas(main_window, vertical_layout)

    size = 0
    days = []
    observations = []
    colors = []

    if need_min_temperature:
        days_form_min, min_temperature = get_points(data, get_min_points)
        days.append(days_form_min)
        observations.append(min_temperature)
        colors.append('r')
        size += 1

    if need_max_temperature:
        days_form_max, max_temperature = get_points(data, get_max_points)
        days.append(days_form_max)
        observations.append(max_temperature)
        colors.append('y')
        size += 1

    if need_average_temperature:
        days_form_average, average_temperature = get_points(data, get_average_points)
        days.append(days_form_average)
        observations.append(average_temperature)
        colors.append('m')
        size += 1

    for i in range(size):
        figure_canvas.axes.plot(days[i], observations[i], colors[i])


def show_diagram_by_month(main_window, vertical_layout, data,
                          need_min_temperature=False,
                          need_max_temperature=False,
                          need_average_temperature=False):
    show_diagram_by_points_function(main_window, vertical_layout, data, get_points_by_month,
                                    need_min_temperature=need_min_temperature,
                                    need_max_temperature=need_max_temperature,
                                    need_average_temperature=need_average_temperature)


def show_diagram_by_several_months(main_window, vertical_layout, data,
                                   need_min_temperature=False,
                                   need_max_temperature=False,
                                   need_average_temperature=False):
    show_diagram_by_points_function(main_window, vertical_layout, data, get_points_by_several_months,
                                    need_min_temperature=need_min_temperature,
                                    need_max_temperature=need_max_temperature,
                                    need_average_temperature=need_average_temperature)


def show_diagram_by_several_all_data(main_window, vertical_layout, data,
                                     need_min_temperature=False,
                                     need_max_temperature=False,
                                     need_average_temperature=False):
    show_diagram_by_points_function(main_window, vertical_layout, data, get_points_by_all_data,
                                    need_min_temperature=need_min_temperature,
                                    need_max_temperature=need_max_temperature,
                                    need_average_temperature=need_average_temperature)
