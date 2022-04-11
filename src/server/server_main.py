# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

from actor_manager import ActorManager
import time
import test_script_reader as test_script_reader


if __name__ == '__main__':
    # The server starts with the actor manager that handles actor connections.

    # TO DO: The port will be configured from the configuration file.
    host = "127.0.0.1"
    port = 12345

    actor_manager = ActorManager(host, port)
    actor_manager.run()

    # TO DO: this will be replaced by a module that can interact with users, where users can type commands
    # This is just an example of implementation which periodically sends requests to update each actor's resource,
    # and some fake test actions for testing purposes only.
    time.sleep(5)
    id_count = 0
    while True:
        for actor in actor_manager.actor_list:
            message = {"type": "resource update request"}
            actor.send_msg_dict(message)
            time.sleep(5)

            message = test_script_reader.read_test_script_xml("test.xml")
            id_count = id_count + 1
            message["id"] = str(id_count)
            message["type"] = "new task request"
            actor.send_msg_dict(message)
            time.sleep(5)


