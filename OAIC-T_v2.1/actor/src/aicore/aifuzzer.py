# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

from actor_logger import logger
from abc import abstractmethod

class AIFuzzer:

    def __init__(self):
        pass

    @abstractmethod
    def next_paras(self):
        pass
        
