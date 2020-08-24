import numpy as np
import matplotlib.pyplot as plt


def read_from_file(file_name, vals_len):
    data = np.fromfile(file_name, sep=',')
    return np.reshape(data, (data.shape[0]//vals_len, vals_len))


def plot_points_for_array(ax, data, column):
    for i in range(data.shape[0]):
        if data[i, column] < 1000:
            ax[0].plot(data[i, 0], data[i, column], 'bo')


def plot_all_data(ax, SIZE, count_column, start_year, end_year, month):
    all_data = np.empty(0)
    for i in range(start_year, end_year+1, 1):
        try:
            file_name = 'data/' + str(i) + '_' + month
            data = read_from_file(file_name, SIZE)
            # plot_points_for_array(ax, data, count_column)
            all_data = np.append(all_data, data[:, count_column])
        except:
            continue
    all_data = np.sort(all_data)
    all_data = all_data[10000 > all_data]
    all_data = all_data[0 < all_data]
    unique, counts = np.unique(all_data, return_counts=True)

    ax_id = count_column - 1
    ax[ax_id].plot(unique, counts, 'b')


def main():
    fig, ax = plt.subplots(3)

    for i in range(3):
        plot_all_data(ax, 4, i+1, 1899, 2020, '07')

    plt.show()


main()
