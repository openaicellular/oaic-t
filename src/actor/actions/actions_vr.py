# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

## This module contains actions for virtual radio applications with ZeroMQ

from actor_logger import logger
from task import Action


# This action is to create a new network namespace for one UE
# It first creates a namespace and verify the new namespace exists
class ActionCreateNS(ActionExecutor):
    ACTION_NAME = 'Create Network Namespace'  ## Be sure this action name is the one used in the test script

    def run(self):
        logger.info("------    Action to be executed: " + self.action.name + " ...")
        namespace = self.action.paras['namespace']
        
        ## TODO:
        # 1. run the bash command to create a network namespace: sudo ip netns add "namespace"(from the parameter)
        # capture and return the output of above command
        output_create_ns = ""
        # 2. Verify the new namespace netns exists, run: sudo ip netns list
        # capture the output and match up if the namespace is included in the output.
        output_list_ns = ""

        time.sleep(5)
        results = "Success! " + "Script Output: " + output_create_ns + " " + output_list_ns
        logger.info("------    Action Done!")
        return results


# This action is to run eNodeB
# It first runs eNodeB and verify if the running succeeds or not
class ActionRunUE(ActionExecutor):
    ACTION_NAME = 'Run UE'  ## Be sure this action name is the one used in the test script

    def run(self):
        logger.info("------    Action to be executed: " + self.action.name + " ...")
        # TODO: extract paras if necessary from self.action.paras

        # TODO:
        # 1. run the bash command (example): s./srsenb/src/srsenb --rf.device_name=zmq --rf.device_args="fail_on_disconnect=true,tx_port=tcp://*:2000,rx_port=tcp://localhost:2001,id=enb,base_srate=23.04e6"
        # capture and verify the output of above command
        output_run_ue = ""

        time.sleep(5)
        results = "Success! " + "Script Output: " + output_run_ue
        logger.info("------    Action Done!")
        return results
        
# This action is to generate traffic (uplink and downlink)
class ActionGenTraffic(ActionExecutor):
    ACTION_NAME = 'Generate Traffic'  ## Be sure this action name is the one used in the test script

    def run(self):
        logger.info("------    Action to be executed: " + self.action.name + " ...")
        # TODO: extract paras if necessary from self.action.paras
        
        # TODO:
        # 1. run the bash command (example for uplink): sudo ip netns exec ue1 ping 172.16.0.1
        # Questions: how to generate downlink traffic, and how to determine the traffic load.
        # capture and verify the output of above command
        output_gen_traffic = ""
	
        time.sleep(5)
        results = "Success! " + "Script Output: " + output_gen_traffic
        logger.info("------    Action Done!")
        return results