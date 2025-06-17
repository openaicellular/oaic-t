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
from actions.proc_gen import *
import time
import subprocess
from actions.xapp_connection import XAPPConnection

# This action is to launch the gNB in the Open Air Interface 5G framework
class StartGNBOAI(ActionExecutor):
    ACTION_NAME = "Start OAI_gNB"  ## Be sure this action name is the one used in the test script

    def run(self):
        print("Action running: " + self.action.name + " ...")
        para_args = []
        config_file = self.action.get_action_para('--config_file')
        if config_file is not None:
            para_args.append('-c ' + config_file)

        gnb_proc_name = 'gNB'
        if get_running_process(gnb_proc_name) is not None:
            results = "Fail! The gNB is already running. Only one running gNB is allowed!"
            action_output = ""
        else:
            cmds = ['sudo', 'nr-softmodem', '-O']
            for arg in para_args:
                cmds.append(arg)

            gnb = Process(gnb_proc_name, cmds, 'gNB started', 'Stopping')
            print("Wait 5 seconds to allow the gNB to start...")
            time.sleep(5)  # wait for seconds to allow it running
            if gnb.status == Process.STATUS_Running:
                add_running_process(gnb_proc_name, gnb)
                results = "Success! The gNB is running!"
                action_output = gnb.stdout
            else:
                results = "Fail! The gNB is not running after 5 seconds!"
                action_output = gnb.stdout
                gnb.stop()

        print("Action: " + self.action.name + " " + results)
        action_output_summary = results
        return action_output_summary, action_output

class StopGNBOAI(ActionExecutor):
    ACTION_NAME = "Stop OAI_gNB"  ## Be sure this action name is the one used in the test script

    def run(self):
        print("Action running: " + self.action.name + " ...")
        gnb_proc_name = 'gNB'
        gnb = get_running_process(gnb_proc_name)
        if gnb is None:
            results = "Fail! The gNB is not running!"
            action_output = ""
        else:
            stop_running_process(gnb_proc_name)
            action_output = gnb.stdout
            results = "Success! The gNB stops!"

        print("Action: " + self.action.name + " " + results)
        action_output_summary = results
        return action_output_summary, action_output

# This action is to launch the UE in the Open Air Interface 5G framework
class StartUEOAI(ActionExecutor):
    ACTION_NAME = "Start OAI_UE"  ## Be sure this action name is the one used in the test script

    def run(self):
        print("Action running: " + self.action.name + " ...")
        para_args = []
        config_file = self.action.get_action_para('--config_file')
        if config_file is not None:
            para_args.append('-c ' + config_file)

        ue_proc_name = 'UE'
        if get_running_process(ue_proc_name) is not None:
            results = "Fail! The UE is already running. Only one running UE is allowed!"
            action_output = ""
        else:
            cmds = ['sudo', 'nr-ue', '-O']
            for arg in para_args:
                cmds.append(arg)

            ue = Process(ue_proc_name, cmds, 'UE started', 'Stopping')
            print("Wait 5 seconds to allow the UE to start...")
            time.sleep(5)  # wait for seconds to allow it running
            if ue.status == Process.STATUS_Running:
                add_running_process(ue_proc_name, ue)
                results = "Success! The UE is running!"
                action_output = ue.stdout
            else:
                results = "Fail! The UE is not running after 5 seconds!"
                action_output = ue.stdout
                ue.stop()

        print("Action: " + self.action.name + " " + results)
        action_output_summary = results
        return action_output_summary, action_output

class StopUEOAI(ActionExecutor):
    ACTION_NAME = "Stop OAI_UE"  ## Be sure this action name is the one used in the test script

    def run(self):
        print("Action running: " + self.action.name + " ...")
        ue_proc_name = 'UE'
        ue = get_running_process(ue_proc_name)
        if ue is None:
            results = "Fail! The UE is not running!"
            action_output = ""
        else:
            stop_running_process(ue_proc_name)
            action_output = ue.stdout
            results = "Success! The UE stops!"

        print("Action: " + self.action.name + " " + results)
        action_output_summary = results
        return action_output_summary, action_output
