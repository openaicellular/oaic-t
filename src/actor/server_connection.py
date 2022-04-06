import socket
from _thread import *
import threading
from actor_logger import logger
import json
import utils as utils
from message_handler import MessageHandler


class ServerConnection:

    def __init__(self, server_host, server_port, actor_name):
        self.server_host = server_port
        self.server_port = server_port
        self.actor_name = actor_name
        self.socket = None
        self.start(server_host, server_port, actor_name)

    def send_msg(self, msg_dict):
        logger.info("-->> Send a message to the server: {}".format(msg_dict))
        data = json.dumps(msg_dict)
        self.socket.sendall(bytes(data, encoding="utf-8"))

    def waiting_server_thread(self, socket):
        msg_handler = MessageHandler(self)
        while True:
            # this thread is created to wait new message received from server
            data = socket.recv(1024)
            data = data.decode("utf-8")

            if not data:
                break

            logger.info('<<-- Receive a message from the server : {}'.format(data))

            message = json.loads(data)
            msg_handler.handle(message)

            # ask the client whether he wants to continue
            # ans = input('\nDo you want to continue(y/n) :')
            # if ans == 'y':
            #    continue
            # else:
            #    break
        # close the connection
        logger.info('Server disconnected')
        socket.close()

    def start(self, host, port, name):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connect to server on local computer
        self.socket.connect((host, port))

        # Send the first message after it connects to the server with the name
        # message you send to server

        message = {"type": "registration", "name": name}  # a real dict.
        data = json.dumps(message)

        self.socket.sendall(bytes(data, encoding="utf-8"))

        # message received from server
        data = self.socket.recv(1024)
        data = data.decode("utf-8")
        # print the received message
        logger.info('-->> Receive a message from the server : {}'.format(data))

        start_new_thread(self.waiting_server_thread, (self.socket,))
