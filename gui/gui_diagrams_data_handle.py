from typing import Callable, Any, Tuple

from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QListWidgetItem

from gui.gui_diagrams_plot import remove_diagrams, show_diagram_by_month, show_diagram_by_several_months, \
    show_diagram_by_several_all_data
from gui.main_window import Ui_main_window


def gui_init_diagrams_data_handle(ui: Ui_main_window,
                                  main_window: QtWidgets.QMainWindow,
                                  get_data: Callable[[], dict],
                                  get_anomaly_data: Callable[[], dict],
                                  get_station_name: Callable[[], str],
                                  is_trained: Callable[[], bool],
                                  get_trained_on: Callable[[], Tuple[bool, bool, bool]],
                                  need_show_min: Callable[[], bool],
                                  need_show_max: Callable[[], bool],
                                  need_show_average: Callable[[], bool],
                                  set_show_min: Callable[[bool], None],
                                  set_show_max: Callable[[bool], None],
                                  set_show_average: Callable[[bool], None]) -> Callable[[], None]:
    select_period_type_combo_box = ui.select_period_type_combo_box
    diagram_vertical_layout = ui.diagram_vertical_layout
    periods_list_widget = ui.periods_list_widget
    select_observation_for_anomaly_combo_box = ui.select_observation_for_anomaly_combo_box

    current_data_dict = {}
    current_anomaly_data_dict = {}
    current_period_type_index = 0
    current_period_index = ""

    def get_anomaly_text() -> str:
        if select_observation_for_anomaly_combo_box.currentText() == "Min temperature":
            return "min"
        elif select_observation_for_anomaly_combo_box.currentText() == "Max temperature":
            return "max"
        elif select_observation_for_anomaly_combo_box.currentText() == "Average temperature":
            return "average"
        return "none"

    def reset_periods_list() -> None:
        periods_list_widget.clear()

    def reset_periods() -> None:
        nonlocal current_period_index
        current_period_index = ""

        current_data_dict.clear()
        current_anomaly_data_dict.clear()
        reset_periods_list()

    def add_item_to_periods(key: str) -> None:
        new_list_widget_item = QListWidgetItem(key)

        colors = ["#7fc97f", "#ffb200", "#ff1f00"]

        if is_trained():
            anomaly_text = get_anomaly_text()
            if anomaly_text == "min":
                current_anomaly_value = current_anomaly_data_dict[key]["min"][1]
                new_list_widget_item.setBackground(QColor(colors[current_anomaly_value]))
            elif anomaly_text == "max":
                current_anomaly_value = current_anomaly_data_dict[key]["max"][1]
                new_list_widget_item.setBackground(QColor(colors[current_anomaly_value]))
            elif anomaly_text == "average":
                current_anomaly_value = current_anomaly_data_dict[key]["average"][1]
                new_list_widget_item.setBackground(QColor(colors[current_anomaly_value]))

        periods_list_widget.addItem(new_list_widget_item)

    def fill_periods_list():
        reset_periods_list()

        for key in current_data_dict:
            add_item_to_periods(key)

    def fill_periods_by_months() -> None:
        for key in get_data():
            current_key = key + "m"
            current_data_dict[current_key] = get_data()[key]

            if is_trained():
                current_anomaly_data_dict[current_key] = get_anomaly_data()[key]

    def split_data_by_years_and_months(data: dict) -> dict:
        years_and_months_data = {}

        for key in data:
            year = key[:4]
            month = key[-2:]

            if year in years_and_months_data:
                years_and_months_data[year][month] = (data[key], year)
            else:
                years_and_months_data[year] = {month: (data[key], year)}
        return years_and_months_data

    def get_seasons(years_and_months_data: dict, seasons_data: dict) -> None:
        for key in years_and_months_data:
            current_data = years_and_months_data[key]

            last_winter = {}
            last_winter_name = str(int(key) - 1) + "-" + key + "_winter"
            if last_winter_name in seasons_data:
                last_winter = seasons_data[last_winter_name]

            if "01" in current_data:
                last_winter["01"] = current_data["01"]
            if "02" in current_data:
                last_winter["02"] = current_data["02"]

            if len(last_winter) > 0:
                seasons_data[last_winter_name] = last_winter

            spring = {}

            if "03" in current_data:
                spring["03"] = current_data["03"]
            if "04" in current_data:
                spring["04"] = current_data["04"]
            if "05" in current_data:
                spring["05"] = current_data["05"]

            if len(spring) > 0:
                seasons_data[key + "_spring"] = spring

            summer = {}

            if "06" in current_data:
                summer["06"] = current_data["06"]
            if "07" in current_data:
                summer["07"] = current_data["07"]
            if "08" in current_data:
                summer["08"] = current_data["08"]

            if len(summer) > 0:
                seasons_data[key + "_summer"] = summer

            fall = {}

            if "09" in current_data:
                fall["09"] = current_data["09"]
            if "10" in current_data:
                fall["10"] = current_data["10"]
            if "11" in current_data:
                fall["11"] = current_data["11"]

            if len(fall) > 0:
                seasons_data[key + "_fall"] = fall

            winter = {}
            winter_name = key + "-" + str(int(key) + 1) + "_winter"

            if "12" in current_data:
                winter["12"] = current_data["12"]

            if len(winter) > 0:
                seasons_data[winter_name] = winter

    def get_max_anomaly_by_seasons(seasons: dict) -> dict:
        new_seasons = {}

        for season in seasons:
            new_seasons[season] = {}
            if get_trained_on()[0]:
                max_anomaly = 0
                for key in seasons[season]:
                    max_anomaly = max(max_anomaly, seasons[season][key][0]["min"][1])
                new_seasons[season]["min"] = (seasons[season], max_anomaly)

            if get_trained_on()[1]:
                max_anomaly = 0
                for key in seasons[season]:
                    max_anomaly = max(max_anomaly, seasons[season][key][0]["max"][1])
                new_seasons[season]["max"] = (seasons[season], max_anomaly)

            if get_trained_on()[2]:
                max_anomaly = 0
                for key in seasons[season]:
                    max_anomaly = max(max_anomaly, seasons[season][key][0]["average"][1])
                new_seasons[season]["average"] = (seasons[season], max_anomaly)

        return new_seasons

    def get_max_anomaly_by_years(years: dict) -> dict:
        new_years = {}

        for year in years:
            new_years[year] = {}
            if get_trained_on()[0]:
                max_anomaly = 0
                for key in years[year]:
                    max_anomaly = max(max_anomaly, years[year][key][0]["min"][1])
                new_years[year]["min"] = (years[year], max_anomaly)
            if get_trained_on()[1]:
                max_anomaly = 0
                for key in years[year]:
                    max_anomaly = max(max_anomaly, years[year][key][0]["max"][1])
                new_years[year]["max"] = (years[year], max_anomaly)
            if get_trained_on()[2]:
                max_anomaly = 0
                for key in years[year]:
                    max_anomaly = max(max_anomaly, years[year][key][0]["average"][1])
                new_years[year]["average"] = (years[year], max_anomaly)

        return new_years

    def get_max_anomaly_by_all_data(years: dict) -> dict:
        new_years = {}

        if get_trained_on()[0]:
            max_anomaly = 0
            for year in years:
                for key in years[year]:
                    max_anomaly = max(max_anomaly, years[year][key][0]["min"][1])
            new_years["min"] = (years, max_anomaly)

        if get_trained_on()[1]:
            max_anomaly = 0
            for year in years:
                for key in years[year]:
                    max_anomaly = max(max_anomaly, years[year][key][0]["max"][1])
            new_years["max"] = (years, max_anomaly)

        if get_trained_on()[2]:
            max_anomaly = 0
            for year in years:
                for key in years[year]:
                    max_anomaly = max(max_anomaly, years[year][key][0]["average"][1])
            new_years["average"] = (years, max_anomaly)

        return new_years

    def fill_periods_by_season() -> None:
        years_and_months_data = split_data_by_years_and_months(get_data())
        seasons_data = {}
        get_seasons(years_and_months_data, seasons_data)

        anomaly_seasons_data = {}
        if is_trained():
            years_and_months_anomaly_data = split_data_by_years_and_months(get_anomaly_data())
            get_seasons(years_and_months_anomaly_data, anomaly_seasons_data)
            anomaly_seasons_data = get_max_anomaly_by_seasons(anomaly_seasons_data)

        for key in seasons_data:
            current_data_dict[key] = seasons_data[key]
            if is_trained():
                current_anomaly_data_dict[key] = anomaly_seasons_data[key]

    def fill_periods_by_years() -> None:
        years_and_months_data = split_data_by_years_and_months(get_data())

        years_and_months_anomaly_data = {}
        if is_trained():
            years_and_months_anomaly_data = split_data_by_years_and_months(get_anomaly_data())
            years_and_months_anomaly_data = get_max_anomaly_by_years(years_and_months_anomaly_data)

        for key in years_and_months_data:
            current_key = key + "y"
            current_data_dict[current_key] = years_and_months_data[key]
            if is_trained():
                current_anomaly_data_dict[current_key] = years_and_months_anomaly_data[key]

    def fill_periods_by_all_data() -> None:
        years_and_months_data = split_data_by_years_and_months(get_data())

        years_and_months_anomaly_data = {}
        if is_trained():
            years_and_months_anomaly_data = split_data_by_years_and_months(get_anomaly_data())
            years_and_months_anomaly_data = get_max_anomaly_by_all_data(years_and_months_anomaly_data)

        current_key = "All"
        current_data_dict[current_key] = years_and_months_data

        if is_trained():
            current_anomaly_data_dict[current_key] = years_and_months_anomaly_data

    def update_diagram() -> None:
        remove_diagrams(diagram_vertical_layout)

        need_min_temperature = need_show_min()
        need_max_temperature = need_show_max()
        need_average_temperature = need_show_average()

        if not need_min_temperature and not need_max_temperature and not need_average_temperature:
            return

        if current_period_index == "(None)" or current_period_index == "":
            return

        current_data = (main_window, diagram_vertical_layout, current_data_dict[current_period_index],
                        {}, get_anomaly_text(), get_station_name(),
                        need_min_temperature, need_max_temperature, need_average_temperature)

        if is_trained():
            current_data = (main_window, diagram_vertical_layout, current_data_dict[current_period_index],
                            current_anomaly_data_dict[current_period_index], get_anomaly_text(), get_station_name(),
                            need_min_temperature, need_max_temperature, need_average_temperature)

        if current_period_type_index == 1:
            show_diagram_by_month(*current_data)

        elif current_period_type_index == 2:
            show_diagram_by_several_months(*current_data)

        elif current_period_type_index == 3:
            show_diagram_by_several_months(*current_data)

        elif current_period_type_index == 4:
            show_diagram_by_several_all_data(*current_data)

    def on_period_type_combo_box_index_changed(index: int) -> None:
        nonlocal current_period_type_index
        current_period_type_index = index

        reset_periods()
        remove_diagrams(diagram_vertical_layout)

        if index <= 0:
            return

        if index == 1:
            fill_periods_by_months()
        elif index == 2:
            fill_periods_by_season()
        elif index == 3:
            fill_periods_by_years()
        elif index == 4:
            fill_periods_by_all_data()

        fill_periods_list()

    # noinspection PyUnusedLocal
    def on_periods_list_index_changed(index: Any) -> None:
        nonlocal current_period_index
        if periods_list_widget.currentItem() is None:
            current_period_index = "(None)"
        else:
            current_period_index = periods_list_widget.currentItem().text()

        update_diagram()

    def set_observation_check_boxes_to(is_min_checked=False, is_max_checked=False, is_average_checked=False):
        set_show_min(is_min_checked)
        set_show_max(is_max_checked)
        set_show_average(is_average_checked)

    # noinspection PyUnusedLocal
    def on_observation_for_anomaly_index_changed(index: int):
        fill_periods_list()

        anomaly_text = get_anomaly_text()

        if anomaly_text == 'min':
            set_observation_check_boxes_to(is_min_checked=True)
        elif anomaly_text == 'max':
            set_observation_check_boxes_to(is_max_checked=True)
        elif anomaly_text == 'average':
            set_observation_check_boxes_to(is_average_checked=True)
        else:
            set_observation_check_boxes_to(is_min_checked=True, is_max_checked=True, is_average_checked=True)

        update_diagram()

    select_period_type_combo_box.currentIndexChanged.connect(on_period_type_combo_box_index_changed)
    periods_list_widget.clicked.connect(on_periods_list_index_changed)
    select_observation_for_anomaly_combo_box.currentIndexChanged.connect(on_observation_for_anomaly_index_changed)

    return update_diagram
