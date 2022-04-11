# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

# This module implements the loading of one or more test scripts
def read_test_script_xml(filename):
    # TO DO: read xml and convert it into a dict, one example given as follows:
    action1 = {'name': "Action 1", 'paras': "paras examples", 'type': "running"}
    action2 = {'name': "Action 2", 'paras': "paras examples", 'type': "running"}
    action3 = {'name': "Action 3", 'paras': "paras examples", 'type': "running"}
    actions = [action1, action2, action3]
    message = {"name": "task_test", "id": "123456", 'actions': actions}
    return message
