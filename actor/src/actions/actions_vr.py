# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

## This module contains actions for virtual radio applications with ZeroMQ

from actor_logger import logger
from task import Action
from actions.action_executor import ActionExecutor
from actions.ue_vr import *
import time
import subprocess


# This action is to create a new network namespace for one UE
# It first creates a namespace and verify the new namespace exists
class ActionCreateNS(ActionExecutor):
    ACTION_NAME = "Create Network Namespace"  ## Be sure this action name is the one used in the test script

    def run(self):
        print("Action running: " + self.action.name + " ...")
        namespace = self.action.paras['namespace']

        result = subprocess.run(['sudo', 'ip', 'netns', 'add', namespace], stdout=subprocess.PIPE)

        # Verify the new namespace netns exists, run: sudo ip netns list
        # capture the output and match up if the namespace is included in the output.
        result = subprocess.run(['sudo', 'ip', 'netns', 'list'], stdout=subprocess.PIPE)
        output_list_ns = result.stdout.decode("utf-8")

        if namespace in output_list_ns:
            results = "Success!"
        else:
            results = "Fail! " + " The UE namespace is not listed in the list!"
        print("Action: " + self.action.name + " " + results)
        action_output_summary = results
        action_output = output_list_ns
        return action_output_summary, action_output


# This action is to run a UE in srsRAN
class ActionRunUE(ActionExecutor):
    ACTION_NAME = 'Run UE'  # Be sure this action name is the one used in the test script

    UE_Network_Attach = False
    UE_Running = False
    UE_IP = None

    def run(self):
        print("Action running: " + self.action.name + " ...")
        namespace = self.action.paras['namespace']

        if not check_ue_running(namespace):
            ue = UE(namespace)
            ue.execute()
            print("Action running: " + self.action.name + " ...")
            print("Wait for 10 seconds to allow the UE start ...")
            time.sleep(10)  # wait for 10 second to allow it to be started
            if ue.status == UE.STATUS_Running:
                results = "Success! " + "UE is initially running with IP: " + ue.UE_IP
            else:
                results = "Fail! " + "UE is not successfully started after 10 seconds"
        else:
            results = "Fail! " + "UE already exists. Please choose another UE namespace!"

        print("Action: " + self.action.name + " " + results)
        action_output_summary = results
        action_output = ue.stdout
        return action_output_summary, action_output


# This action is to generate traffic (uplink and downlink)
class ActionGenTraffic(ActionExecutor):
    ACTION_NAME = 'Generate Traffic'  ## Be sure this action name is the one used in the test script

    def run(self):
        print("Action running: " + self.action.name + " ...")

        namespace = self.action.paras['namespace']

        direction = self.action.paras['direction']  # uplink or downlink

        ping_time = self.action.paras['ping_time']

        ue = get_ue_running(namespace)
        if ue is None:
            results = "Fail! The UE is not in the running list:" + namespace
        else:
            if direction == "uplink":
                ip = "172.16.0.1"  # default ip for enodeB
            elif direction == "downlink":
                ip = ue.UE_IP
            else:
                results = "Fail! Unknown network traffic direction. Currently only support uplink or downlink!"
                return results

            logger.info("IP to be pinged: " + ip)
            #result = subprocess.run(['sudo', 'ping', ip], stdout=subprocess.PIPE, timeout=10)
            process = subprocess.Popen(['sudo', 'ping', ip],
                                            stdout=subprocess.PIPE, bufsize=1, universal_newlines=True, text=True)
            ping_count = 0
            ping_output = ""
            for line in process.stdout:
                print(line, end='')
                ping_output = ping_output + line
                ping_count = ping_count + 1
                if ping_count == ping_time:
                    break

            results = "Success!"
        print("Action: " + self.action.name + " " + results)
        action_output_summary = results
        action_output = ping_output
        return action_output_summary, action_output

# This action is to stop a UE
class StopUE(ActionExecutor):
    ACTION_NAME = 'Stop UE'  ## Be sure this action name is the one used in the test script

    def run(self):
        print("Action running: " + self.action.name + " ...")
        namespace = self.action.paras['namespace']
        ue = get_ue_running(namespace)
        if ue is None:
            results = "Fail! The UE to be stopped is not running or does not exist! The UE namespace: " + namespace
        else:
            ue.stop()
            time.sleep(5)  # wait 5 second to allow it to be stopped
            results = "Success! The UE is forced to stop."
        print("Action: " + self.action.name + " " + results)
        action_output_summary = results
        action_output = ue.stdout
        return action_output_summary, action_output

