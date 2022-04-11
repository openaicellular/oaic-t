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


class ActorManager:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.actor_list = []

    # A new thread to handle requests from the actor
    def waiting_actor_thread(self, actor):
        while True:
            # data received from client
            data = actor.socket.recv(1024)
            data = data.decode("utf-8")
            logger.info("<<-- Received message: {}".format(data) + " from " + actor.name + " " + str(actor.addr[0]) + ':' + str(actor.addr[1]))

            if not data:
                logger.info("Actor disconnected" + " from " + str(actor.addr[0]) + ':' + str(actor.addr[1]))
                break

            message = json.loads(data)
            message_handler.handle(actor, message)

        # connection closed
        actor.socket.close()

    def register_actor(self, actor):
        self.actor_list.append(actor)

    def get_actors_size(self):
        return len(self.actor_list)

    def remove_actor(self, actor):
        self.actor_list.remove(actor)

    def waiting_actor_registration(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        logger.info("Server socket binded to port " + str(self.port))

        # put the socket into listening mode
        self.s.listen(5)
        logger.info("Server socket is listening... ")

        # a forever loop until client wants to exit
        while True:
            # establish connection with client
            c, addr = self.s.accept()

            actor = Actor(addr, c)

            self.register_actor(actor)

            logger.info('Connected to : ' + str(addr[0]) + ':' + str(addr[1]))

            # Start a new thread to listen and handle messages sent from this actor
            start_new_thread(self.waiting_actor_thread, (actor,))

        self.s.close()

    def run(self):
        # Start a new thread to handle actor connections
        start_new_thread(self.waiting_actor_registration, ())

