import requests
import datetime
import numpy as np


class Info:
    def __init__(self):
        self.day = 0
        self.max = 0
        self.min = 0
        self.precipitation = 0

    def __str__(self):
        return "{}: {}, {}, {}".format(self.day, self.max, self.min, self.precipitation)


def handle_data_to_files(
        station_id,
        need_min_max_temperature,
        need_precipitation,
        event_list,
        on_error,
        on_status_changed,
        on_finished):

    def add_event(function, *args, **kwargs):
        event_list.append(lambda: function(*args, **kwargs))

    site_path = "https://www.ncei.noaa.gov/access/services/data/v1?"
    dataset = "dataset=daily-summaries"

    data_types = "&dataTypes="
    data_types += "TMAX,TMIN," if need_min_max_temperature else ""
    data_types += "PRCP," if need_precipitation else ""
    if need_min_max_temperature or need_precipitation:
        data_types = data_types[:-1]
    else:
        data_types = ""

    stations = "&stations=" + str(station_id)
    start_date = "&startDate=1800-01-01"
    end_date = "&endDate=3000-01-01"
    include_attributes = "&includeAttributes=false"
    units = "&units=metric"
    output_format = "&format=json"

    url = \
        site_path + dataset + data_types + stations + start_date + end_date + include_attributes + units + output_format

    add_event(on_status_changed, "Getting data from site")

    request = requests.get(url)
    data_json = request.json()

    if len(data_json) == 0:
        add_event(on_error, "Entered station doesn't exist!")
        return

    data = {}

    min_temperature = 10000
    max_temperature = 0
    max_precipitation = 0

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
        if need_min_max_temperature and 'TMIN' in current_data:
            min_value = float(current_data['TMIN']) + 273.15
            min_temperature = min(min_temperature, min_value)

        max_value = 100000
        if need_min_max_temperature and 'TMAX' in current_data:
            max_value = float(current_data['TMAX']) + 273.15
            max_temperature = max(max_temperature, max_value)

        precipitation = 100000
        if need_precipitation and 'PRCP' in current_data:
            precipitation = float(current_data['PRCP'])
            max_precipitation = max(max_precipitation, precipitation)

        info.max = min_value
        info.min = max_value
        info.precipitation = precipitation

        if name in data:
            data[name].append(info)
        else:
            data[name] = [info]

    add_event(on_status_changed, "Saving data to files")

    for key in data:
        current_data = data[key]
        length = len(current_data)

        sorted(current_data, key=lambda current_info: current_info.day)

        size = 1
        size += 2 if need_min_max_temperature else 0
        size += 1 if need_precipitation else 0

        out_data = np.zeros((length, size))

        for i in range(length):
            info = current_data[i]
            offset = 0
            out_data[i][offset] = info.day
            offset += 1

            if need_min_max_temperature:
                out_data[i][offset] = info.min
                offset += 1

                out_data[i][offset] = info.max
                offset += 1

            if need_precipitation:
                out_data[i][offset] = info.precipitation
                offset += 1

        out_data.tofile("data/" + key, sep=',')

    print(min_temperature)
    print(max_temperature)
    print(max_precipitation)

    print("Finished")

    add_event(on_status_changed, "Finished")
    add_event(on_finished, data)
