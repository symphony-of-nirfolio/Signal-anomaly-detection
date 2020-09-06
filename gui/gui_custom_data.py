from typing import Callable

from PyQt5 import QtWidgets, QtCore

from gui.custom_data_window import Ui_custom_data_window
from gui.gui_diagrams_plot import remove_diagrams, show_diagram_by_month
from handle_data.data_management import get_anomaly_from_data
from handle_data.info import Info


def gui_init_custom_data(ui: Ui_custom_data_window,
                         window: QtWidgets.QMainWindow) -> (QtWidgets.QComboBox, Callable[[], None]):
    sliders_horizontal_layout = ui.sliders_horizontal_layout
    observation_combo_box = ui.observation_combo_box
    season_type_combo_box = ui.season_type_combo_box
    data_size_spin_box = ui.data_size_spin_box
    default_value_double_spin_box = ui.default_value_double_spin_box
    reset_push_button = ui.reset_push_button
    update_limits_push_button = ui.update_limits_push_button
    diagram_vertical_layout = ui.diagram_vertical_layout
    min_temperature_double_spin_box = ui.min_temperature_double_spin_box
    max_temperature_double_spin_box = ui.max_temperature_double_spin_box

    value_sliders = []

    current_min_limit = min_temperature_double_spin_box.value()
    current_max_limit = max_temperature_double_spin_box.value()

    def get_anomaly_text() -> str:
        if observation_combo_box.currentText() == "Min temperature":
            return "min"
        elif observation_combo_box.currentText() == "Max temperature":
            return "max"
        elif observation_combo_box.currentText() == "Average temperature":
            return "average"
        return "none"

    def get_season() -> int:
        if season_type_combo_box.currentText() == "Winter":
            return 0
        if season_type_combo_box.currentText() == "Spring":
            return 1
        if season_type_combo_box.currentText() == "Summer":
            return 2
        if season_type_combo_box.currentText() == "Fall":
            return 3
        return -1

    def get_min_limit() -> float:
        return min_temperature_double_spin_box.value()

    def get_max_limit() -> float:
        return max_temperature_double_spin_box.value()

    def get_default_value() -> float:
        return default_value_double_spin_box.value()

    def value_from_slider_value_with_min_max(value: float, min_limit: float, max_limit: float) -> float:
        return min_limit + (value / 100.0) * (max_limit - min_limit)

    def value_from_slider_value(value: int) -> float:
        return value_from_slider_value_with_min_max(value, current_min_limit, current_max_limit)

    def value_to_slider_value_with_min_max(value: float, min_limit: float, max_limit: float) -> int:
        return int(100.0 * (value - min_limit) / (max_limit - min_limit))

    def get_data_from_sliders() -> list:
        anomaly_text = get_anomaly_text()
        if anomaly_text == "none":
            return []

        data = []
        for i in range(len(value_sliders)):
            info = Info()
            info.day = i + 1
            if anomaly_text == "min":
                info.min = value_from_slider_value(value_sliders[i].value()) + 273.15
            if anomaly_text == "max":
                info.max = value_from_slider_value(value_sliders[i].value()) + 273.15
            if anomaly_text == "average":
                info.average = value_from_slider_value(value_sliders[i].value()) + 273.15
            data.append(info)

        return data

    def update_diagram() -> None:
        remove_diagrams(diagram_vertical_layout)

        data = get_data_from_sliders()
        season = get_season()
        anomaly_text = get_anomaly_text()
        if len(data) == 0 or season == -1 or anomaly_text == "none":
            return

        anomaly_data = get_anomaly_from_data(data, anomaly_text, season)

        min_max_average_tuple = (False, False, False)
        if anomaly_text == "min":
            min_max_average_tuple = (True, False, False)
        if anomaly_text == "max":
            min_max_average_tuple = (False, True, False)
        if anomaly_text == "average":
            min_max_average_tuple = (False, False, True)

        show_diagram_by_month(window,
                              diagram_vertical_layout,
                              data,
                              anomaly_data,
                              anomaly_text,
                              "Custom Data",
                              min_max_average_tuple[0],
                              min_max_average_tuple[1],
                              min_max_average_tuple[2])

    def reset_sliders(need_save_value: bool) -> None:
        nonlocal value_sliders, current_min_limit, current_max_limit

        data_size = data_size_spin_box.value()
        min_limit = get_min_limit()
        max_limit = get_max_limit()
        default_value = get_default_value()

        for i in reversed(range(sliders_horizontal_layout.count())):
            sliders_horizontal_layout.itemAt(i).widget().deleteLater()

        if not need_save_value:
            value_sliders.clear()

        for i in range(data_size):
            vertical_slider = QtWidgets.QSlider()
            vertical_slider.setMinimumSize(QtCore.QSize(20, 100))
            vertical_slider.setMaximumSize(QtCore.QSize(20, 100))
            vertical_slider.setMinimum(0)
            vertical_slider.setMaximum(100)

            if need_save_value:
                vertical_slider.setSliderPosition(
                    value_to_slider_value_with_min_max(
                        value_from_slider_value_with_min_max(value_sliders[i].value(),
                                                             current_min_limit,
                                                             current_max_limit),
                        min_limit,
                        max_limit))
            else:
                vertical_slider.setSliderPosition(value_to_slider_value_with_min_max(default_value,
                                                                                     min_limit,
                                                                                     max_limit))

            vertical_slider.setOrientation(QtCore.Qt.Vertical)
            vertical_slider.setObjectName("verticalSlider")
            vertical_slider.valueChanged.connect(update_diagram)
            sliders_horizontal_layout.addWidget(vertical_slider)
            if need_save_value:
                value_sliders[i] = vertical_slider
            else:
                value_sliders.append(vertical_slider)

        current_min_limit = get_min_limit()
        current_max_limit = get_max_limit()

        update_diagram()

    def on_update_limits_push_button_clicked() -> None:
        reset_sliders(True)

    def on_limits_value_changed() -> None:
        min_limit = get_min_limit()
        max_limit = get_max_limit()

        if min_limit < max_limit:
            update_limits_push_button.setEnabled(True)
            update_limits_push_button.setToolTip(None)
            reset_push_button.setEnabled(True)
            reset_push_button.setToolTip(None)
        else:
            update_limits_push_button.setEnabled(False)
            update_limits_push_button.setToolTip("Min temperature more than max")
            reset_push_button.setEnabled(False)
            reset_push_button.setToolTip("Min temperature more than max")

    def on_reset_push_button_clicked() -> None:
        reset_sliders(False)

    reset_push_button.clicked.connect(on_reset_push_button_clicked)
    update_limits_push_button.clicked.connect(on_update_limits_push_button_clicked)
    season_type_combo_box.currentIndexChanged.connect(lambda index: update_diagram())
    observation_combo_box.currentIndexChanged.connect(lambda index: update_diagram())
    default_value_double_spin_box.valueChanged.connect(on_limits_value_changed)
    min_temperature_double_spin_box.valueChanged.connect(on_limits_value_changed)
    max_temperature_double_spin_box.valueChanged.connect(on_limits_value_changed)

    return observation_combo_box
