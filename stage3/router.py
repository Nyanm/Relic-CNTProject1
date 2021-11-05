# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'router.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Switch(object):
    def setupUi(self, Switch):
        Switch.setObjectName("Switch")
        Switch.resize(289, 490)
        self.centralwidget = QtWidgets.QWidget(Switch)
        self.centralwidget.setObjectName("centralwidget")
        self.route_table = QtWidgets.QTableWidget(self.centralwidget)
        self.route_table.setGeometry(QtCore.QRect(10, 120, 271, 331))
        self.route_table.setObjectName("route_table")
        self.route_table.setColumnCount(2)
        self.route_table.setRowCount(1)
        item = QtWidgets.QTableWidgetItem()
        self.route_table.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.route_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.route_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.route_table.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.route_table.setItem(0, 1, item)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(-50, 90, 501, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.label_icon = QtWidgets.QLabel(self.centralwidget)
        self.label_icon.setGeometry(QtCore.QRect(70, 10, 151, 20))
        self.label_icon.setObjectName("label_icon")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(80, 50, 128, 25))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_id = QtWidgets.QLabel(self.layoutWidget)
        self.label_id.setObjectName("label_id")
        self.horizontalLayout.addWidget(self.label_id)
        self.num_id = QtWidgets.QLCDNumber(self.layoutWidget)
        self.num_id.setObjectName("num_id")
        self.horizontalLayout.addWidget(self.num_id)
        Switch.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(Switch)
        self.statusbar.setObjectName("statusbar")
        Switch.setStatusBar(self.statusbar)

        self.retranslateUi(Switch)
        QtCore.QMetaObject.connectSlotsByName(Switch)

    def retranslateUi(self, Switch):
        _translate = QtCore.QCoreApplication.translate
        Switch.setWindowTitle(_translate("Switch", "Switch"))
        item = self.route_table.verticalHeaderItem(0)
        item.setText(_translate("Switch", "0"))
        item = self.route_table.horizontalHeaderItem(0)
        item.setText(_translate("Switch", "Destionation"))
        item = self.route_table.horizontalHeaderItem(1)
        item.setText(_translate("Switch", "PORT"))
        __sortingEnabled = self.route_table.isSortingEnabled()
        self.route_table.setSortingEnabled(False)
        item = self.route_table.item(0, 0)
        item.setText(_translate("Switch", "7"))
        item = self.route_table.item(0, 1)
        item.setText(_translate("Switch", "ALL"))
        self.route_table.setSortingEnabled(__sortingEnabled)
        self.label_icon.setText(_translate("Switch", "\"Should be an icon here\""))
        self.label_id.setText(_translate("Switch", "My ID"))

