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


def get_precipitation_form_info(info):
    return info.precipitation


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


def get_precipitation_points(data, offset):
    return get_data_points(data, offset, get_precipitation_form_info)


def show_min_max_diagram_by_month(main_window, vertical_layout, data):
    figure_canvas = create_diagram_canvas(main_window, vertical_layout)

    days_form_min, min_temperature = get_min_points(data, 0)
    days_form_max, max_temperature = get_max_points(data, 0)

    figure_canvas.axes.plot(days_form_min, min_temperature, 'r', days_form_max, max_temperature, 'y')


def show_precipitation_diagram_by_month(main_window, vertical_layout, data):
    figure_canvas = create_diagram_canvas(main_window, vertical_layout)

    days, precipitation = get_precipitation_points(data, 0)

    figure_canvas.axes.plot(days, precipitation, 'r')


def calculate_offset(year, month):
    month_begin = date(int(year), int(month), 1)
    next_month_begin = date(
        int(year) if month != "12" else int(year) + 1,
        int(month) + 1 if month != "12" else 1,
        1)

    days = (next_month_begin - month_begin).days
    return days


def show_min_max_diagram_by_year(main_window, vertical_layout, data):
    figure_canvas = create_diagram_canvas(main_window, vertical_layout)

    days_form_min_all = []
    days_form_max_all = []
    min_temperature_all = []
    max_temperature_all = []

    offset = 0
    for key in data:
        days_form_min, min_temperature = get_min_points(data[key][0], offset)
        days_form_max, max_temperature = get_max_points(data[key][0], offset)
        days_form_min_all += days_form_min
        days_form_max_all += days_form_max
        min_temperature_all += min_temperature
        max_temperature_all += max_temperature

        offset += calculate_offset(data[key][1], key)

    figure_canvas.axes.plot(days_form_min_all, min_temperature_all, 'r', days_form_max_all, max_temperature_all, 'y')


def show_precipitation_diagram_by_year(main_window, vertical_layout, data):
    figure_canvas = create_diagram_canvas(main_window, vertical_layout)

    days_all = []
    precipitations_all = []

    offset = 0
    for key in data:
        days, precipitation = get_precipitation_points(data[key][0], offset)
        days_all += days
        precipitations_all += precipitation

        offset += calculate_offset(data[key][1], key)

    figure_canvas.axes.plot(days_all, precipitations_all, 'r')


def show_min_max_diagram_by_all_data(main_window, vertical_layout, data):
    figure_canvas = create_diagram_canvas(main_window, vertical_layout)

    days_form_min_all = []
    days_form_max_all = []
    min_temperature_all = []
    max_temperature_all = []

    offset = 0
    for year in data:
        current_data = data[year]

        for key in current_data:
            days_form_min, min_temperature = get_min_points(current_data[key][0], offset)
            days_form_max, max_temperature = get_max_points(current_data[key][0], offset)
            days_form_min_all += days_form_min
            days_form_max_all += days_form_max
            min_temperature_all += min_temperature
            max_temperature_all += max_temperature

            offset += calculate_offset(current_data[key][1], key)

    figure_canvas.axes.plot(days_form_min_all, min_temperature_all, 'r', days_form_max_all, max_temperature_all, 'y')


def show_precipitation_diagram_by_all_data(main_window, vertical_layout, data):
    figure_canvas = create_diagram_canvas(main_window, vertical_layout)

    days_all = []
    precipitations_all = []

    offset = 0
    for year in data:
        current_data = data[year]

        for key in current_data:
            days, precipitation = get_precipitation_points(current_data[key][0], offset)
            days_all += days
            precipitations_all += precipitation

            offset += calculate_offset(current_data[key][1], key)

    figure_canvas.axes.plot(days_all, precipitations_all, 'r')
