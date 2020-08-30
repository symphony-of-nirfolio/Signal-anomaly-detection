import requests
import datetime
import numpy as np

from handle_data.data_management import create_directory_for_station, write_stations_info_to_json
from handle_data.info import Info


def handle_data_to_files(
        stations_info,
        station_id,
        event_list,
        on_error,
        on_status_changed,
        on_finished):

    def add_event(function, *args, **kwargs):
        event_list.append(lambda: function(*args, **kwargs))

    site_path = "https://www.ncei.noaa.gov/access/services/data/v1?"
    dataset = "dataset=daily-summaries"
    data_types = "&dataTypes=TMAX,TMIN,TAVG"
    stations = "&stations=" + str(station_id)
    start_date = "&startDate=1800-01-01"
    end_date = "&endDate=3000-01-01"
    include_attributes = "&includeAttributes=false"
    units = "&units=metric"
    output_format = "&format=json"

    url = \
        site_path + dataset + data_types + stations + start_date + end_date + include_attributes + units + output_format

    add_event(on_status_changed, "Extracting data from site")

    # TODO: make it's better
    try:
        request = requests.get(url)
        data_json = request.json()
    except requests.exceptions.RequestException as e:
        add_event(on_error, str(e))
        return

    if len(data_json) == 0:
        add_event(on_error, "Entered station doesn't exist!")
        return

    if request.status_code != 200:
        add_event(on_error, "Bad status code: {}!".format(request.status_code))
        return

    data = {}

    min_temperature = 10000
    max_temperature = 0

    contain_min_temperature = False
    contain_max_temperature = False
    contain_average_temperature = False

    add_event(on_status_changed, "Parsing data")

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

        info.max = min_value
        info.min = max_value
        info.average = average_value

        if name in data:
            data[name].append(info)
        else:
            data[name] = [info]

    add_event(on_status_changed, "Saving data to files")

    path = create_directory_for_station(station_id)

    is_trained = False
    if station_id in stations_info:
        is_trained = stations_info[station_id]["is_trained"]

    stations_info[station_id] =\
        {
            "need_min": contain_min_temperature,
            "need_max": contain_max_temperature,
            "need_average": contain_average_temperature,
            "is_trained": is_trained
        }
    write_stations_info_to_json(stations_info)

    for key in data:
        current_data = data[key]
        length = len(current_data)

        sorted(current_data, key=lambda current_info: current_info.day)

        size = 4
        out_data = np.zeros((length, size))

        for i in range(length):
            info = current_data[i]

            out_data[i][0] = info.day
            out_data[i][1] = info.min
            out_data[i][2] = info.max
            out_data[i][3] = info.average

        out_data.tofile(path + "/" + key, sep=',')

    print("Min of min temperatures: {}".format(min_temperature))
    print("Max of max temperatures: {}".format(max_temperature))

    print("Contain min: {}, Contain max: {}, Contain average: {}".format(
        contain_min_temperature,
        contain_max_temperature,
        contain_average_temperature))

    print("Finished")

    add_event(on_status_changed, "Finished")
    add_event(on_finished, data, contain_min_temperature, contain_max_temperature, contain_average_temperature)
