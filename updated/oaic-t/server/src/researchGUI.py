# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import QWidget, QFileDialog, QInputDialog, QAbstractItemView, QTableWidget, QTableWidgetItem, \
    QListWidgetItem, QMessageBox
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys
import time
from test_task import TestTask


class Ui_MainWindow(QWidget):

    def set_actor_manager(self, actor_manager):
        self.actor_manager = actor_manager

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.showMaximized()
        MainWindow.setStyleSheet("background-color: rgb(229, 227, 206);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(17, 350, 761, 20))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(104, 104, 104))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(104, 104, 104))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(104, 104, 104))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(104, 104, 104))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(104, 104, 104))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(104, 104, 104))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(104, 104, 104))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(104, 104, 104))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(104, 104, 104))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.line.setPalette(palette)
        self.line.setLineWidth(2)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.actorList = QtWidgets.QListWidget(self.centralwidget)
        self.actorList.setGeometry(QtCore.QRect(10, 180, 200, 161))
        self.actorList.setStyleSheet("background-color: rgb(224, 224, 224);")
        self.actorList.setEditTriggers(
            QtWidgets.QAbstractItemView.EditKeyPressed | QtWidgets.QAbstractItemView.SelectedClicked)
        self.actorList.setObjectName("actorList")
        self.scriptList = QtWidgets.QListWidget(self.centralwidget)
        self.scriptList.setGeometry(QtCore.QRect(290, 180, 221, 161))
        self.scriptList.setStyleSheet("background-color: rgb(224, 224, 224);")
        self.scriptList.setObjectName("scriptList")
        self.addButton = QtWidgets.QPushButton(self.centralwidget)
        self.addButton.setGeometry(QtCore.QRect(570, 180, 141, 28))
        self.addButton.setStyleSheet("background-color: rgb(190, 208, 166);")
        self.addButton.setObjectName("addButton")
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setGeometry(QtCore.QRect(570, 250, 141, 28))
        self.startButton.setStyleSheet("background-color: rgb(190, 208, 166);")
        self.startButton.setObjectName("startButton")
        self.taskLogs = QtWidgets.QTextBrowser(self.centralwidget)
        self.taskLogs.setGeometry(QtCore.QRect(290, 420, 491, 350))
        self.taskLogs.setStyleSheet("background-color: rgb(224, 224, 224);")
        self.taskLogs.setObjectName("taskLogs")
        # self.stopButton = QtWidgets.QPushButton(self.centralwidget)
        # self.stopButton.setGeometry(QtCore.QRect(20, 800, 93, 28))
        # self.stopButton.setStyleSheet("background-color: rgb(153, 153, 255);")
        # self.stopButton.setObjectName("stopButton")
        # self.removeButton = QtWidgets.QPushButton(self.centralwidget)
        # self.removeButton.setGeometry(QtCore.QRect(150, 800, 93, 28))
        # self.removeButton.setStyleSheet("background-color: rgb(153, 153, 255);")
        # self.removeButton.setObjectName("removeButton")
        self.actor_label = QtWidgets.QLabel(self.centralwidget)
        self.actor_label.setGeometry(QtCore.QRect(30, 160, 161, 16))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(True)
        font.setUnderline(False)
        font.setWeight(75)
        self.actor_label.setFont(font)
        self.actor_label.setObjectName("actor_label")
        self.files_label = QtWidgets.QLabel(self.centralwidget)
        self.files_label.setGeometry(QtCore.QRect(290, 160, 161, 16))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.files_label.setFont(font)
        self.files_label.setObjectName("files_label")
        self.tasks_label = QtWidgets.QLabel(self.centralwidget)
        self.tasks_label.setGeometry(QtCore.QRect(20, 390, 161, 21))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.tasks_label.setFont(font)
        self.tasks_label.setObjectName("tasks_label")
        self.logs_label = QtWidgets.QLabel(self.centralwidget)
        self.logs_label.setGeometry(QtCore.QRect(290, 390, 161, 21))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.logs_label.setFont(font)
        self.logs_label.setObjectName("logs_label")
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setGeometry(QtCore.QRect(810, 20, 20, 981))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(104, 104, 104))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(104, 104, 104))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(104, 104, 104))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(104, 104, 104))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(104, 104, 104))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(104, 104, 104))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(104, 104, 104))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(104, 104, 104))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(104, 104, 104))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
        self.line_2.setPalette(palette)
        self.line_2.setLineWidth(2)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.graphWidget1 = PlotWidget(self.centralwidget, background=(224,255,255))
        self.graphWidget1.setGeometry(QtCore.QRect(1030, 120, 750, 340))
        self.graphWidget1.setObjectName("graphWidget1")
        self.graphWidget1.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Plain)
        CHART_MARGINS = (0, 0, 20, 5)
        self.graphWidget1.showGrid(x=True, y=True)
        self.graphWidget1.setXRange(0, 5, padding=0)

        self.graphWidget2 = PlotWidget(self.centralwidget, background=(224,255,255))
        self.graphWidget2.setGeometry(QtCore.QRect(1030, 500, 750, 340))
        self.graphWidget2.setObjectName("graphWidget2")
        self.graphWidget2.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Plain)
        self.graphWidget2.showGrid(x=True, y=True)
        self.graphWidget2.setXRange(1, 10, padding=0)
        self.graphWidget2.setXRange(0, 10, padding=0)

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(1040, 480, 200, 21))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(1040, 100, 500, 21))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(10, 10, 481, 141))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap("oaic-t_logo.png"))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName("label_2")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(10, 420, 200, 350))
        self.tableWidget.setStyleSheet("background-color: rgb(224, 224, 224);")
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(1, item)

        self.dropDown1 = QtWidgets.QComboBox(self.centralwidget)
        self.dropDown1.setGeometry(QtCore.QRect(840, 120, 171, 22))
        self.dropDown1.setStyleSheet("background-color: rgb(204, 229, 255);")
        self.dropDown1.setObjectName("dropDown1")
        self.dropDown2 = QtWidgets.QComboBox(self.centralwidget)
        self.dropDown2.setGeometry(QtCore.QRect(840, 500, 171, 22))
        self.dropDown2.setStyleSheet("background-color: rgb(204, 229, 255);")
        self.dropDown2.setObjectName("dropDown2")
        self.dropDown2.currentIndexChanged.connect(self.kpi_plot_updated)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1920, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # Internal memory
        self.selected_lists = []
        self.load_test_files = []
        self.listOfActors = []
        self.count = 0
        self.tableCount = 0
        self.graphX = []
        self.graphY = []
        self.logRole = QtCore.Qt.UserRole + 1
        self.graphRoleX = QtCore.Qt.UserRole + 2
        self.graphRoleY = QtCore.Qt.UserRole + 3

        self.actor_rsc_all = dict()

        self.test_task_all = dict()
        self.test_task_updater = TestTaskUpdater()
        self.actor_updater = ActorUpdater()
        self.actor_updater.rsc_updated.connect(self.on_actor_rsc_updated)
        self.actor_updater.kpi_updated.connect(self.on_actor_kpi_updated)
        self.kpi_names = []
        self.ts_all = []
        self.kpi_all = dict()
        self.test_task_updater.status_changed.connect(self.on_status_updated)
        self.test_task_updater.log_changed.connect(self.on_log_updated)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.actorList.setSortingEnabled(True)
        self.addButton.setText(_translate("MainWindow", "Load Test Scripts"))
        self.startButton.setText(_translate("MainWindow", "Start A New Test"))
        # self.stopButton.setText(_translate("MainWindow", "Stop"))
        # self.removeButton.setText(_translate("MainWindow", "Remove"))
        self.actor_label.setText(_translate("MainWindow", "Actors"))
        self.files_label.setText(_translate("MainWindow", "Test Script Files"))
        self.tasks_label.setText(_translate("MainWindow", "Active Test Tasks"))
        self.logs_label.setText(_translate("MainWindow", "Logs"))
        self.label.setText(_translate("MainWindow", "KPI Metrics in gNodeB"))
        self.label_3.setText(_translate("MainWindow", "CPU Usage (Percent) in Actor"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Test Task"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Status"))

        # Add Button Logic
        self.addButton.clicked.connect(self.addToScript)

        # Actor List Logic
        self.actorList.setSelectionMode(QAbstractItemView.MultiSelection)

        # Test Script List Logic
        self.scriptList.setSelectionMode(QAbstractItemView.MultiSelection)

        # Start Button Logic
        self.startButton.clicked.connect(self.activeTestSave)

        # Test Task List Logic
        self.tableWidget.itemClicked.connect(self.showLogs)

    # Functions called outside of GUI
    def addActor(self, actor):
        self.actorList.addItem(actor)
        self.dropDown1.addItem(actor)

    def removeActor(self, actor):
        remAcList = self.actorList.findItems(actor, Qt.MatchExactly)
        remAcDrop = self.dropDown1.findText(actor)
        for foo in remAcList:
            self.actorList.takeItem(self.actorList.row(foo))
        self.dropDown1.removeItem(remAcDrop)

    @QtCore.pyqtSlot(str, float, float)
    def on_actor_rsc_updated(self, actor_name, actor_rsc_cpu, actor_rsc_mem):
        if actor_name in self.actor_rsc_all.keys():
            old_value = self.actor_rsc_all[actor_name]
            new_value = old_value.copy() + [actor_rsc_cpu]
            self.data1_x = list(range(len(new_value)))
            self.data1_y = new_value
            new_dic = {actor_name: new_value}
            self.actor_rsc_all.update(new_dic)
        else:
            new_value = [actor_rsc_cpu]
            self.actor_rsc_all[actor_name] = new_value
            self.data1_y = new_value
            self.data1_x = list(range(len(new_value)))

        current_actor_name = self.dropDown1.currentText()
        if current_actor_name == actor_name:
            #self.graphWidget1.clear()
            pen = pg.mkPen(color='b')
            self.graphWidget1.setXRange(max(self.data1_x[-1]-10, 0), self.data1_x[-1] + 5, padding=0)
            self.graphWidget1.setYRange(max(min(self.data1_y) - 0.2 * min(self.data1_y), 0),
                                        min(max(self.data1_y) + 0.2 * max(self.data1_y), 100), padding=0)
            if len(new_value) > 10:
                # print(self.data1_x)
                self.data1_line.setData(self.data1_x, self.data1_y)
            else:
                self.data1_line = self.graphWidget1.plot(self.data1_x, self.data1_y, name='CPU', pen=pen, symbol='o', symbolSize=8, symbolBrush=('b'))


    def actor_rsc_updated(self, actor_name, actor_rsc_cpu, actor_rsc_mem):
        self.actor_updater.rsc_updated.emit(actor_name, actor_rsc_cpu, actor_rsc_mem)

    def plot_kpi(self):
        current_selected = self.dropDown2.currentText()
        data_plot = self.kpi_all[current_selected]

        # print(data_plot)
        self.data2_x = list(range(len(data_plot)))
        pen = pg.mkPen(color='b')
        self.graphWidget2.setXRange(max(self.data2_x[-1] - 10, 0), self.data2_x[-1] + 5, padding=0)
        self.graphWidget2.setYRange(max(min(data_plot) - 0.2 * min(data_plot), 0),
                                    min(max(data_plot) + 0.2 * max(data_plot), 500), padding=0)

        self.data2_line = self.graphWidget2.plot(self.data2_x, data_plot, name='KPI', pen=pen, symbol='o',
                                                     symbolSize=8, symbolBrush=('b'))

    def kpi_plot_updated(self):
        self.graphWidget2.clear()
        self.plot_kpi()

    @QtCore.pyqtSlot(str, bool)
    def on_actor_kpi_updated(self, timestamp, flag):
        # print("received kpi: " + timestamp)
        # print(self.kpi_all_update)

        self.ts_all = self.ts_all.copy() + [timestamp]
        first_input_flag = len(self.kpi_all) == 0
        for k in self.kpi_all_update.keys():
            if self.kpi_all.__contains__(k):
                old_value = self.kpi_all[k]
                new_value = old_value.copy() + [self.kpi_all_update[k]]
                self.kpi_all[k] = new_value
            else:
                self.kpi_all[k] = [self.kpi_all_update[k]]
                self.dropDown2.addItem(k)
        if first_input_flag:
            self.dropDown2.setCurrentIndex(0)

        self.plot_kpi()


    def actor_kpi_updated(self, timestamp, kpi_all):
        self.kpi_all_update = kpi_all
        self.actor_updater.kpi_updated.emit(timestamp, True)

    @QtCore.pyqtSlot(str, int)
    def on_log_updated(self, log, row_index):
        if self.tableWidget.currentRow() == (row_index - 1):
            self.taskLogs.clear()
            self.taskLogs.append(log)

    def logs_updated(self, test_task):
        (row_index, item_first, item_second) = self.test_task_all[test_task]
        self.test_task_updater.log_changed.emit(test_task.log, row_index)

    def update_status(self, task_id, status):
        pass

    def addGraphData(self, xData, yData):
        index = self.dropDown1.currentIndex()
        self.dropDown1.setItemData(index, xData, self.graphRoleX)
        self.dropDown1.setItemData(index, yData, self.graphRoleY)

    @QtCore.pyqtSlot(str, int)
    def on_status_updated(self, status, row_index):
        tableStatus = QTableWidgetItem(status)
        if (status == 'Pending'):
            tableStatus.setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        if (status == 'Running'):
            tableStatus.setForeground(QtGui.QBrush(QtGui.QColor(128, 128, 0)))
        if (status == 'Completed'):
            tableStatus.setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 128)))
        if (status == 'Failed'):
            tableStatus.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
        self.tableWidget.setItem(row_index - 1, 1, tableStatus)

    def status_updated(self, test_task):
        ## emit a signal to allow GUI update
        (row_index, item_first, item_second) = self.test_task_all[test_task]
        self.test_task_updater.status_changed.emit(test_task.status, row_index)

    def getActors(self):
        foo = self.tableWidget.currentItem()
        self.listOfActors = str(foo.data(QtCore.Qt.UserRole))

    # used for testing
    def printout(self):
        print(self.listOfActors)

    # Functions within the GUI
    def addToScript(self):
        #path = QFileDialog.getOpenFileName()
        #filename = path
        # filename = path[0].split("/")[-1]
        filename, _filter = QFileDialog.getOpenFileName(None, "Select one or more files to open", ".", "JSON (*.json)")
        ## check if the file is already included in the list
        if filename in self.load_test_files:
            pass
        else:
            self.scriptList.addItem(filename)
            self.load_test_files.append(filename)

    def activeTestSave(self):
        self.selected_lists.clear()
        self.selected_lists.append([item.text() for item in self.actorList.selectedItems()])
        self.selected_lists.append([item.text() for item in self.scriptList.selectedItems()])

        selected_actors = [item.text() for item in self.actorList.selectedItems()]
        selected_tests = [item.text() for item in self.scriptList.selectedItems()]

        if not selected_actors:
            QMessageBox.about(self, "Error", "At least one actor should be selected!")
            return
        if len(selected_actors) > 1:
            QMessageBox.about(self, "Error", "Only one actor should be selected! Multiple actors testing will be supported soon!")
            return

        if not selected_tests:
            QMessageBox.about(self, "Error", "At least one test script should be selected!")
            return

        if len(selected_tests) > 1:
            QMessageBox.about(self, "Error", "Only one test script should be selected! Multiple test scripts will be supported soon!")
            return

        test_name, ok = QInputDialog.getText(self, 'Text Input Dialog', 'Enter a name for your Test Task:')
        if ok:
            ## TODO: check if the test_name is not used before.

            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            item_first = QTableWidgetItem(str(test_name))
            self.tableWidget.setItem(self.count, 0, item_first)
            item_first.setData(QtCore.Qt.UserRole, self.selected_lists)
            self.tableWidget.setCurrentItem(item_first)

            item_second = QTableWidgetItem("Pending")
            self.tableWidget.setItem(self.count, 1, item_second)
            item_second.setData(QtCore.Qt.UserRole, self.selected_lists)

            self.count = self.count + 1
            test_task = TestTask(selected_actors, selected_tests, str(self.count))
            ## TODO: generate a test task for each selected actor
            self.add_test_task(test_task, self.tableWidget.rowCount(), item_first, item_second)
            self.actor_manager.start_test_task(test_task)

    def add_test_task(self, test_task, row_index, item_first, item_second):
        self.test_task_all[test_task] = (row_index, item_first, item_second)

    def showLogs(self):
        self.taskLogs.clear()
        foo = self.tableWidget.currentItem()
        ## find test task with the currentrow
        for test_task in self.test_task_all:
            (row_index, item_first, item_second) = self.test_task_all[test_task]
            if self.tableWidget.currentRow() == row_index - 1:
                break

        self.taskLogs.append(test_task.log)

    def showGraph(self):
        self.graphWidget1.clear()
        index = self.dropDown1.currentIndex()
        self.graphWidget1.plot(self.dropDown1.itemData(index, self.graphRoleX),
                               self.dropDown1.itemData(index, self.graphRoleY))


class TestTaskUpdater(QObject):
    status_changed = pyqtSignal(str, int)
    log_changed = pyqtSignal(str, int)


class ActorUpdater(QObject):
    rsc_updated = pyqtSignal(str, float, float)
    kpi_updated = pyqtSignal(str, bool)  #ts, kpi_name1, kpi_val1, ..., 3

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
