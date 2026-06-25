# -*- coding: utf-8 -*-

import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QInputDialog,
    QMessageBox,
    QTableWidgetItem,
    QWidget,
)
from pyqtgraph import PlotWidget
import pyqtgraph as pg

from test_task import TestTask


class Ui_MainWindow(QWidget):
    """Main OAIC-T research console.

    Public methods and widget names are intentionally preserved because
    server_main.py and actor_manager.py call into this object directly.
    """

    STATUS_COLORS = {
        "Pending": QtGui.QColor("#64748B"),
        "Running": QtGui.QColor("#B45309"),
        "Completed": QtGui.QColor("#047857"),
        "Failed": QtGui.QColor("#DC2626"),
    }

    def set_actor_manager(self, actor_manager):
        self.actor_manager = actor_manager
        self._update_server_status("Server connected")

    def setupUi(self, MainWindow):
        self._init_state()
        self._setup_window(MainWindow)
        self._setup_styles(MainWindow)
        self._setup_content()
        self._setup_plots()
        self._connect_signals()
        self.retranslateUi(MainWindow)

        MainWindow.setCentralWidget(self.centralwidget)
        MainWindow.setMenuBar(self.menubar)
        MainWindow.setStatusBar(self.statusbar)
        MainWindow.showMaximized()

        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self._update_start_button_state()
        self._update_empty_states()

    def _init_state(self):
        self.actor_manager = None
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

        self.actor_rsc_all = {}
        self.test_task_all = {}
        self.kpi_names = []
        self.ts_all = []
        self.kpi_all = {}
        self.kpi_all_update = {}
        self.data1_x = []
        self.data1_y = []
        self.data2_x = []
        self.data1_line = None
        self.data2_line = None

        self.test_task_updater = TestTaskUpdater()
        self.actor_updater = ActorUpdater()
        self.actor_updater.rsc_updated.connect(self.on_actor_rsc_updated)
        self.actor_updater.kpi_updated.connect(self.on_actor_kpi_updated)
        self.test_task_updater.status_changed.connect(self.on_status_updated)
        self.test_task_updater.log_changed.connect(self.on_log_updated)

    def _setup_window(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1440, 900)
        MainWindow.setMinimumSize(1100, 720)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")

    def _setup_content(self):
        main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        main_layout.setContentsMargins(24, 18, 24, 18)
        main_layout.setSpacing(18)

        main_layout.addWidget(self._build_header())

        self.mainSplitter = QtWidgets.QSplitter(Qt.Horizontal, self.centralwidget)
        self.mainSplitter.setObjectName("mainSplitter")
        self.mainSplitter.setChildrenCollapsible(False)
        self.mainSplitter.addWidget(self._build_controls_panel())
        self.mainSplitter.addWidget(self._build_tasks_panel())
        self.mainSplitter.addWidget(self._build_charts_panel())
        self.mainSplitter.setStretchFactor(0, 1)
        self.mainSplitter.setStretchFactor(1, 2)
        self.mainSplitter.setStretchFactor(2, 3)
        self.mainSplitter.setSizes([320, 430, 620])
        main_layout.addWidget(self.mainSplitter, 1)

    def _build_header(self):
        header = QtWidgets.QFrame(self.centralwidget)
        header.setObjectName("Header")
        layout = QtWidgets.QHBoxLayout(header)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(18)

        self.label_2 = QtWidgets.QLabel(header)
        self.label_2.setObjectName("Logo")
        self.label_2.setMinimumSize(180, 52)
        self.label_2.setMaximumSize(260, 72)
        self.label_2.setScaledContents(True)
        logo_path = os.path.join(os.path.dirname(__file__), "oaic-t_logo.png")
        if os.path.exists(logo_path):
            self.label_2.setPixmap(QtGui.QPixmap(logo_path))
        else:
            self.label_2.setText("OAIC-T")
        layout.addWidget(self.label_2)

        title_box = QtWidgets.QVBoxLayout()
        title_box.setSpacing(2)
        self.titleLabel = QtWidgets.QLabel("OAIC-T Research Console", header)
        self.titleLabel.setObjectName("TitleLabel")
        self.subtitleLabel = QtWidgets.QLabel("Distributed test orchestration and live research metrics", header)
        self.subtitleLabel.setObjectName("SubtitleLabel")
        title_box.addWidget(self.titleLabel)
        title_box.addWidget(self.subtitleLabel)
        layout.addLayout(title_box, 1)

        self.serverStatus = QtWidgets.QLabel("Waiting for server context", header)
        self.serverStatus.setObjectName("StatusPill")
        self.serverStatus.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.serverStatus)

        return header

    def _build_controls_panel(self):
        panel = self._card("Test Setup")
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        self.actor_label = self._section_label("Actors")
        self.actorCountLabel = self._muted_label("No actors registered")
        actor_header = self._label_row(self.actor_label, self.actorCountLabel)
        layout.addLayout(actor_header)

        self.actorList = QtWidgets.QListWidget(panel)
        self.actorList.setObjectName("actorList")
        self.actorList.setSortingEnabled(True)
        self.actorList.setSelectionMode(QAbstractItemView.MultiSelection)
        self.actorList.setEditTriggers(QAbstractItemView.EditKeyPressed | QAbstractItemView.SelectedClicked)
        self.actorList.setAlternatingRowColors(True)
        self.actorList.setToolTip("Select one actor to run a test task.")
        layout.addWidget(self.actorList, 1)

        self.files_label = self._section_label("Test Script Files")
        self.scriptCountLabel = self._muted_label("No scripts loaded")
        script_header = self._label_row(self.files_label, self.scriptCountLabel)
        layout.addLayout(script_header)

        self.scriptList = QtWidgets.QListWidget(panel)
        self.scriptList.setObjectName("scriptList")
        self.scriptList.setSelectionMode(QAbstractItemView.MultiSelection)
        self.scriptList.setAlternatingRowColors(True)
        self.scriptList.setToolTip("Select one JSON test script to run.")
        layout.addWidget(self.scriptList, 1)

        actions = QtWidgets.QHBoxLayout()
        actions.setSpacing(10)
        self.addButton = QtWidgets.QPushButton(panel)
        self.addButton.setObjectName("SecondaryButton")
        self.addButton.setToolTip("Load a JSON test script into the task file list.")
        self.startButton = QtWidgets.QPushButton(panel)
        self.startButton.setObjectName("PrimaryButton")
        self.startButton.setToolTip("Create and start a test task with the selected actor and script.")
        actions.addWidget(self.addButton)
        actions.addWidget(self.startButton)
        layout.addLayout(actions)

        return panel

    def _build_tasks_panel(self):
        panel = self._card("Tasks and Logs")
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        self.tasks_label = self._section_label("Active Test Tasks")
        self.taskCountLabel = self._muted_label("No active tasks")
        layout.addLayout(self._label_row(self.tasks_label, self.taskCountLabel))

        self.tableWidget = QtWidgets.QTableWidget(panel)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(["Test Task", "Status"])
        self.tableWidget.horizontalHeader().setStretchLastSection(False)
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tableWidget.setToolTip("Select a task row to inspect its logs.")
        layout.addWidget(self.tableWidget, 1)

        self.logs_label = self._section_label("Logs")
        self.logHintLabel = self._muted_label("Select a task to view logs")
        layout.addLayout(self._label_row(self.logs_label, self.logHintLabel))

        self.taskLogs = QtWidgets.QTextBrowser(panel)
        self.taskLogs.setObjectName("taskLogs")
        self.taskLogs.setOpenExternalLinks(True)
        self.taskLogs.setPlaceholderText("Task logs will appear here after a test starts.")
        layout.addWidget(self.taskLogs, 2)

        return panel

    def _build_charts_panel(self):
        panel = self._card("Live Metrics")
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)

        cpu_header = QtWidgets.QHBoxLayout()
        self.label_3 = self._section_label("CPU Usage in Actor")
        self.dropDown1 = QtWidgets.QComboBox(panel)
        self.dropDown1.setObjectName("dropDown1")
        self.dropDown1.setMinimumWidth(180)
        self.dropDown1.setToolTip("Choose the actor whose CPU usage should be plotted.")
        cpu_header.addWidget(self.label_3)
        cpu_header.addStretch(1)
        cpu_header.addWidget(self.dropDown1)
        layout.addLayout(cpu_header)

        self.graphWidget1 = PlotWidget(panel)
        self.graphWidget1.setObjectName("graphWidget1")
        layout.addWidget(self.graphWidget1, 1)

        kpi_header = QtWidgets.QHBoxLayout()
        self.label = self._section_label("KPI Metrics in gNodeB")
        self.dropDown2 = QtWidgets.QComboBox(panel)
        self.dropDown2.setObjectName("dropDown2")
        self.dropDown2.setMinimumWidth(180)
        self.dropDown2.setToolTip("Choose the KPI metric to plot.")
        kpi_header.addWidget(self.label)
        kpi_header.addStretch(1)
        kpi_header.addWidget(self.dropDown2)
        layout.addLayout(kpi_header)

        self.graphWidget2 = PlotWidget(panel)
        self.graphWidget2.setObjectName("graphWidget2")
        layout.addWidget(self.graphWidget2, 1)

        return panel

    def _setup_plots(self):
        pg.setConfigOptions(antialias=True)
        self._configure_plot(self.graphWidget1, "Samples", "CPU %")
        self._configure_plot(self.graphWidget2, "Samples", "KPI value")

        cpu_pen = pg.mkPen(color="#2563EB", width=2)
        kpi_pen = pg.mkPen(color="#0F766E", width=2)
        self.data1_line = self.graphWidget1.plot([], [], name="CPU", pen=cpu_pen, symbol="o", symbolSize=6, symbolBrush="#2563EB")
        self.data2_line = self.graphWidget2.plot([], [], name="KPI", pen=kpi_pen, symbol="o", symbolSize=6, symbolBrush="#0F766E")

    def _configure_plot(self, widget, bottom_label, left_label):
        widget.setBackground("#FFFFFF")
        widget.showGrid(x=True, y=True, alpha=0.25)
        widget.setLabel("bottom", bottom_label)
        widget.setLabel("left", left_label)
        widget.getAxis("bottom").setPen(pg.mkPen("#94A3B8"))
        widget.getAxis("left").setPen(pg.mkPen("#94A3B8"))
        widget.getAxis("bottom").setTextPen(pg.mkPen("#475569"))
        widget.getAxis("left").setTextPen(pg.mkPen("#475569"))
        widget.setMenuEnabled(False)

    def _connect_signals(self):
        self.addButton.clicked.connect(self.addToScript)
        self.startButton.clicked.connect(self.activeTestSave)
        self.tableWidget.itemClicked.connect(self.showLogs)
        self.actorList.itemSelectionChanged.connect(self._update_start_button_state)
        self.scriptList.itemSelectionChanged.connect(self._update_start_button_state)
        self.dropDown1.currentIndexChanged.connect(self._refresh_actor_plot)
        self.dropDown2.currentIndexChanged.connect(self.kpi_plot_updated)

    def _setup_styles(self, MainWindow):
        MainWindow.setStyleSheet(
            """
            QMainWindow, QWidget#centralwidget {
                background: #F4F7FB;
                color: #0F172A;
                font-family: Segoe UI, Calibri, Arial;
                font-size: 10.5pt;
            }
            QFrame#Header, QFrame#Card {
                background: #FFFFFF;
                border: 1px solid #DDE5EF;
                border-radius: 8px;
            }
            QLabel#TitleLabel {
                color: #0F172A;
                font-size: 20pt;
                font-weight: 700;
            }
            QLabel#SubtitleLabel, QLabel#MutedLabel {
                color: #64748B;
                font-size: 9.5pt;
            }
            QLabel#SectionLabel {
                color: #1E293B;
                font-size: 11pt;
                font-weight: 700;
            }
            QLabel#StatusPill {
                background: #E0F2FE;
                color: #075985;
                border: 1px solid #BAE6FD;
                border-radius: 12px;
                padding: 6px 12px;
                font-weight: 600;
            }
            QListWidget, QTableWidget, QTextBrowser, QComboBox {
                background: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 5px;
                selection-background-color: #DBEAFE;
                selection-color: #0F172A;
            }
            QListWidget::item {
                min-height: 26px;
                padding: 4px 6px;
            }
            QListWidget::item:selected {
                border-left: 3px solid #2563EB;
            }
            QTableWidget {
                gridline-color: #E2E8F0;
                alternate-background-color: #F8FAFC;
            }
            QHeaderView::section {
                background: #F1F5F9;
                color: #334155;
                border: none;
                border-bottom: 1px solid #CBD5E1;
                padding: 8px;
                font-weight: 700;
            }
            QTextBrowser {
                font-family: Consolas, Cascadia Mono, monospace;
                font-size: 9.5pt;
                line-height: 140%;
            }
            QPushButton {
                border: none;
                border-radius: 6px;
                padding: 9px 12px;
                font-weight: 700;
            }
            QPushButton#PrimaryButton {
                background: #2563EB;
                color: #FFFFFF;
            }
            QPushButton#PrimaryButton:hover {
                background: #1D4ED8;
            }
            QPushButton#PrimaryButton:disabled {
                background: #CBD5E1;
                color: #64748B;
            }
            QPushButton#SecondaryButton {
                background: #E2E8F0;
                color: #1E293B;
            }
            QPushButton#SecondaryButton:hover {
                background: #CBD5E1;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QStatusBar {
                background: #FFFFFF;
                color: #475569;
            }
            QSplitter::handle {
                background: #DDE5EF;
            }
            """
        )

    def _card(self, title):
        card = QtWidgets.QFrame(self.centralwidget)
        card.setObjectName("Card")
        card.setProperty("title", title)
        return card

    def _section_label(self, text):
        label = QtWidgets.QLabel(text)
        label.setObjectName("SectionLabel")
        return label

    def _muted_label(self, text):
        label = QtWidgets.QLabel(text)
        label.setObjectName("MutedLabel")
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return label

    def _label_row(self, left, right):
        row = QtWidgets.QHBoxLayout()
        row.addWidget(left)
        row.addStretch(1)
        row.addWidget(right)
        return row

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "OAIC-T Research Console"))
        self.addButton.setText(_translate("MainWindow", "Load Test Script"))
        self.startButton.setText(_translate("MainWindow", "Start Test"))
        self.statusbar.showMessage(_translate("MainWindow", "Ready"))

    # Functions called outside of GUI
    def addActor(self, actor):
        if not self.actorList.findItems(actor, Qt.MatchExactly):
            self.actorList.addItem(actor)
        if self.dropDown1.findText(actor) == -1:
            self.dropDown1.addItem(actor)
        self._update_empty_states()
        self._update_start_button_state()

    def removeActor(self, actor):
        remAcList = self.actorList.findItems(actor, Qt.MatchExactly)
        remAcDrop = self.dropDown1.findText(actor)
        for item in remAcList:
            self.actorList.takeItem(self.actorList.row(item))
        if remAcDrop >= 0:
            self.dropDown1.removeItem(remAcDrop)
        self.actor_rsc_all.pop(actor, None)
        self._refresh_actor_plot()
        self._update_empty_states()
        self._update_start_button_state()

    @QtCore.pyqtSlot(str, float, float)
    def on_actor_rsc_updated(self, actor_name, actor_rsc_cpu, actor_rsc_mem):
        values = self.actor_rsc_all.get(actor_name, [])
        values = values + [actor_rsc_cpu]
        self.actor_rsc_all[actor_name] = values
        self.data1_x = list(range(len(values)))
        self.data1_y = values

        if self.dropDown1.findText(actor_name) == -1:
            self.dropDown1.addItem(actor_name)

        if self.dropDown1.currentText() == actor_name:
            self._plot_actor_cpu(actor_name)

    def actor_rsc_updated(self, actor_name, actor_rsc_cpu, actor_rsc_mem):
        self.actor_updater.rsc_updated.emit(actor_name, actor_rsc_cpu, actor_rsc_mem)

    def plot_kpi(self):
        current_selected = self.dropDown2.currentText()
        if not current_selected or current_selected not in self.kpi_all:
            self.data2_line.setData([], [])
            return

        data_plot = self.kpi_all[current_selected]
        if not data_plot:
            self.data2_line.setData([], [])
            return

        self.data2_x = list(range(len(data_plot)))
        self.graphWidget2.setLabel("left", current_selected)
        self._set_plot_window(self.graphWidget2, self.data2_x, data_plot, 500)
        self.data2_line.setData(self.data2_x, data_plot)

    def kpi_plot_updated(self):
        self.plot_kpi()

    @QtCore.pyqtSlot(str, bool)
    def on_actor_kpi_updated(self, timestamp, flag):
        self.ts_all = self.ts_all.copy() + [timestamp]
        first_input_flag = len(self.kpi_all) == 0

        for key, value in self.kpi_all_update.items():
            if key in self.kpi_all:
                self.kpi_all[key] = self.kpi_all[key].copy() + [value]
            else:
                self.kpi_all[key] = [value]
                self.dropDown2.addItem(key)

        if first_input_flag and self.dropDown2.count() > 0:
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
            self.logHintLabel.setText("Live task log")

    def logs_updated(self, test_task):
        row_index, item_first, item_second = self.test_task_all[test_task]
        self.test_task_updater.log_changed.emit(test_task.log, row_index)

    def update_status(self, task_id, status):
        for test_task, (row_index, item_first, item_second) in self.test_task_all.items():
            if test_task.test_id == task_id:
                test_task.update_status(status)
                self.test_task_updater.status_changed.emit(status, row_index)
                break

    def addGraphData(self, xData, yData):
        index = self.dropDown1.currentIndex()
        if index >= 0:
            self.dropDown1.setItemData(index, xData, self.graphRoleX)
            self.dropDown1.setItemData(index, yData, self.graphRoleY)

    @QtCore.pyqtSlot(str, int)
    def on_status_updated(self, status, row_index):
        row = row_index - 1
        tableStatus = QTableWidgetItem(status)
        tableStatus.setTextAlignment(Qt.AlignCenter)
        color = self.STATUS_COLORS.get(status, QtGui.QColor("#0F172A"))
        tableStatus.setForeground(QtGui.QBrush(color))
        task_item = self.tableWidget.item(row, 0)
        task_data = task_item.data(Qt.UserRole) if task_item else None
        tableStatus.setData(Qt.UserRole, task_data)
        self.tableWidget.setItem(row, 1, tableStatus)
        self.statusbar.showMessage("Task status updated: " + status, 5000)

    def status_updated(self, test_task):
        row_index, item_first, item_second = self.test_task_all[test_task]
        self.test_task_updater.status_changed.emit(test_task.status, row_index)

    def getActors(self):
        item = self.tableWidget.currentItem()
        self.listOfActors = str(item.data(QtCore.Qt.UserRole)) if item else ""

    # used for testing
    def printout(self):
        print(self.listOfActors)

    # Functions within the GUI
    def addToScript(self):
        filename, _filter = QFileDialog.getOpenFileName(
            self,
            "Select a JSON test script",
            ".",
            "JSON (*.json)",
        )
        if not filename:
            return

        if filename not in self.load_test_files:
            display_name = os.path.basename(filename)
            item = QtWidgets.QListWidgetItem(display_name)
            item.setToolTip(filename)
            item.setData(Qt.UserRole, filename)
            self.scriptList.addItem(item)
            self.load_test_files.append(filename)
            self.statusbar.showMessage("Loaded test script: " + display_name, 5000)

        self._update_empty_states()
        self._update_start_button_state()

    def activeTestSave(self):
        selected_actors = [item.text() for item in self.actorList.selectedItems()]
        selected_tests = [item.data(Qt.UserRole) or item.text() for item in self.scriptList.selectedItems()]

        self.selected_lists.clear()
        self.selected_lists.append(selected_actors)
        self.selected_lists.append(selected_tests)

        if not selected_actors:
            QMessageBox.warning(self, "Actor required", "Select one actor before starting a test.")
            return
        if len(selected_actors) > 1:
            QMessageBox.warning(
                self,
                "Only one actor supported",
                "Select one actor. Multiple-actor testing will be supported in a later version.",
            )
            return

        if not selected_tests:
            QMessageBox.warning(self, "Test script required", "Select one JSON test script before starting a test.")
            return

        if len(selected_tests) > 1:
            QMessageBox.warning(
                self,
                "Only one script supported",
                "Select one test script. Multiple-script testing will be supported in a later version.",
            )
            return

        test_name, ok = QInputDialog.getText(self, "New Test Task", "Enter a name for your test task:")
        if not ok:
            return

        test_name = str(test_name).strip()
        if not test_name:
            QMessageBox.warning(self, "Task name required", "Enter a task name before starting the test.")
            return

        if self.actor_manager is None:
            QMessageBox.warning(self, "Server unavailable", "The actor manager is not connected to the GUI.")
            return

        row = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(row + 1)

        item_first = QTableWidgetItem(test_name)
        item_first.setData(QtCore.Qt.UserRole, self.selected_lists)
        self.tableWidget.setItem(row, 0, item_first)

        item_second = QTableWidgetItem("Pending")
        item_second.setTextAlignment(Qt.AlignCenter)
        item_second.setForeground(QtGui.QBrush(self.STATUS_COLORS["Pending"]))
        item_second.setData(QtCore.Qt.UserRole, self.selected_lists)
        self.tableWidget.setItem(row, 1, item_second)
        self.tableWidget.setCurrentItem(item_first)

        self.count = self.count + 1
        test_task = TestTask(selected_actors, selected_tests, str(self.count))
        self.add_test_task(test_task, self.tableWidget.rowCount(), item_first, item_second)
        self.actor_manager.start_test_task(test_task)

        self._update_empty_states()
        self.statusbar.showMessage("Started test task: " + test_name, 5000)

    def add_test_task(self, test_task, row_index, item_first, item_second):
        self.test_task_all[test_task] = (row_index, item_first, item_second)

    def showLogs(self):
        self.taskLogs.clear()
        if self.tableWidget.currentRow() < 0:
            self.logHintLabel.setText("Select a task to view logs")
            return

        selected_task = None
        for test_task, (row_index, item_first, item_second) in self.test_task_all.items():
            if self.tableWidget.currentRow() == row_index - 1:
                selected_task = test_task
                break

        if selected_task is None:
            self.logHintLabel.setText("No log available")
            return

        self.taskLogs.append(selected_task.log or "No log entries yet.")
        self.logHintLabel.setText("Task " + selected_task.test_id)

    def showGraph(self):
        index = self.dropDown1.currentIndex()
        if index < 0:
            return
        x_data = self.dropDown1.itemData(index, self.graphRoleX) or []
        y_data = self.dropDown1.itemData(index, self.graphRoleY) or []
        self.data1_line.setData(x_data, y_data)

    def _plot_actor_cpu(self, actor_name):
        values = self.actor_rsc_all.get(actor_name, [])
        if not values:
            self.data1_line.setData([], [])
            return

        x_values = list(range(len(values)))
        self.graphWidget1.setLabel("left", actor_name + " CPU %")
        self._set_plot_window(self.graphWidget1, x_values, values, 100)
        self.data1_line.setData(x_values, values)

    def _refresh_actor_plot(self):
        actor_name = self.dropDown1.currentText()
        if actor_name:
            self._plot_actor_cpu(actor_name)
        else:
            self.data1_line.setData([], [])

    def _set_plot_window(self, plot_widget, x_values, y_values, max_y):
        if not x_values or not y_values:
            return

        last_x = x_values[-1]
        plot_widget.setXRange(max(last_x - 10, 0), last_x + 5, padding=0)

        min_y = min(y_values)
        max_value = max(y_values)
        lower = max(min_y - 0.2 * abs(min_y), 0)
        upper = max_value + 0.2 * abs(max_value)
        if max_value <= max_y:
            upper = min(upper, max_y)
        if upper <= lower:
            upper = lower + 1
        plot_widget.setYRange(lower, upper, padding=0)

    def _update_server_status(self, text):
        if hasattr(self, "serverStatus"):
            self.serverStatus.setText(text)

    def _update_start_button_state(self):
        if not hasattr(self, "startButton"):
            return
        actor_count = len(self.actorList.selectedItems()) if hasattr(self, "actorList") else 0
        script_count = len(self.scriptList.selectedItems()) if hasattr(self, "scriptList") else 0
        self.startButton.setEnabled(actor_count == 1 and script_count == 1)

    def _update_empty_states(self):
        if hasattr(self, "actorCountLabel"):
            count = self.actorList.count()
            text = str(count) + (" actor" if count == 1 else " actors") if count else "No actors registered"
            self.actorCountLabel.setText(text)
        if hasattr(self, "scriptCountLabel"):
            count = self.scriptList.count()
            text = str(count) + (" script" if count == 1 else " scripts") if count else "No scripts loaded"
            self.scriptCountLabel.setText(text)
        if hasattr(self, "taskCountLabel"):
            count = self.tableWidget.rowCount()
            text = str(count) + (" task" if count == 1 else " tasks") if count else "No active tasks"
            self.taskCountLabel.setText(text)


class TestTaskUpdater(QObject):
    status_changed = pyqtSignal(str, int)
    log_changed = pyqtSignal(str, int)


class ActorUpdater(QObject):
    rsc_updated = pyqtSignal(str, float, float)
    kpi_updated = pyqtSignal(str, bool)  # ts, kpi_name1, kpi_val1, ...


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
