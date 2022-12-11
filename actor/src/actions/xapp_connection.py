# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

import socket
from _thread import *
import threading
from actor_logger import logger
import json
import utils as utils
from socket import error as socket_error



class XAPPConnection:

    def __init__(self, server_host, server_port, xapp_name, server_connection):
        self.server_host = server_port
        self.server_port = server_port
        self.xapp_name = xapp_name
        self.server_connection = server_connection
        self.socket = None
        self.start(server_host, server_port, xapp_name)
        # self.status = False
        # self.reasons = "The socket client does not start yet!"

    def send_msg(self, msg_dict):
        logger.info("-->> Send a message to the server: {}".format(msg_dict))
        data = json.dumps(msg_dict)
        self.socket.sendall(bytes(data, encoding="utf-8"))

    def waiting_server_thread(self, socket):
        # msg_handler = MessageHandler(self)
        while True:
            # this thread is created to wait new message received from server
            data = socket.recv(1024)
            data = data.decode("utf-8")

            if not data:
                break

            logger.info('<<-- Receive a message from the server : {}'.format(data))

            #message = json.loads(data)
            # message_handler.handle(message)
            self.server_connection.send_msg(data)  ## forward this message to the oaic-t server

        # close the connection
        print('Server disconnected!')
        socket.close()

    # def check_status(self):
    #     return (self.status, self.reasons)

    def start(self, host, port, name):
        print("Trying to connect to the Test xApp, ip: " + host + " port: " + str(port) + "...")
        print(self.server_connection)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.status = False
        self.reasons = "Socket is created. Now it is trying to connect the Test xApp!"
        # connect to server on local computer
        try:
            self.socket.connect((host, port))
        except socket_error as err:
            self.status = False
            self.reasons = "Fail to connect Test xApp."
            return

        # message = {"type": "registration", "name": name}  # a real dict.
        # data = json.dumps(message)
        #
        # self.socket.sendall(bytes(data, encoding="utf-8"))
        #
        # # message received from server
        # data = self.socket.recv(1024)
        # data = data.decode("utf-8")
        # print the received message
        # logger.info('-->> Receive a message from the server : {}'.format(data))
        print("Server connection is completed!")
        self.status = True
        self.reasons = "Test xApp connection success!"
        start_new_thread(self.waiting_server_thread, (self.socket,))

