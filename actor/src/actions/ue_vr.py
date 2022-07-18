# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

## This module contains actions for virtual radio applications with ZeroMQ

from actor_logger import logger
import subprocess
from _thread import *
import threading
import re

ue_running_dict = {}

def check_ue_running(ue_id):
    return ue_id in ue_running_dict.keys()

def add_running_ue_pid(ue_id, ue):
    ue_running_dict[ue_id] = ue

def get_ue_running(ue_id):
    if ue_id in ue_running_dict.keys():
        return ue_running_dict[ue_id]
    else:
        return None

def remove_ue_running(ue_id):
    del ue_running_dict[ue_id]

def stop_all_ue_running():
    for ue_id in ue_running_dict.keys():
        ue = ue_running_dict[ue_id]
        ue.stop()

class UE:
    STATUS_NotStarted = 'Not Started'
    STATUS_Running = 'Running'
    STATUS_RAC = 'Random Access Completed'
    STATUS_NetworkAttached = 'Network Attached'
    STATUS_Terminated = 'Terminated'

    def __init__(self, ue_id):
        self.ue_id = ue_id
        self.process = None
        self.status = UE.STATUS_NotStarted
        self.UE_IP = None
        self.stdout = ""
        self.results = ""
        self.return_code = None
        self.line_num = 0

    def process_thread(self):
        self.process = subprocess.Popen(['sudo', 'srsue', '--rf.device_name=zmq',
                                 '--rf.device_args="tx_port=tcp://*:2001, rx_port=tcp://localhost:2000, id=ue, base_srate=23.04e6"',
                                 '--gw.netns=' + self.ue_id],
                                stdout=subprocess.PIPE, bufsize=1, universal_newlines=True, text=True)

        for line in self.process.stdout:
            print(line, end='')
            self.stdout = self.stdout + line
            self.line_num = self.line_num + 1
            if 'Random Access Complete' in line:
                self.status = UE.STATUS_RAC
            if 'Network attach successful' in line:
                self.status = UE.STATUS_NetworkAttached
                ip_pattern = re.compile(r'[0-9]+(?:\.[0-9]+){3}')
                self.UE_IP = ip_pattern.findall(line)[0]
                if self.UE_IP is not None:
                    self.status = UE.STATUS_Running
                    add_running_ue_pid(self.ue_id, self)

                if 'Stopping' in line or 'Forcing exit' in line:
                    return_code = self.process.poll()
                    self.status = UE.STATUS_Terminated
                    stop()

    def execute(self):
        start_new_thread(self.process_thread, ())

    def check_process_stop(self, timeout):
        return_code = self.process.poll()
        if return_code is not None:
            self.status = UE.STATUS_Terminated
            self.return_code = return_code

    def stop(self):
        logger.info("Stops the UE: " + self.ue_id + ", pid: " + str(self.process.pid) + "...")
        subprocess.check_call(["sudo", "kill", str(self.process.pid + 1)])  # note: p_ue.pid is for sudo
        subprocess.check_call(["sudo", "kill", str(self.process.pid)])  # note: p_ue.pid is for sudo
        remove_ue_running(self.ue_id)
        logger.info("UE Stopped!")

