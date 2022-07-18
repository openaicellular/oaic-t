# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

from task import Action
from abc import abstractmethod

class ActionExecutor:
    ACTION_NAME = 'None'

    def __init__(self, action):
        self.action = action

    @abstractmethod
    def run(self):
        pass