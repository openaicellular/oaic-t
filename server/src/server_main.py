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



if __name__ == '__main__':
    # The server starts with the actor manager that handles actor connections.

    # TO DO: The port will be configured from the configuration file.
    host = "127.0.0.1"
    #port = 12345

    config_parser = configparser.RawConfigParser()
    config_file_path = r'config.txt'
    config_parser.read(config_file_path)
    port = int(config_parser.get('server_config', 'server_port'))

    print("Server is running...")
    actor_manager = ActorManager(host, port)
    actor_manager.run()

    test_file = sys.argv[1]

    # TO DO: this will be replaced by a module that can interact with users, where users can type commands
    # This is just an example of implementation which periodically sends requests to update each actor's resource,
    # and some fake test actions for testing purposes only.

    # wait until one actor is registered. To Be Replaced!
    while True:
        time.sleep(2)
        if len(actor_manager.actor_list) > 0:
            break


    #time.sleep(10)
    id_count = 0

    # To Be Replaced
    print("Running the test script: " + test_file)

    #while True:
    for actor in actor_manager.actor_list:
        print("Send a Resource Update Request to the Actor [" + actor.name + "] ...")
        message = {"type": "resource update request"}
        actor.send_msg_dict(message)
        time.sleep(5)

        print("Send a New Task Request to the Actor [" + actor.name + "] ...")
        message = test_script_reader.read_test_script_json(test_file)
        id_count = id_count + 1
        message["id"] = "task id" + str(id_count)
        message["type"] = "new task request"
        actor.send_msg_dict(message)
        time.sleep(1000)


