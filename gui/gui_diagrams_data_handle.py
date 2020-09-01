from typing import Callable

from PyQt5 import QtWidgets

from gui.gui_diagrams_plot import remove_diagrams, show_diagram_by_month, show_diagram_by_several_months, \
    show_diagram_by_several_all_data
from gui.main_window import Ui_main_window


def gui_init_diagrams_data_handle(ui: Ui_main_window,
                                  main_window: QtWidgets.QMainWindow,
                                  get_data: Callable[[], dict],
                                  need_show_min: Callable[[], bool],
                                  need_show_max: Callable[[], bool],
                                  need_show_average: Callable[[], bool]) -> Callable[[], None]:
    select_period_combo_box = ui.select_period_combo_box
    select_period_type_combo_box = ui.select_period_type_combo_box
    diagram_vertical_layout = ui.diagram_vertical_layout

    current_data_list = []
    current_period_type_index = 0
    current_period_index = 0

    def reset_period_combo_box() -> None:
        select_period_combo_box.clear()
        select_period_combo_box.addItem("(None)")

        current_data_list.clear()
        current_data_list.append(None)

    def fill_periods_by_months() -> None:
        for key in get_data():
            select_period_combo_box.addItem(key + "m")
            current_data_list.append(get_data()[key])

    def split_data_by_years_and_months() -> dict:
        years_and_months_data = {}

        for key in get_data():
            year = key[:4]
            month = key[-2:]

            if year in years_and_months_data:
                years_and_months_data[year][month] = (get_data()[key], year)
            else:
                years_and_months_data[year] = {month: (get_data()[key], year)}
        return years_and_months_data

    def get_seasons(years_and_months_data, seasons_data) -> None:
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

    def fill_periods_by_season() -> None:
        years_and_months_data = split_data_by_years_and_months()
        seasons_data = {}
        get_seasons(years_and_months_data, seasons_data)

        for key in seasons_data:
            select_period_combo_box.addItem(key)
            current_data_list.append(seasons_data[key])

    def fill_periods_by_years() -> None:
        years_and_months_data = split_data_by_years_and_months()

        for key in years_and_months_data:
            select_period_combo_box.addItem(key + "y")
            current_data_list.append(years_and_months_data[key])

    def fill_periods_by_all_data() -> None:
        years_and_months_data = split_data_by_years_and_months()

        select_period_combo_box.addItem("All")
        current_data_list.append(years_and_months_data)

    def update_diagram() -> None:
        remove_diagrams(diagram_vertical_layout)

        need_min_temperature = need_show_min()
        need_max_temperature = need_show_max()
        need_average_temperature = need_show_average()

        if not need_min_temperature and not need_max_temperature and not need_average_temperature:
            return

        current_data = (main_window, diagram_vertical_layout, {}, need_min_temperature, need_max_temperature,
                        need_average_temperature)
        if current_period_index > 0:
            current_data = (main_window, diagram_vertical_layout, current_data_list[current_period_index],
                            need_min_temperature, need_max_temperature, need_average_temperature)

        if current_period_type_index == 1 and current_period_index > 0:
            show_diagram_by_month(*current_data)

        elif current_period_type_index == 2 and current_period_index > 0:
            show_diagram_by_several_months(*current_data)

        elif current_period_type_index == 3 and current_period_index > 0:
            show_diagram_by_several_months(*current_data)

        elif current_period_type_index == 4 and current_period_index > 0:
            show_diagram_by_several_all_data(*current_data)

    def on_period_type_combo_box_index_changed(index: int) -> None:
        nonlocal current_period_type_index
        current_period_type_index = index

        reset_period_combo_box()

        if index == 1:
            fill_periods_by_months()
        elif index == 2:
            fill_periods_by_season()
        elif index == 3:
            fill_periods_by_years()
        elif index == 4:
            fill_periods_by_all_data()

    def on_period_combo_box_index_changed(index: int) -> None:
        nonlocal current_period_index
        current_period_index = index

        update_diagram()

    select_period_type_combo_box.currentIndexChanged.connect(on_period_type_combo_box_index_changed)
    select_period_combo_box.currentIndexChanged.connect(on_period_combo_box_index_changed)

    return update_diagram
