# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

import sys

sys.path.append("../../src/server/")

from test_script_reader import read_test_script_xml


if __name__ == '__main__':
    message = read_test_script_xml("test.xml")
    actions = message["actions"]
    action1 = actions[0]
    print(message)
    print(action1)
    print(action1['paras'])
    print(action1['paras']['namespace'])


