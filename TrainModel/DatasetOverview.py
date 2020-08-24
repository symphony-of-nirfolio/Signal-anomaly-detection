import numpy as np
import matplotlib.pyplot as plt
from PIL import Image


MIN_YEAR = 1899
MAX_YEAR = 2020
COLUMN_SIZE = 4


def read_from_file(file_name, vals_len):
    data = np.fromfile(file_name, sep=',')
    return np.reshape(data, (data.shape[0]//vals_len, vals_len))


def plot_points_for_array(ax, data, column):
    for i in range(data.shape[0]):
        if data[i, column] < 1000:
            ax[0].plot(data[i, 0], data[i, column], 'bo')


def merge_all_years(SIZE, count_column, start_year, end_year, month):
    all_data = np.empty(0)
    for i in range(start_year, end_year+1, 1):
        try:
            file_name = 'data/' + str(i) + '_' + month
            data = read_from_file(file_name, SIZE)
            all_data = np.append(all_data, data[:, count_column])
        except:
            continue

    all_data = all_data[10000 > all_data]
    return all_data


def plot_all_data(ax, SIZE, count_column, start_year, end_year, month):
    all_data = merge_all_years(SIZE, count_column, start_year, end_year, month)

    all_data = all_data[10000 > all_data]
    # all_data = all_data[0 < all_data]

    unique, counts = np.unique(all_data, return_counts=True)
    ax_id = count_column - 1
    ax[ax_id].plot(unique, counts, 'b')


def print_type(column_type):
    if column_type == 0:
        return "MIN_TEMP"
    if column_type == 1:
        return "MAX_TEMP"
    if column_type == 2:
        return "PRECIPITATION"


def main_get_plots():
    fig, ax = plt.subplots(COLUMN_SIZE-1)

    for i in range(COLUMN_SIZE-1):
        plot_all_data(ax, 4, i+1, MIN_YEAR, MAX_YEAR, '07')

    plt.show()


def main_get_min_max_info():
    for i in range(12):
        str_month = str(i+1) if i+1 > 9 else '0' + str(i+1)
        file = open('all_info/' + str_month + '.txt', "w")
        for j in range(3):
            data = merge_all_years(COLUMN_SIZE, j+1, MIN_YEAR, MAX_YEAR, str_month)
            plt.clf()
            res = plt.boxplot(data, vert=False)
            # plt.show()
            file.write(print_type(j) + '\n')
            file.write(str(res['caps'][0].get_data()[0][0]))
            file.write(',')
            file.write(str(res['caps'][1].get_data()[0][0]))
            file.write(',')
            file.write('\n\n')

        file.close()


def count_min_max_size_for_each_month():
    for i in range(12):
        str_month = str(i+1) if i+1 > 9 else '0' + str(i+1)
        file = open('all_info/' + str_month + '.txt', "r")
        print(str_month)
        for j in range(COLUMN_SIZE-1):
            line = file.readline()
            if not line.startswith(print_type(j)):
                line = file.readline()
            line = file.readline()
            vals = line.split(sep=',')
            min_size = 10000
            min_pos = -1
            max_pos = -1
            max_size = 0
            # print(float(vals[0]))
            # print(float(vals[1]))
            for k in range(MIN_YEAR, MAX_YEAR, 1):
                try:
                    data = read_from_file('data/' + str(k) + '_' + str_month, COLUMN_SIZE)
                    # print(data.shape)
                    cur = data[:, j+1]
                    # print(str(cur.shape) + ' ' + str(float(vals[0])) + ' ' + str(float(vals[1])))
                    cur = cur[cur >= float(vals[0])]
                    cur = cur[cur <= float(vals[1])]
                    # print(len(cur))
                    if min_size > len(cur) > 0:
                        min_size = len(cur)
                        min_pos = k
                    if max_size < len(cur):
                        max_size = len(cur)
                        max_pos = k
                except:
                    continue
            print(print_type(j) + ': ' + str(min_size) + ', ' + str(min_pos) + '; ' + str(max_size) + ', ' + str(max_pos))


def get_vals_from_all_info(file_name):
    file = open('all_info/' + file_name, "r")
    line = file.readline()
    line = file.readline()
    values_min = line.split(sep=',')
    line = file.readline()
    line = file.readline()
    line = file.readline()
    values_max = line.split(sep=',')
    return [float(values_min[0]), float(values_min[1])], [float(values_max[0]), float(values_max[1])]


def get_plot():
    min_temp, max_temp = get_vals_from_all_info('01.txt')

    for year in range(MIN_YEAR, MAX_YEAR, 1):
        try:
            data = read_from_file('data/' + str(year) + '_01', 4)
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
            wrong = np.empty(0)
            for i in range(data.shape[0]):
                if not min_temp[1] > data[i, 1] > min_temp[0] or not max_temp[1] > data[i, 2] > max_temp[0]:
                    wrong = np.append(wrong, i)
            for i in range(wrong.shape[0]):
                data = np.delete(data, int(wrong[i] - i), axis=0)
            ax.set_ylim([260, 310])
            ax.set_facecolor('black')
            fig.patch.set_facecolor('black')
            ax.plot(data[:, 0], data[:, 1], c='w', linewidth=5.3)
            ax.plot(data[:, 0], data[:, 2], c='w', linewidth=5.3)
            fig.savefig('temp_graphics/01/' + str(year) + '.png', dpi=15)
            fig.close()
        except:
            continue



# main_get_plots()
# main_get_min_max_info()
# count_min_max_size_for_each_month()
get_plot()
