# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

from server_logger import logger


class TestTask:

    def __init__(self, actor_name, test_scripts, test_id):
        self.actor_name = actor_name
        self.test_scripts = test_scripts
        self.test_id = test_id
        self.status = "Pending"
        self.log = ""


    def update_status(self, status):
        self.status = status

    def append_log(self, log):
        self.log = self.log + "\n"
        self.log = self.log + log
