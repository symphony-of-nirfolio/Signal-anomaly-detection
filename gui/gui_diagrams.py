import matplotlib
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


def show_min_max_diagram(main_window, vertical_layout, data):
    figure_canvas = create_diagram_canvas(main_window, vertical_layout)

    days = []
    min_temperature = []
    max_temperature = []

    for info in data:
        if info.min < 100000.0 or info.max < 100000.0:
            days.append(info.day)

        if info.min < 100000.0:
            min_temperature.append(info.min - 273.15)

        if info.max < 100000.0:
            max_temperature.append(info.max - 273.15)

    figure_canvas.axes.plot(days, min_temperature, 'r', days, max_temperature, 'y')


def show_precipitation_diagram(main_window, vertical_layout, data):
    figure_canvas = create_diagram_canvas(main_window, vertical_layout)

    days = []
    precipitation = []

    for info in data:
        if info.precipitation < 100000.0:
            days.append(info.day)
            precipitation.append(info.precipitation)

    figure_canvas.axes.plot(days, precipitation, 'r')
