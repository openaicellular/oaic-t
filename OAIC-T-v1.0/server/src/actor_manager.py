# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

import socket
from _thread import *
import threading
from actor import Actor
from server_logger import logger
from message_handler import message_handler
import time
import json
import test_script_reader as test_script_reader
import os.path
from test_task import TestTask


class ActorManager:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.actor_list = []
        self.ui = None
        self.test_task_all = []

    # A new thread to handle requests from the actor
    def waiting_actor_thread(self, actor):
        while True:
            # data received from client
            data = actor.socket.recv(1024)
            data = data.decode("utf-8")
            logger.info(
                "<<-- Received message: {}".format(data) + " from " + actor.name + " " + str(actor.addr[0]) + ':' + str(
                    actor.addr[1]))

            if not data:
                logger.info("Actor disconnected" + " from " + str(actor.addr[0]) + ':' + str(actor.addr[1]))
                break

            message = json.loads(data, strict=False)
            message_handler.handle(actor, message, self)

        # connection closed
        self.remove_actor(actor)
        print("Actor [" + actor.name + "] is disconnected and unregistered!")
        actor.socket.close()

    def get_actor(self, actor_name):
        for actor in self.actor_list:
            if actor.name == actor_name:
                return actor
        return None

    def register_actor_without_name(self, actor):
        self.actor_list.append(actor)

    def register_actor_with_name(self, actor):
        if self.ui:
            self.ui.addActor(actor.name)

    def get_actors_size(self):
        return len(self.actor_list)

    def remove_actor(self, actor):
        self.actor_list.remove(actor)
        if self.ui:
            self.ui.removeActor(actor.name)

    def waiting_actor_registration(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        self.s.listen(5)
        print("Server socket is listening to the port " + str(self.port) + "...")

        # a forever loop until client wants to exit
        while True:
            # establish connection with client
            c, addr = self.s.accept()

            actor = Actor(addr, c)

            self.register_actor_without_name(actor)

            logger.info('Connected to : ' + str(addr[0]) + ':' + str(addr[1]))

            # Start a new thread to listen and handle messages sent from this actor
            start_new_thread(self.waiting_actor_thread, (actor,))

        self.s.close()

    def run(self):
        # Start a new thread to handle actor connections
        start_new_thread(self.waiting_actor_registration, ())

        self.update_rsc()

    def update_rsc(self):
        threading.Timer(5.0, self.update_rsc).start()
        for actor in self.actor_list:
            if actor.name != "Not Recognized":
                message = {"type": "resource update request"}
                actor.send_msg_dict(message)

    def stop(self):
        self.s.close()

    def set_ui(self, ui):
        self.ui = ui

    def find_test_task(self, test_id):
        for test_task in self.test_task_all:
            if test_task.test_id == test_id:
                return test_task
        print("Error: cannot find the test task with id: " + test_id)
        return None

    def update_actor_rsc(self, actor_name, actor_rsc):
        if self.ui:
            self.ui.actor_rsc_updated(actor_name, float(actor_rsc.cpu), float(actor_rsc.mem))

    def update_kpi_xapp(self, ts, kpi_all):
        if self.ui:
            self.ui.actor_kpi_updated(ts, kpi_all)

    def update_test_status(self, test_id, status):
        test_task = self.find_test_task(test_id)
        test_task.update_status(status)
        if self.ui and test_task is not None:
            self.ui.status_updated(test_task)
        else:
            print("The status of the test task has been updated to be " + status + "!")

    def update_test_logs(self, test_id, logs):
        test_task = self.find_test_task(test_id)
        if self.ui and test_task:
            test_task.append_log(logs)
            self.ui.logs_updated(test_task)
        else:
            print(logs)

    def start_test_task(self, test_task):
        # check if all test scripts exist

        selected_actors = test_task.actor_name
        selected_tests = test_task.test_scripts
        test_id = test_task.test_id

        test_exist = True
        test_not_exist = ""
        for test in selected_tests:
            if not os.path.exists(test):
                test_not_exist = test_not_exist + test + "; "

        if test_not_exist:
            print("Test scripts cannot be found: " + test_not_exist)
            return

        for actor_name in selected_actors:
            actor = self.get_actor(actor_name)
            if actor is None:
                print(
                    "Actor is not registered: " + actor_name + "! Type cmd 'list actors' to list all active actors!")
                break

            for test in selected_tests:
                message = test_script_reader.read_test_script_json(test)
                message["id"] = str(test_id)
                message["type"] = "new task request"
                actor.send_msg_dict(message)
                print("Send test script: " + test + " to the actor: " + actor_name)

        self.test_task_all.append(test_task)
        logs = "The test task is created. \n" \
               "...... Target Actor: " + selected_actors[0] + "\n" + "...... Test Scripts: " + "; ".join(selected_tests) + "\n" + "===================================================\n"
        self.update_test_logs(test_id, logs)
