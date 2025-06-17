# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

import os
import psutil

def get_cpu_info():
    return psutil.cpu_percent()

def get_mem_info():
    total_memory, used_memory, free_memory = map(
        int, os.popen('free -t -m').readlines()[-1].split()[1:])
    mem_per = round(used_memory / total_memory) * 100
    return mem_per