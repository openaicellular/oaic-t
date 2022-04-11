# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

import json
from server_logger import logger


class Actor:
    def __init__(self, addr, socket):
        self.addr = addr
        self.socket = socket
        self.name = "Not Recognized"

    # This function checks if the socket is alive
    def is_alive(self):
        ### TO DO
        return True

    def set_name(self, name):
        self.name = name

    # Overload class object comparison operator
    def __eq__(self, other):
        if self.addr == other.addr:
            return True
        else:
            return False

    def send_msg_dict(self, msg):
        logger.info('-->> Send message to the actor: {}'.format(msg) + " : " + self.name + " " + str(self.addr[0]) + ':' + str(
            self.addr[1]))
        data = json.dumps(msg)
        self.socket.sendall(bytes(data, encoding="utf-8"))

    def update_resource(self, actor_resource):
        this.actor_resource = actor_resource
