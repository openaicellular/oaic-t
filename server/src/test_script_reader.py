# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

import json
import random

# This module implements the loading of one or more test scripts
def read_test_script_xml(filename):
    # TO DO: read xml and convert it into a dict, one example given as follows:
    action1 = {"name": "Create Network Namespace", "paras": {"namespace": "ue1"}, "type": "running"}
    action2 = {"name": "Run UE", "paras": {"namespace": "ue1"}, "type": "running"}
    action3 = {"name": "Generate Traffic", "paras": {"namespace": "ue1", "direction": "uplink", "ping_time": 20}, "type": "running"}
    action4 = {"name": "Stop UE", "paras": {"namespace": "ue1"}, "type": "running"}
    actions = [action1, action2, action3, action4]
    message = {"test_name": "task_test", "id": "123456", "mode": "virtual radio", "actions": actions}

    print(message)

    return message


def read_test_script_json(filename):
    # TO DO: read xml and convert it into a dict, one example given as follows:
    # action1 = {"name": "Create Network Namespace", "paras": {"namespace": "ue1"}, "type": "running"}
    # action2 = {"name": "Run UE", "paras": {"namespace": "ue1"}, "type": "running"}
    # action3 = {"name": "Generate Traffic", "paras": {"namespace": "ue1", "direction": "uplink", "ping_time": 20}, "type": "running"}
    # action4 = {"name": "Stop UE", "paras": {"namespace": "ue1"}, "type": "running"}
    # actions = [action1, action2, action3, action4]
    # message = {"name": "task_test", "id": "123456", "mode": "virtual radio", "actions": actions}
    with open(filename, "r") as read_file:
        message = json.load(read_file)

    # unique_sequence = uniqueid()
    # uid = next(unique_sequence)
    # message["id"] = str(uid)
    # print(message)

    return message


def uniqueid():
    seed = random.getrandbits(32)
    while True:
       yield seed
       seed += 1
