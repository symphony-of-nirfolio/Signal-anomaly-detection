import datetime
from typing import Callable

import requests

from handle_data.data_management import write_stations_info_to_json, save_data_to_file,\
    create_directory_for_single_file_station_and_return_file_path
from handle_data.info import Info


def handle_data_to_files(
        stations_info: dict,
        station_id: str,
        on_error: Callable[[str], None],
        on_status_changed: Callable[[str], None],
        on_finished: Callable[[], None]) -> None:
    site_path = "https://www.ncei.noaa.gov/access/services/data/v1?"
    dataset = "dataset=daily-summaries"
    data_types = "&dataTypes=TMAX,TMIN,TAVG"
    stations = "&stations=" + str(station_id)
    start_date = "&startDate=1800-01-01"
    end_date = "&endDate=3000-01-01"
    include_attributes = "&includeAttributes=false"
    units = "&units=metric"
    include_station_name = "&includeStationName=true"
    output_format = "&format=json"

    url = site_path + dataset + data_types + stations + start_date + end_date + include_attributes + units +\
        include_station_name + output_format

    on_status_changed("Extracting data from site")

    # TODO: make it's better
    try:
        request = requests.get(url)
        data_json = request.json()
    except requests.exceptions.RequestException as e:
        on_error(str(e))
        return

    if len(data_json) == 0:
        on_error("Entered station doesn't exist!")
        return

    if request.status_code != 200:
        on_error("Bad status code: {}!".format(request.status_code))
        return

    data = {}

    min_temperature = 10000
    max_temperature = 0

    contain_min_temperature = False
    contain_max_temperature = False
    contain_average_temperature = False

    station_name = ""

    on_status_changed("Parsing data")

    for current_data in data_json:
        date = current_data['DATE']
        date_time = datetime.datetime.strptime(date, '%Y-%m-%d')

        year = date_time.date().year
        month = date_time.date().month
        day = date_time.date().day

        name = "{}_{:02d}".format(year, month)

        info = Info()
        info.day = day

        min_value = 100000
        if 'TMIN' in current_data:
            min_value = float(current_data['TMIN']) + 273.15
            min_temperature = min(min_temperature, min_value)
            contain_min_temperature = True

        max_value = 100000
        if 'TMAX' in current_data:
            max_value = float(current_data['TMAX']) + 273.15
            max_temperature = max(max_temperature, max_value)
            contain_max_temperature = True

        average_value = 100000
        if 'TAVG' in current_data:
            average_value = float(current_data['TAVG']) + 273.15
            contain_average_temperature = True

        if 'NAME' in current_data:
            station_name = current_data['NAME']

        info.min = min_value
        info.max = max_value
        info.average = average_value

        if name in data:
            data[name].append(info)
        else:
            data[name] = [info]

    on_status_changed("Saving data to file")

    is_trained = False
    if station_id in stations_info:
        is_trained = stations_info[station_id]["is_trained"]
    else:
        stations_info[station_id] = {}

    stations_info[station_id]["name"] = station_name
    stations_info[station_id]["need_min"] = contain_min_temperature
    stations_info[station_id]["need_max"] = contain_max_temperature
    stations_info[station_id]["need_average"] = contain_average_temperature
    stations_info[station_id]["is_trained"] = is_trained
    stations_info[station_id]["is_cashed_anomaly_data"] = False

    write_stations_info_to_json(stations_info)

    single_file_path = create_directory_for_single_file_station_and_return_file_path(station_id)
    save_data_to_file(data, single_file_path)

    print("Min of min temperatures: {}".format(min_temperature))
    print("Max of max temperatures: {}".format(max_temperature))

    print("Contain min: {}, Contain max: {}, Contain average: {}".format(
        contain_min_temperature,
        contain_max_temperature,
        contain_average_temperature))

    print("Finished")

    on_status_changed("Finished")
    on_finished()
