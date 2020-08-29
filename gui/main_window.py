# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyqt5_design.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_main_window(object):
    def setupUi(self, main_window):
        main_window.setObjectName("main_window")
        main_window.resize(1753, 640)
        main_window.setMinimumSize(QtCore.QSize(982, 566))
        self.centralwidget = QtWidgets.QWidget(main_window)
        self.centralwidget.setObjectName("centralwidget")
        self.controller_frame = QtWidgets.QFrame(self.centralwidget)
        self.controller_frame.setGeometry(QtCore.QRect(10, 0, 341, 621))
        self.controller_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.controller_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.controller_frame.setObjectName("controller_frame")
        self.station_id_label = QtWidgets.QLabel(self.controller_frame)
        self.station_id_label.setGeometry(QtCore.QRect(10, 60, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.station_id_label.setFont(font)
        self.station_id_label.setObjectName("station_id_label")
        self.station_id_line_edit = QtWidgets.QLineEdit(self.controller_frame)
        self.station_id_line_edit.setGeometry(QtCore.QRect(10, 100, 161, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.station_id_line_edit.setFont(font)
        self.station_id_line_edit.setObjectName("station_id_line_edit")
        self.select_training_observations_group_box = QtWidgets.QGroupBox(self.controller_frame)
        self.select_training_observations_group_box.setGeometry(QtCore.QRect(10, 280, 321, 121))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.select_training_observations_group_box.setFont(font)
        self.select_training_observations_group_box.setObjectName("select_training_observations_group_box")
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.select_training_observations_group_box)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(9, 20, 301, 91))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.select_training_observation_vertical_layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.select_training_observation_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.select_training_observation_vertical_layout.setObjectName("select_training_observation_vertical_layout")
        self.extract_data_push_button = QtWidgets.QPushButton(self.controller_frame)
        self.extract_data_push_button.setGeometry(QtCore.QRect(10, 140, 131, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.extract_data_push_button.setFont(font)
        self.extract_data_push_button.setObjectName("extract_data_push_button")
        self.data_extraction_status_text_label = QtWidgets.QLabel(self.controller_frame)
        self.data_extraction_status_text_label.setGeometry(QtCore.QRect(10, 190, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.data_extraction_status_text_label.setFont(font)
        self.data_extraction_status_text_label.setObjectName("data_extraction_status_text_label")
        self.data_extraction_status_value_label = QtWidgets.QLabel(self.controller_frame)
        self.data_extraction_status_value_label.setGeometry(QtCore.QRect(10, 220, 321, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.data_extraction_status_value_label.setFont(font)
        self.data_extraction_status_value_label.setText("")
        self.data_extraction_status_value_label.setObjectName("data_extraction_status_value_label")
        self.site_text_label = QtWidgets.QLabel(self.controller_frame)
        self.site_text_label.setGeometry(QtCore.QRect(10, 20, 47, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.site_text_label.setFont(font)
        self.site_text_label.setObjectName("site_text_label")
        self.site_hyperlink_label = QtWidgets.QLabel(self.controller_frame)
        self.site_hyperlink_label.setGeometry(QtCore.QRect(50, 20, 131, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.site_hyperlink_label.setFont(font)
        self.site_hyperlink_label.setTextFormat(QtCore.Qt.RichText)
        self.site_hyperlink_label.setOpenExternalLinks(True)
        self.site_hyperlink_label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.site_hyperlink_label.setObjectName("site_hyperlink_label")
        self.training_status_value_label = QtWidgets.QLabel(self.controller_frame)
        self.training_status_value_label.setGeometry(QtCore.QRect(10, 490, 321, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.training_status_value_label.setFont(font)
        self.training_status_value_label.setText("")
        self.training_status_value_label.setObjectName("training_status_value_label")
        self.training_status_text_label = QtWidgets.QLabel(self.controller_frame)
        self.training_status_text_label.setGeometry(QtCore.QRect(10, 460, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.training_status_text_label.setFont(font)
        self.training_status_text_label.setObjectName("training_status_text_label")
        self.train_push_button = QtWidgets.QPushButton(self.controller_frame)
        self.train_push_button.setGeometry(QtCore.QRect(10, 410, 131, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.train_push_button.setFont(font)
        self.train_push_button.setObjectName("train_push_button")
        self.line = QtWidgets.QFrame(self.controller_frame)
        self.line.setGeometry(QtCore.QRect(0, 260, 341, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.diagram_frame = QtWidgets.QFrame(self.centralwidget)
        self.diagram_frame.setEnabled(False)
        self.diagram_frame.setGeometry(QtCore.QRect(350, 0, 1381, 621))
        self.diagram_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.diagram_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.diagram_frame.setObjectName("diagram_frame")
        self.select_period_type_combo_box = QtWidgets.QComboBox(self.diagram_frame)
        self.select_period_type_combo_box.setGeometry(QtCore.QRect(490, 10, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.select_period_type_combo_box.setFont(font)
        self.select_period_type_combo_box.setObjectName("select_period_type_combo_box")
        self.select_period_type_combo_box.addItem("")
        self.select_period_type_combo_box.addItem("")
        self.select_period_type_combo_box.addItem("")
        self.select_period_type_combo_box.addItem("")
        self.select_period_type_combo_box.addItem("")
        self.select_period_type_label = QtWidgets.QLabel(self.diagram_frame)
        self.select_period_type_label.setGeometry(QtCore.QRect(350, 10, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.select_period_type_label.setFont(font)
        self.select_period_type_label.setObjectName("select_period_type_label")
        self.select_period_label = QtWidgets.QLabel(self.diagram_frame)
        self.select_period_label.setGeometry(QtCore.QRect(350, 50, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.select_period_label.setFont(font)
        self.select_period_label.setObjectName("select_period_label")
        self.select_period_combo_box = QtWidgets.QComboBox(self.diagram_frame)
        self.select_period_combo_box.setGeometry(QtCore.QRect(490, 50, 221, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.select_period_combo_box.setFont(font)
        self.select_period_combo_box.setObjectName("select_period_combo_box")
        self.select_period_combo_box.addItem("")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.diagram_frame)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 140, 1361, 471))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.diagram_vertical_layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.diagram_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.diagram_vertical_layout.setObjectName("diagram_vertical_layout")
        self.select_diagram_observations_group_box = QtWidgets.QGroupBox(self.diagram_frame)
        self.select_diagram_observations_group_box.setGeometry(QtCore.QRect(10, 10, 321, 121))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.select_diagram_observations_group_box.setFont(font)
        self.select_diagram_observations_group_box.setObjectName("select_diagram_observations_group_box")
        self.verticalLayoutWidget_3 = QtWidgets.QWidget(self.select_diagram_observations_group_box)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(9, 20, 301, 91))
        self.verticalLayoutWidget_3.setObjectName("verticalLayoutWidget_3")
        self.select_diagram_observation_vertical_layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_3)
        self.select_diagram_observation_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.select_diagram_observation_vertical_layout.setObjectName("select_diagram_observation_vertical_layout")
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setGeometry(QtCore.QRect(340, 0, 21, 621))
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        main_window.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)
        self.actionkk = QtWidgets.QAction(main_window)
        self.actionkk.setObjectName("actionkk")

        self.retranslateUi(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("main_window", "Weather anomaly detection"))
        self.station_id_label.setText(_translate("main_window", "Station ID"))
        self.station_id_line_edit.setText(_translate("main_window", "UPM00033345"))
        self.select_training_observations_group_box.setTitle(_translate("main_window", "Select observations for training"))
        self.extract_data_push_button.setText(_translate("main_window", "Extract data"))
        self.data_extraction_status_text_label.setText(_translate("main_window", "Data extraction status:"))
        self.site_text_label.setText(_translate("main_window", "Site:"))
        self.site_hyperlink_label.setText(_translate("main_window", "<a href=\"https://gis.ncdc.noaa.gov/maps/ncei/cdo/daily\">gis.ncdc.noaa.gov</a>"))
        self.training_status_text_label.setText(_translate("main_window", "Training status:"))
        self.train_push_button.setText(_translate("main_window", "Train"))
        self.select_period_type_combo_box.setItemText(0, _translate("main_window", "(None)"))
        self.select_period_type_combo_box.setItemText(1, _translate("main_window", "Month"))
        self.select_period_type_combo_box.setItemText(2, _translate("main_window", "Season"))
        self.select_period_type_combo_box.setItemText(3, _translate("main_window", "Year"))
        self.select_period_type_combo_box.setItemText(4, _translate("main_window", "All"))
        self.select_period_type_label.setText(_translate("main_window", "Select period type"))
        self.select_period_label.setText(_translate("main_window", "Select period"))
        self.select_period_combo_box.setItemText(0, _translate("main_window", "(None)"))
        self.select_diagram_observations_group_box.setTitle(_translate("main_window", "Select observations for showing diagram"))
        self.actionkk.setText(_translate("main_window", "kk"))
        self.actionkk.setStatusTip(_translate("main_window", "hi"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    ui = Ui_main_window()
    ui.setupUi(main_window)
    main_window.show()
    sys.exit(app.exec_())
