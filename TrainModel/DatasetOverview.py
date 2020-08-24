import numpy as np
import matplotlib.pyplot as plt


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
            # plot_points_for_array(ax, data, count_column)
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
            file.write('\n\n')

        file.close()


# main_get_plots()
main_get_min_max_info()
