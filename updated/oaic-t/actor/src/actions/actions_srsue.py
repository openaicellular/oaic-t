# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

import socket
from actor_logger import logger
from task import Action
from actions.action_executor import ActionExecutor
import time
from _thread import *


class SRSUE:
    def __init__(self, addr, socket):
        self.addr = addr
        self.socket = socket
        self.name = "Not Recognized"

    def set_name(self, name):
        self.name = name

    # Overload class object comparison operator
    def __eq__(self, other):
        if self.addr == other.addr:
            return True
        else:
            return False

    def send_msg_dict(self, msg):
        logger.info(
            '-->> Send message to the srsUE: {}'.format(msg) + " : " + self.name + " " + str(self.addr[0]) + ':' + str(
                self.addr[1]))
        data = json.dumps(msg)
        try:
            self.socket.sendall(bytes(data, encoding="utf-8"))
        except Exception as e:
            logger.info('-->> Send message error: socket is disconnected!')


def handle(srsUE, message):
    if message['type'] == "registration":
        srsUE.set_name(message['name'])
        message_sent = {"type": "registration confirmed"}
        print("A srsUE [" + srsUE.name + "] is registered!")
    elif message['type'] == "test status":
        status = message['status']
        task_results = message['results']
        print("srsUE [" + actor.name + "] updated its test status!" + " Status: " + status)
        message_sent = {"type": "confirmed"}
    else:
        # TO DO: implement other message from the actor
        message_sent = {"type": "confirmed"}

    srsUE.send_msg_dict(message_sent)


class SRSUEManager:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.srsUE_list = []

    def waiting_srsue_thread(self, srsUE):
        while True:
            # data received from client
            data = srsUE.socket.recv(1024)
            data = data.decode("utf-8")
            logger.info(
                "<<-- Received message: {}".format(data) + " from " + srsUE.name + " " + str(srsUE.addr[0]) + ':' + str(
                    srsUE.addr[1]))

            if not data:
                logger.info("srsUE disconnected" + " from " + str(srsUE.addr[0]) + ':' + str(srsUE.addr[1]))
                break

            message = json.loads(data, strict=False)
            handle(srsUE, message)

        # connection closed
        self.remove_srsUE(srsUE)
        print("srsUE [" + srsUE.name + "] is disconnected and unregistered!")
        srsUE.socket.close()

    def get_srsUE(self, srsUE_name):
        for srsUE in self.srsUE_list:
            if srsUE.name == srsUE_name:
                return srsUE
        return None

    def register_srsUE(self, srsUE):
        self.srsUE_list.append(srsUE)

    def remove_srsUE(self, srsUE):
        self.srsUE_list.remove(srsUE)

    def waiting_srsUE_registration(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        self.s.listen(5)
        print("Server socket is listening to the port " + str(self.port) + "...")

        # a forever loop until client wants to exit
        while True:
            # establish connection with client
            c, addr = self.s.accept()

            srsUE = SRSUE(addr, c)

            self.register_srsUE(srsUE)

            logger.info('Connected to : ' + str(addr[0]) + ':' + str(addr[1]))

            # Start a new thread to listen and handle messages sent from this srsUE
            start_new_thread(self.waiting_srsUE_thread, (srsUE,))

        self.s.close()

    def run(self):
        # Start a new thread to handle srsUE connections
        start_new_thread(self.waiting_srsUE_registration, ())

    def stop(self):
        self.s.close()


# This action is to create a new network namespace for one UE
# It first creates a namespace and verify the new namespace exists
class ActionStartSRSUE(ActionExecutor):
    ACTION_NAME = "Start SRSUE"  ## Be sure this action name is the one used in the test script

    def run(self):
        print("Action running: " + self.action.name + " ...")
        namespace = self.action.paras['namespace']

        srsUEManager = SRSUEManager("127.0.0.1", 54321)
        srsUEManager.run()

        action_output_summary = ""
        action_output = " "
        return action_output_summary, action_output

        

        #return action_output_summary, action_output
