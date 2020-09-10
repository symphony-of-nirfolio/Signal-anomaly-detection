from typing import Callable

from PyQt5 import QtWidgets


def reset_observation(available_observations_vertical_layout: QtWidgets.QVBoxLayout) -> None:
    for i in reversed(range(available_observations_vertical_layout.count())):
        available_observations_vertical_layout.itemAt(i).widget().deleteLater()


def set_observation(available_observations_vertical_layout: QtWidgets.QVBoxLayout,
                    on_observation_check_box_state_changed: Callable[[int], None],
                    need_min: bool,
                    need_max: bool,
                    need_average: bool,
                    is_min_checked=True,
                    is_max_checked=True,
                    is_average_checked=True) -> (QtWidgets.QCheckBox, QtWidgets.QCheckBox, QtWidgets.QCheckBox):
    max_temperature_check_box = None
    if need_max:
        max_temperature_check_box = QtWidgets.QCheckBox()
        max_temperature_check_box.setText("Max temperature")
        max_temperature_check_box.setChecked(is_max_checked)
        max_temperature_check_box.setObjectName("max_temperature_check_box")
        max_temperature_check_box.stateChanged.connect(on_observation_check_box_state_changed)
        available_observations_vertical_layout.addWidget(max_temperature_check_box)

    average_temperature_check_box = None
    if need_average:
        average_temperature_check_box = QtWidgets.QCheckBox()
        average_temperature_check_box.setText("Average temperature")
        average_temperature_check_box.setChecked(is_average_checked)
        average_temperature_check_box.setObjectName("average_temperature_check_box")
        average_temperature_check_box.stateChanged.connect(on_observation_check_box_state_changed)
        available_observations_vertical_layout.addWidget(average_temperature_check_box)

    min_temperature_check_box = None
    if need_min:
        min_temperature_check_box = QtWidgets.QCheckBox()
        min_temperature_check_box.setText("Min temperature")
        min_temperature_check_box.setChecked(is_min_checked)
        min_temperature_check_box.setObjectName("min_temperature_check_box")
        min_temperature_check_box.stateChanged.connect(on_observation_check_box_state_changed)
        available_observations_vertical_layout.addWidget(min_temperature_check_box)

    return min_temperature_check_box, max_temperature_check_box, average_temperature_check_box
