# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

from actor_logger import logger
from task import Action
import time
from abc import abstractmethod


class ActionExecutor:
    ACTION_NAME = 'None'

    def __init__(self, action):
        self.action = action

    @abstractmethod
    def run(self):
        pass


def get_action_executor(action):
    for cls in ActionExecutor.__subclasses__():
        logger.debug("--------------------------" + cls.__name__)
        if cls.ACTION_NAME == action.name:
            return cls(action)

    logger.error("Cannot find the action executor: " + action.name)


# This is an example of an action implementation. Users can implement their own actions, while
# several commonly used actions are already provided.
class ActionExample1(ActionExecutor):
    ACTION_NAME = 'Action 1'  ## Be sure this action name is the one used in the test script

    def run(self):
        logger.info("------    Action to be executed: " + self.action.name + " ...")
        ## TO DO: An action factory should be implemented here to run specific actions

        time.sleep(5)
        results = "Success!"
        logger.info("------    Action Done!")
        return results


class ActionExample2(ActionExecutor):
    ACTION_NAME = 'Action 2'  ## Be sure this action name is the one used in the test script

    def run(self):
        logger.info("------    Action to be executed: " + self.action.name + " ...")
        ## TO DO: An action factory should be implemented here to run specific actions

        time.sleep(5)
        results = "Success!"
        logger.info("------    Action Done!")
        return results
