# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

from actor_logger import logger
from abc import abstractmethod
from actions.action_executor import ActionExecutor
import actions.actions_vr
import actions.actions_srsue

def get_action_executor(action):
    for cls in ActionExecutor.__subclasses__():
        logger.debug("--------------------------" + cls.__name__)
        if cls.ACTION_NAME == action.name:
            return cls(action)

    logger.error("Cannot find the action executor: " + action.name)



        
