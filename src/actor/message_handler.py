# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

from task import Task
import utils
import json
import task_executor
from actor_logger import logger

# Handle all requests from the server.
class MessageHandler:
    def __init__(self, server_connection):
        self.server_connection = server_connection
        pass

    def rsc_update_message(self, message):
        message_sent = {"type": "resource update", "cpu": str(utils.get_cpu_info()),
                        "mem": str(utils.get_mem_info()), "sdr_size": str(2)}
        self.server_connection.send_msg(message_sent)

    def new_task_message(self, message):
        new_task = Task(message)
        task_executor.register_new_task(new_task)
        message_sent = {"type": "new task received and pending to run"}
        self.server_connection.send_msg(message_sent)

    def task_status_message(self, message):
        pass

    def task_termination_message(self, message):
        pass

    def sdr_reset_message(self, message):
        pass

    def actor_reset_message(self, message):
        pass

    def handle(self, message):
        if message['type'] == "resource update request":
            self.rsc_update_message(message)
        elif message['type'] == "new task request":
            self.new_task_message(message)
        elif message['type'] == "task status request":
            self.task_status_message(message)
        elif message['type'] == "task termination request":
            self.task_termination_message(message)
        elif message['type'] == "sdr reset request":
            self.sdr_reset_message(message)
        elif message['type'] == "actor reset request":
            self.actor_reset_message(message)