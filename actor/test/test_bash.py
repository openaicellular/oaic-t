import subprocess
import time
import os


if __name__ == '__main__':
    namespace = 'ue1'
    #p_ue = subprocess.Popen(['sudo', 'srsue', '--rf.device_name=zmq', '--rf.device_args="tx_port=tcp://*:2001, rx_port=tcp://localhost:2000, id=ue, base_srate=23.04e6"', '--gw.netns='+namespace],
    #                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    #print(p_ue.poll())
    #print(p_ue.pid)

    p_ue = subprocess.Popen(['sudo', 'srsue', '--rf.device_name=zmq',
                             '--rf.device_args="tx_port=tcp://*:2001, rx_port=tcp://localhost:2000, id=ue, base_srate=23.04e6"',
                             '--gw.netns=' + namespace], stdout=subprocess.PIPE, bufsize=1, universal_newlines=True, text=True)
    print(p_ue.poll())
    print(p_ue.pid)

    for line in p_ue.stdout:
        print(line, end='')  # process line here

    time.sleep(5)
    subprocess.check_call(["sudo", "kill", str(p_ue.pid + 1)])
    outs, errs = p_ue.communicate()
    print("5:" + outs + errs)