# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

import getopt
from actor_logger import logger
from server_connection import ServerConnection
import task_executor
import sys
from backports import configparser
import atexit
from actions.proc_gen import stop_all_running_process

server_connection = None

def main(argv):
    # server_ip = '127.0.0.1'
    # server_port = 12345
    # actor_name = 'Actor 1'
    atexit.register(exit_handler)

    config_parser = configparser.RawConfigParser()
    config_file_path = r'config.txt'
    config_parser.read(config_file_path)
    server_ip = config_parser.get('actor_config', 'server_ip')
    server_port = config_parser.get('actor_config', 'server_port')
    actor_name = config_parser.get('actor_config', 'actor_name')

    print("Actor [" + actor_name + "] is running...")

    # Register itself to the server and starts a thread to listen all requests from the server
    server_connection = ServerConnection(server_ip, int(server_port), actor_name)

    # A thread or a forever main loop to execute tasks
    task_executor.run(server_connection)


def exit_handler():
    logger.info("Clean environment before the actor ends...")
    stop_all_running_process()
    print("Actor stopped and exited!")



if __name__ == '__main__':
    main(sys.argv)

