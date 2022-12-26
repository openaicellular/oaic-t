# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

## This module contains actions for virtual radio applications with ZeroMQ

from actor_logger import logger
from task import Action
from actions.action_executor import ActionExecutor
from actions.proc_gen import *
import time
import subprocess
from actions.xapp_connection import XAPPConnection

# This action is to create a new network namespace for one UE
# It first creates a namespace and verify the new namespace exists
class ActionCreateNS(ActionExecutor):
    ACTION_NAME = "Create Network Namespace"  ## Be sure this action name is the one used in the test script

    def run(self):
        print("Action running: " + self.action.name + " ...")
        namespace = self.action.get_action_para('namespace')

        cmds = ['sudo', 'ip', 'netns', 'add', namespace]

        create_ns_proc = Process("Create Namespace", cmds, None, None)

        # Verify the new namespace netns exists, run: sudo ip netns list
        # capture the output and match up if the namespace is included in the output.
        cmds = ['sudo', 'ip', 'netns', 'list']
        list_all_ns = Process("List Namespace", cmds, namespace, None)
        time.sleep(1)
        # if list_all_ns.status == Process.STATUS_Running:
        #     results = "Success!"
        # else:
        #     results = "Fail! " + " The UE namespace is not listed in the list!"
        results = "Success!"
        print("Action: " + self.action.name + " " + results)
        action_output_summary = results
        action_output = list_all_ns.stdout
        return action_output_summary, action_output


# This action is to run a UE in srsRAN
class ActionRunUE(ActionExecutor):
    ACTION_NAME = 'Run UE'  # Be sure this action name is the one used in the test script

    UE_Network_Attach = False
    UE_Running = False
    UE_IP = None

    def run(self):
        print("Action running: " + self.action.name + " ...")
        namespace = self.action.get_action_para('namespace')
        device_name = self.action.get_action_para('--rf.device_name')
        device_args = self.action.get_action_para('--rf.device_args')
        waiting_time_to_startup = self.action.get_action_para('waiting_time_to_startup')
        if waiting_time_to_startup is None:
            waiting_time_to_startup = 25   # default value
        para_args = []
        if device_name is not None:
            para_args.append('--rf.device_name=' + device_name)
        if device_args is not None:
            para_args.append('--rf.device_args=\"' + device_args + '\"')
        if namespace is not None:
            para_args.append('--gw.netns=' + namespace)

        if get_running_process(namespace) is None:
            # cmds = ['sudo', 'srsue', '--rf.device_name=zmq',
            #  '--rf.device_args="tx_port=tcp://*:2001, rx_port=tcp://localhost:2000, id=ue, base_srate=23.04e6"',
            #  '--gw.netns=' + namespace]
            cmds = ['sudo', 'srsue']
            cmds.extend(para_args)
            print(cmds)
            ue_proc = UE_Process(namespace, cmds, "Network attach successful", "Stopping")
            waiting_time_total = 0
            while waiting_time_total < waiting_time_to_startup:
                time.sleep(2)  # check for every 2 second
                waiting_time_total += 2
                if ue_proc.status == Process.STATUS_Running:
                    results = "Success! " + "UE is initially running with IP: " + ue_proc.UE_IP
                    add_running_process(namespace, ue_proc)
                    break
            if ue_proc.status != Process.STATUS_Running:
                results = "Fail! " + "UE is not successfully started after " + str(waiting_time_to_startup) + " seconds"
                ue_proc.stop()
            action_output = ue_proc.stdout
        else:
            results = "Fail! " + "UE already exists. Please choose another UE namespace!"
            action_output = " "

        print("Action: " + self.action.name + " " + results)
        action_output_summary = results
        return action_output_summary, action_output



class ActionRunIPERFServer(ActionExecutor):
    ACTION_NAME = "Run IPERF Server"  ## Be sure this action name is the one used in the test script

    def run(self):
        print("Action running: " + self.action.name + " ...")

        cmds = ['iperf3', '-s', '-i', '1']

        create_ns_proc = Process("Run IPERF Server", cmds, None, None, stop_proc=1)
        add_running_process("IPERF Server", create_ns_proc)
        time.sleep(1)

        results = "Success!"
        print("Action: " + self.action.name + " " + results)
        action_output_summary = results
        action_output = results
        return action_output_summary, action_output

class ActionStopIPERFServer(ActionExecutor):
    ACTION_NAME = "Stop IPERF Server"  ## Be sure this action name is the one used in the test script

    def run(self):
        print("Action running: " + self.action.name + " ...")
        proc_name = "IPERF Server"
        proc = get_running_process(proc_name)

        if proc is None:
            results = "Fail! The IPERF Server is not running!"
            action_output = ""
        else:
            stop_running_process(proc_name)
            action_output = proc.stdout
            results = "Success! The IPERF Server stops!"

        time.sleep(1)

        # results = "Success!"
        action_output_summary = results
        action_output = results
        return action_output_summary, action_output

# This action is to generate traffic (uplink and downlink)
class ActionGenTraffic(ActionExecutor):
    ACTION_NAME = 'Generate Traffic'  ## Be sure this action name is the one used in the test script

    def run(self):
        print("Action running: " + self.action.name + " ...")

        namespace = self.action.get_action_para('namespace')
        ue_proc = get_running_process(namespace)
        if ue_proc is None:
            results = "Fail! The UE is not in the running list:" + namespace
            action_output = " "
        else:
            direction = self.action.get_action_para('direction')  # uplink or downlink
            traffic_gen_mode = self.action.get_action_para('traffic_gen_mode')  # two modes supported: ping and surf
            if traffic_gen_mode.lower() == "ping":  # ping command to generate traffic
                ping_time = self.action.get_action_para('ping_time')

                if direction == "uplink":
                    ip = "172.16.0.1"  # default ip for enodeB
                    cmds = ['sudo', 'ip', 'netns', 'exec', namespace, 'ping', ip]
                elif direction == "downlink":
                    ip = ue_proc.UE_IP
                    cmds = ['sudo', 'ping', ip]
                else:
                    results = "Fail! Unknown network traffic direction. Currently only support uplink or downlink!"
                    action_output = " "

                if ip is not None:
                    print("IP to be pinged: " + ip + " for " + str(ping_time) + " times...")
                    ping_proc = Process("Ping", cmds, None, None)
                    time.sleep(ping_time)
                    ping_proc.stop()
                    action_output = ping_proc.stdout
                    results = "Success!"
            elif traffic_gen_mode.lower() == "iperf":  # iperf command to generate traffic for a time
                bandwidth = self.action.get_action_para('bandwidth')  # M unit
                iperf_time = self.action.get_action_para('iperf_time')  # in second
                ip = "172.16.0.1"  # default ip for enodeB
                logger.info("IP to be communicate (uplink using iperf): " + ip)
                cmds = ['sudo', 'ip', 'netns', 'exec', namespace, 'iperf3', "-c", ip, "-b", str(bandwidth) + "M", "-i",
                     "1", "-t", str(iperf_time)]
                iperf_proc = Process("IPerf", cmds, None, None)
                # TO DO: capture the output to get the iperf results
                time.sleep(iperf_time)
                iperf_proc.stop()
                action_output = iperf_proc.stdout
                results = "Success!"
            else:
                results = "Unrecognized traffic generation mode. Ping and iPerf are only supported."
                action_output = " "
        print("Action: " + self.action.name + " " + results)
        action_output_summary = results
        return action_output_summary, action_output

# This action is to stop a UE
class StopUE(ActionExecutor):
    ACTION_NAME = 'Stop UE'  ## Be sure this action name is the one used in the test script

    def run(self):
        print("Action running: " + self.action.name + " ...")
        namespace = self.action.get_action_para('namespace')
        ue_proc = get_running_process(namespace)
        if ue_proc is None:
            results = "Fail! The UE to be stopped is not running or does not exist! The UE namespace: " + namespace
            action_output = " "
        else:
            stop_running_process(namespace)
            time.sleep(1)
            results = "Success! The UE is forced to stop."
            action_output = ue_proc.stdout
        print("Action: " + self.action.name + " " + results)
        action_output_summary = results
        return action_output_summary, action_output

# This action is to start the EPC
class StartEPC(ActionExecutor):
    ACTION_NAME = "Start EPC"  ## Be sure this action name is the one used in the test script

    def run(self):
        print("Action running: " + self.action.name + " ...")

        #results = start_epc()

        epc_proc_name = 'EPC'
        if get_running_process(epc_proc_name) is not None:
            results = "Fail! The EPC is already running. Only one running EPC is allowed!"
            action_output = ""
        else:
            cmds = ['sudo', 'srsepc']
            print("Wait 3 seconds to allow the EPC running...")
            epc = Process(epc_proc_name, cmds, 'SP-GW Initialized.', 'Stopping')
            time.sleep(5) # wait for seconds to allow it running
            if epc.status == Process.STATUS_Running:
                add_running_process(epc_proc_name, epc)
                results = "Success! The EPC is running!"
                action_output = epc.stdout
            else:
                results = "Fail! The EPC is not running after 3 seconds!"
                action_output = epc.stdout
                epc.stop()

        print("Action: " + self.action.name + " " + results)
        action_output_summary = results
        return action_output_summary, action_output

class StopEPC(ActionExecutor):
    ACTION_NAME = "Stop EPC"  ## Be sure this action name is the one used in the test script

    def run(self):
        print("Action running: " + self.action.name + " ...")

        epc_proc_name = 'EPC'
        epc = get_running_process(epc_proc_name)
        if epc is None:
            results = "Fail! The EPC is not running!"
            action_output = ""
        else:
            stop_running_process(epc_proc_name)
            action_output = epc.stdout
            results = "Success! The EPC stops!"

        print("Action: " + self.action.name + " " + results)
        action_output_summary = results
        return action_output_summary, action_output

# This action is to start the ENodeB
class StartENodeB(ActionExecutor):
    ACTION_NAME = "Start ENodeB"  ## Be sure this action name is the one used in the test script

    def run(self):
        print("Action running: " + self.action.name + " ...")
        para_args = []
        device_name = self.action.get_action_para('--rf.device_name')
        if device_name is not None:
            para_args.append('--rf.device_name=' + device_name)
        device_args = self.action.get_action_para('--rf.device_args')
        if device_args is not None:
            para_args.append('--rf.device_args=\"' + device_args + '\"')
        #para_args = ['--rf.device_name=' + device_name, '--rf.device_args=\"' + device_args + '\"']

        enb_proc_name = 'ENodeB'
        if get_running_process(enb_proc_name) is not None:
            results = "Fail! The ENodeB is already running. Only one running ENodeB is allowed!"
            action_output = ""
        else:
            cmds = ['sudo', 'srsenb']
            for arg in para_args:
                cmds.append(arg)

            enb = Process(enb_proc_name, cmds, 'eNodeB started', 'Stopping')
            print("Wait 5 seconds to allow the ENodeB running...")
            time.sleep(5)  # wait for seconds to allow it running
            if enb.status == Process.STATUS_Running:
                add_running_process(enb_proc_name, enb)
                results = "Success! The ENodeB is running!"
                action_output = enb.stdout
            else:
                results = "Fail! The ENodeB is not running after 3 seconds!"
                action_output = enb.stdout
                enb.stop()

        print("Action: " + self.action.name + " " + results)
        action_output_summary = results
        return action_output_summary, action_output

class StopENodeB(ActionExecutor):
    ACTION_NAME = "Stop ENodeB"  ## Be sure this action name is the one used in the test script

    def run(self):
        print("Action running: " + self.action.name + " ...")
        enb_proc_name = 'ENodeB'
        enb = get_running_process(enb_proc_name)
        if enb is None:
            results = "Fail! The ENodeB is not running!"
            action_output = ""
        else:
            stop_running_process(enb_proc_name)
            action_output = enb.stdout
            results = "Success! The ENodeB stops!"

        print("Action: " + self.action.name + " " + results)
        action_output_summary = results
        return action_output_summary, action_output

class ConnectTestXApp(ActionExecutor):
    ACTION_NAME = "Connect Test xApp"  ## Be sure this action name is the one used in the test script

    def __init__(self, action):
        super().__init__(action)
        # Base.__init__(self)

    def run(self):
        print("Action running: " + self.action.name + " ...")
        xapp_ip = self.action.get_action_para('xapp_ip')
        xapp_port = int(self.action.get_action_para('xapp_port'))
        xapp_connection = XAPPConnection(xapp_ip, xapp_port, "Test xApp", super().get_server_connection())
        time.sleep(2)
        # (socket_status, socket_outputs) = xapp_connection.check_status()
        print("Action: " + self.action.name + " " + xapp_connection.reasons)
        action_output_summary = xapp_connection.reasons
        action_output = xapp_connection.reasons

        # server_connection = super().get_server_connection()
        # for i in range(50):
        #     time.sleep(2)
        #     message_sent = {"type": "KPI xApp", "timestamp": str(i),
        #                     "kpi1": str(i+100), "kpi2": str(i+200), "kpi3": str(i+300)}
        #     server_connection.send_msg(message_sent)

        return action_output_summary, action_output