# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

## This module contains actions for virtual radio applications with ZeroMQ
import time

from actor_logger import logger
import subprocess
from _thread import *
import threading
import re

all_running_processes = {}

def add_running_process(proc_name, proc):
    all_running_processes[proc_name] = proc

def remove_running_process(proc_name):
    del all_running_processes[proc_name]

def get_running_process(proc_name):
    if proc_name in all_running_processes.keys():
        return all_running_processes[proc_name]
    else:
        return None

def stop_running_process(proc_name):
    if proc_name in all_running_processes.keys():
        proc = all_running_processes[proc_name]
        proc.stop()
        remove_running_process(proc_name)

def stop_all_running_process():
    all_processes = all_running_processes.keys()
    for proc_name in list(all_processes):
        print("Stopping the process: " + proc_name + "...")
        stop_running_process(proc_name)
        print("Success!")


class Process:
    STATUS_NotStarted = 'Not Started'
    STATUS_Running = 'Running'
    STATUS_Terminated = 'Terminated'

    def __init__(self, process_name, cmds, running_str_indicator, stop_str_indicator, stop_proc=2):
        self.process_name = process_name
        self.process = None
        self.status = Process.STATUS_NotStarted
        self.stdout = ""
        self.results = ""
        self.return_code = None
        self.line_num = 0
        self.running_str_indicator = running_str_indicator
        self.stop_str_indicator = stop_str_indicator
        self.stop_proc = stop_proc
        self.cmds = cmds
        self.thread = None
        self.execute()


    def process_thread(self):
        self.process = subprocess.Popen(self.cmds,
                                        stdout=subprocess.PIPE, bufsize=1, universal_newlines=True, text=True)
        self.console_output_monitoring()

    def console_output_monitoring(self):
        for line in self.process.stdout:
            print(line, end='')
            self.stdout = self.stdout + line
            self.line_num = self.line_num + 1
            if self.running_str_indicator is None or self.running_str_indicator in line:  # if running_str_indicator is None, the process will always be running
                self.status = Process.STATUS_Running
            if self.stop_str_indicator is not None and self.stop_str_indicator in line:  # if stop_str_indicator is None, the process will never terminate itself
                self.status = Process.STATUS_Terminated

    def execute(self):
        #self.thread = start_new_thread(self.process_thread, ())
        self.thread = threading.Thread(target=self.process_thread, args=())
        self.thread.daemon = True
        self.thread.start()

    def check_process_stop(self, timeout):
        return_code = self.process.poll()
        if return_code is not None:
            self.status = Process.STATUS_Terminated
            self.return_code = return_code

    def stop(self):
        if self.stop_proc == 2:
            try:
                subprocess.check_call(["sudo", "kill", str(self.process.pid + 1), "-9"])  # note: pid is for sudo
            except subprocess.CalledProcessError:
                pass

        try:
            subprocess.check_call(["sudo", "kill", str(self.process.pid), "-9"])
        except subprocess.CalledProcessError:
            pass





class UE_Process(Process):
    UE_IP = None

    def console_output_monitoring(self):
        for line in self.process.stdout:
            print(line, end='')
            self.stdout = self.stdout + line
            self.line_num = self.line_num + 1

            if self.running_str_indicator in line:
                ip_pattern = re.compile(r'[0-9]+(?:\.[0-9]+){3}')
                self.UE_IP = ip_pattern.findall(line)[0]
                if self.UE_IP is not None:
                    self.status = Process.STATUS_Running

            if self.stop_str_indicator is not None and self.stop_str_indicator in line:  # if stop_str_indicator is None, the process will never terminate itself
                self.status = Process.STATUS_Terminated
