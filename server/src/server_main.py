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
import os.path
import argparse
import threading

# # flush stdin when something are displayed
# def keep_wait_input(input_queue):
#     while True:
#         display = False
#         while not display:
#             if sys.stdout.read():
#                 display = True
#                 sys.stdout.buffer.flush()
#                 time.sleep(1)
#
#         print("Type commands anytime (new):", end="\n")
#         sys.stdout.buffer.flush()
#         time.sleep(0.05)


if __name__ == '__main__':
    # The server starts with the actor manager that handles actor connections.

    # TO DO: The port will be configured from the configuration file.
    host = "127.0.0.1"
    # port = 12345

    config_parser = configparser.RawConfigParser()
    config_file_path = r'config.txt'
    config_parser.read(config_file_path)
    port = int(config_parser.get('server_config', 'server_port'))

    print("Server is running...")
    actor_manager = ActorManager(host, port)
    actor_manager.run()

    # TO DO: this will be replaced by a module that can interact with users, where users can type commands
    # This is just an example of implementation which periodically sends requests to update each actor's resource,
    # and some fake test actions for testing purposes only.

    # wait until one actor is registered. To Be Replaced!
    while True:
        time.sleep(2)
        if len(actor_manager.actor_list) > 0:
            break

    # # keep allowing users type commands
    # input_thread = threading.Thread(target=keep_wait_input, args=(None,))
    # input_thread.daemon = True
    # input_thread.start()


    id_count = 1
    while True:

        str_cmd = input("Type commands anytime:")
        #print("str you just typed: " + str_cmd)
        cmds = str_cmd.split()

        if not cmds:
            continue
        elif cmds[0].lower() == "run":
            args = cmds[1:len(cmds)]
            parser = argparse.ArgumentParser(
                description='Run test scripts in one or more Actors. For example, run --actor ue1 ue2 --test ../test/test_traffic.json')
            parser.add_argument('--actor', type=str, nargs='*',
                                help='An argument to indicate the actor')
            parser.add_argument('--test', type=str, nargs='*',
                                help='An argument to indicate test scripts')
            try:
                args = parser.parse_args(args)

                if args.test is None or len(args.test) == 0:
                    print("A test script must be specified! Use --test option!")
                    continue
                if args.actor is None or len(args.actor) == 0:
                    print("An actor must be specified! Use --actor option!")
                    continue

                # check if all test scripts exist
                test_exist = True

                test_not_exist = ""
                for test in args.test:
                    if not os.path.exists(test):
                        test_not_exist = test_not_exist + test + "; "

                if test_not_exist:
                    print("Test scripts cannot be found: " + test_not_exist)
                    continue

                for actor_name in args.actor:
                    actor = actor_manager.get_actor(actor_name)
                    if actor is None:
                        print(
                            "Actor is not registered: " + actor_name + "! Type cmd 'list actors' to list all active actors!")
                        break

                    for test in args.test:
                        message = test_script_reader.read_test_script_json(test)
                        id_count = id_count + 1
                        message["id"] = "task id" + str(id_count)
                        message["type"] = "new task request"
                        actor.send_msg_dict(message)
                        print("Send test script: " + test + " to the actor: " + actor_name)

            except SystemExit:
                print("Unknown arguments. Usage: run --actor actor(s) --test testscript(s) ")
        # elif cmds[0].lower() == "config":
        #     args = cmds[1:len(cmds)]
        #     parser = argparse.ArgumentParser(
        #         description='Config the actor, e.g., start the EPC or ENodeB')
        #     parser.add_argument('--actor', type=str, nargs='?',
        #                         help='An argument to indicate the actor')
        #     parser.add_argument('--start', type=str, nargs='?',
        #                         help='An argument to indicate which app to be started in the actor')
        #     parser.add_argument('--paras', type=str, nargs='?',
        #                         help='Paras to be used for the app to be started in the actor')
        #
        #     try:
        #         args = parser.parse_args(args)
        #
        #         if args.start is None:
        #             print("A app to be started must be specified! Use --start option!")
        #             continue
        #         if len(args.start) > 1:
        #             print("Only one app must be specified!")
        #             continue
        #         if args.actor is None:
        #             print("An actor must be specified! Use --actor option!")
        #             continue
        #         if len(args.actor) > 1:
        #             print("Only one actor must be specified!")
        #             continue
        #         if len(args.paras) is None:
        #             args.paras = ""
        #         if len(args.paras) > 1:
        #             print("Paras should be quoted!")
        #             continue
        #
        #         actor = actor_manager.get_actor(args.actor[0])
        #         if actor is None:
        #             print("Actor is not registered: " + actor_name + "! Type cmd 'list actors' to list all active actors!")
        #             continue
        #
        #         # build a message to configure the actor
        #         message["type"] = "configure"
        #         message["app"] = args.start[0]
        #         message["paras"] = args.paras[0]
        #         actor.send_msg_dict(message)
        #         print("Send configuration info to the actor: " + actor_name)
        #     except SystemExit:
        #         print("Unknown arguments. Usage: config --actor actor --start app --paras 'paras' ")

        elif cmds[0].lower() == "list":
            if cmds[1].lower() == "actors":
                all_actor_name = ""
                for actor in actor_manager.actor_list:
                    all_actor_name = all_actor_name + actor.name + "; "
                print("[" + str(len(actor_manager.actor_list)) + "] active actors available: " + all_actor_name)
            elif cmds[1].lower() == "tests":
                print("To Be Supported Soon!")
            else:
                print(
                    "Unknown list commands. Usage: list actors [This lists all active actors.] or list tests [This lists all running tests.]")
        elif cmds[0].lower() == "quit" or cmds[0].lower() == "exit":
            actor_manager.stop()
            print("OAIC-T Server Exits! Bye!")
            break
        else:
            print("Unknown command!")
            continue

    # test_file = sys.argv[1]
    #
    #
    #
    #
    # #time.sleep(10)
    # id_count = 0
    #
    # # To Be Replaced
    # print("Running the test script: " + test_file)
    #
    # #while True:
    # for actor in actor_manager.actor_list:
    #     print("Send a Resource Update Request to the Actor [" + actor.name + "] ...")
    #     message = {"type": "resource update request"}
    #     actor.send_msg_dict(message)
    #     time.sleep(5)
    #
    #     print("Send a New Task Request to the Actor [" + actor.name + "] ...")
    #     message = test_script_reader.read_test_script_json(test_file)
    #     id_count = id_count + 1
    #     message["id"] = "task id" + str(id_count)
    #     message["type"] = "new task request"
    #     actor.send_msg_dict(message)
    #     time.sleep(1000)
