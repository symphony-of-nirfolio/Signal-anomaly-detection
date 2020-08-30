from PyQt5 import QtWidgets


def reset_observation(available_observations_vertical_layout):
    for i in reversed(range(available_observations_vertical_layout.count())):
        available_observations_vertical_layout.itemAt(i).widget().deleteLater()


def set_observation(available_observations_vertical_layout, on_observation_check_box_state_changed, need_min, need_max,
                    need_average):
    max_temperature_check_box = None
    if need_max:
        max_temperature_check_box = QtWidgets.QCheckBox()
        max_temperature_check_box.setText("Max temperature")
        max_temperature_check_box.setChecked(True)
        max_temperature_check_box.setObjectName("max_temperature_check_box")
        max_temperature_check_box.stateChanged.connect(on_observation_check_box_state_changed)
        available_observations_vertical_layout.addWidget(max_temperature_check_box)

    average_temperature_check_box = None
    if need_average:
        average_temperature_check_box = QtWidgets.QCheckBox()
        average_temperature_check_box.setText("Average temperature")
        average_temperature_check_box.setChecked(True)
        average_temperature_check_box.setObjectName("average_temperature_check_box")
        average_temperature_check_box.stateChanged.connect(on_observation_check_box_state_changed)
        available_observations_vertical_layout.addWidget(average_temperature_check_box)

    min_temperature_check_box = None
    if need_min:
        min_temperature_check_box = QtWidgets.QCheckBox()
        min_temperature_check_box.setText("Min temperature")
        min_temperature_check_box.setChecked(True)
        min_temperature_check_box.setObjectName("min_temperature_check_box")
        min_temperature_check_box.stateChanged.connect(on_observation_check_box_state_changed)
        available_observations_vertical_layout.addWidget(min_temperature_check_box)

    return min_temperature_check_box, max_temperature_check_box, average_temperature_check_box
