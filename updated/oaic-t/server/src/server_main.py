# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

from actor_manager import ActorManager
import time
import test_script_reader as test_script_reader
from backports import configparser
import sys
import os.path
import argparse
import threading
from researchGUI import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QFileDialog, QInputDialog, QAbstractItemView, QTableWidget, QTableWidgetItem
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
from random import randint
from test_task import TestTask

if __name__ == '__main__':
    # The server starts with the actor manager that handles actor connections.

    # TO DO: The port will be configured from the configuration file.
    host = "127.0.0.1"
    # port = 12345

    config_parser = configparser.RawConfigParser()
    config_file_path = r'config.txt'
    config_parser.read(config_file_path)
    port = int(config_parser.get('server_config', 'server_port'))

    gui_flag = config_parser.get('server_config', 'GUI')

    print("Server is running...")
    actor_manager = ActorManager(host, port)
    actor_manager.run()

    if gui_flag.lower() == 'true':
        app = QtWidgets.QApplication(sys.argv)
        MainWindow = QtWidgets.QMainWindow()
        ui = Ui_MainWindow()
        ui.setupUi(MainWindow)
        MainWindow.show()
        ui.set_actor_manager(actor_manager)

        actor_manager.set_ui(ui)


        # Use this to get the list of actors and test script files used in
        # each test task.
        ui.tableWidget.itemClicked.connect(lambda: ui.getActors())
        ui.tableWidget.itemClicked.connect(lambda: ui.printout())
        # ui.stopButton.clicked.connect(lambda: ui.updateStatus("Running"))
        # ui.stopButton.clicked.connect(lambda: ui.addLogs(logs))



        ui.graphX = list(range(100))
        ui.graphY = [randint(0, 100) for _ in range(100)]
        ui.addGraphData(ui.graphX, ui.graphY)

        sys.exit(app.exec_())
    else:
        # while True:
        #     time.sleep(2)
        #     if len(actor_manager.actor_list) > 0:
        #         break

        id_count = 1
        while True:

            str_cmd = input("Type commands anytime:")
            #print("str you just typed: " + str_cmd)
            cmds = str_cmd.split()

            if not cmds:
                continue
            elif cmds[0].lower() == "run":
                args = cmds[1:len(cmds)]
                parser = argparse.ArgumentParser(
                    description='Run test scripts in one or more Actors. For example, run --actor ue1 ue2 --test ../test/test_traffic.json')
                parser.add_argument('--actor', type=str, nargs='*',
                                    help='An argument to indicate the actor')
                parser.add_argument('--test', type=str, nargs='*',
                                    help='An argument to indicate test scripts')
                try:
                    args = parser.parse_args(args)

                    if args.test is None or len(args.test) == 0:
                        print("A test script must be specified! Use --test option!")
                        continue
                    if args.actor is None or len(args.actor) == 0:
                        print("An actor must be specified! Use --actor option!")
                        continue

                    selected_actors = args.actor
                    selected_tests = args.test
                    test_task = TestTask(selected_actors, selected_tests, str(id_count))
                    actor_manager.start_test_task(test_task)
                    id_count = id_count + 1
                except SystemExit:
                    print("Unknown arguments. Usage: run --actor actor(s) --test testscript(s) ")
            elif cmds[0].lower() == "list":
                if len(cmds) <= 1:
                    print(
                        "Unknown list commands. Usage: list actors [This lists all active actors.] or list tests [This lists all running tests.]")
                    continue
                if cmds[1].lower() == "actors":
                    all_actor_name = ""
                    for actor in actor_manager.actor_list:
                        all_actor_name = all_actor_name + actor.name + "; "
                    print("[" + str(len(actor_manager.actor_list)) + "] active actors available: " + all_actor_name)
                elif cmds[1].lower() == "tests":
                    all_test_name = ""
                    for test in actor_manager.test_task_all:
                        all_test_name = all_test_name + test.test_id + "; "
                    print("[" + str(len(actor_manager.test_task_all)) + "] tests: " + all_test_name)

                    # print("To Be Supported Soon!")
                else:
                    print(
                        "Unknown list commands. Usage: list actors [This lists all active actors.] or list tests [This lists all running tests.]")
            elif cmds[0].lower() == "quit" or cmds[0].lower() == "exit":
                actor_manager.stop()
                print("OAIC-T Server Exits! Bye!")
                break
            else:
                print("Unknown command!")
                continue
