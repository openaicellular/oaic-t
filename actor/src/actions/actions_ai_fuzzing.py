# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

## This module contains actions using AI Fuzzing to generate testing signals

from actor_logger import logger
from task import Action
from actions.action_executor import ActionExecutor
import time

def sendMsgToSimulator(ues)
    return

def getSimulatorKPIs(ue)
    return

# This action is to reset the simulator to the initial state
class ActionRadioSimulatorRst(ActionExecutor):
    ACTION_NAME = "Radio Simulator Reset"  ## Be sure this action name is the one used in the test script

    def run(selfs):
        ## To Be Implement
        action_output_summary = "Fail. The function is not implemented yet!"
        action_output = "N/A"
        return action_output_summary, action_output


# This action is to start UEs and generate traffic randomly
class ActionTrafficGenRandom(ActionExecutor):
    ACTION_NAME = "Random Traffic Generation"  ## Be sure this action name is the one used in the test script

    def run(self):
        ## To Be Implement
        action_output_summary = "Fail. The function is not implemented yet!"
        action_output = "N/A"
        return action_output_summary, action_output


# This action is to start UEs and generate traffic using AI Fuzzing method
class ActionTrafficGenAIF(ActionExecutor):
    ACTION_NAME = "AIF Traffic Generation"  ## Be sure this action name is the one used in the test script

    def run(self):
        print("Action running: " + self.action.name + " ...")
        ## To Be Implement
        action_output_summary = "Fail. The function is not implemented yet!"
        action_output = "N/A"
        return action_output_summary, action_output

