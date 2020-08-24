import sys
import matplotlib
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit, QMessageBox

from gui.worker import Worker
from handle_data.handle_data import handle_data_to_files

matplotlib.use('Qt5Agg')


def main_ui():
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle('Weather anomaly detection')
    window.setGeometry(700, 350, 400, 400)

    label = QtWidgets.QLabel(window)
    label.setText("Enter Station id")
    label.move(20, 0)

    status_text = "Status: "

    status_label = QtWidgets.QLabel(window)
    status_label.setText(status_text)
    status_label.move(20, 120)
    status_label.resize(280, 20)

    text_box = QLineEdit(window)
    text_box.setText("USC00080228")
    text_box.move(20, 30)
    text_box.resize(280, 20)

    button = QPushButton('Get data', window)
    button.move(20, 90)

    thread_pool = QThreadPool()

    event_list = []

    def run_event():
        if len(event_list) > 0:
            function = event_list[0]
            function()

            event_list.pop(0)

    event_list_runner = QtCore.QTimer()
    event_list_runner.timeout.connect(run_event)
    event_list_runner.start(10)

    def on_error(message):
        QMessageBox.warning(window, 'Warning', message, QMessageBox.Ok)

    def on_status_changed(status):
        status_label.setText(status_text + status)

    def on_click():
        textbox_value = text_box.text()
        thread = Worker(handle_data_to_files, textbox_value, event_list, on_error, on_status_changed)
        thread_pool.start(thread)

    # noinspection PyUnresolvedReferences
    button.clicked.connect(on_click)

    window.show()
    sys.exit(app.exec_())
