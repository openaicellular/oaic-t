# Import socket module
import getopt
from actor_logger import logger
from server_connection import ServerConnection
import task_executor
import sys
from backports import configparser


def main(argv):

    # server_ip = '127.0.0.1'
    # server_port = 12345
    # actor_name = 'Actor 1'

    # try:
    #     optlist, args = getopt.getopt(argv[1:], 'i:p:n:', ["help", "output="])
    #     print(optlist, args)
    # except getopt.GetoptError:
    #     logger.error('actor_main -h server_ip -p server_port -n actor_name')
    #     sys.exit(2)
    #
    # for o, a in optlist:
    #     if o == "-i":
    #         server_ip = a
    #     elif o == '-p':
    #         server_port = a
    #     elif o == "-n":
    #         actor_name = a
    #     else:
    #         print("unhandled option")
    #         sys.exit(2)
    config_parser = configparser.RawConfigParser()
    config_file_path = r'config.txt'
    config_parser.read(config_file_path)
    server_ip = config_parser.get('actor_config', 'server_ip')
    server_port = config_parser.get('actor_config', 'server_port')
    actor_name = config_parser.get('actor_config', 'actor_name')
    print(server_ip, server_port, actor_name)
    server_connection = ServerConnection(server_ip, int(server_port), actor_name)
    task_executor.run(server_connection)


if __name__ == '__main__':
    main(sys.argv)
