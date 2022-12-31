# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

import threading
import time
from actor_logger import logger
import task
import action_factory

thread_lock = threading.Lock()

pending_tasks = []
past_tasks = []


# Push a new task: It must use thread lock(s) as the other thread may pop a task at the same time
def register_new_task(new_task):
    thread_lock.acquire()
    pending_tasks.append(new_task)
    thread_lock.release()


# Pop the next task. It must use thread lock(s) as the other thread may push new tasks at the same time
def next_task():
    thread_lock.acquire()
    if len(pending_tasks) > 0:
        task = pending_tasks.pop()
        thread_lock.release()
    else:
        task = None
        thread_lock.release()
    return task


def run(server_connection):
    # A forever loop to execute all tasks one by one, and wait new tasks when no task is available.
    while True:
        task = next_task()
        if task is None:
            time.sleep(0.5)
        else:
            # logger.info( "Task running: " + task.name + " id: " + task.id + " action list (first 5 actions): " +
            # task.first_five_actions_str())
            print("Task running: " + task.name + " id: " + task.id)
            report_msg = task.task_running()
            server_connection.send_msg(report_msg)
            time.sleep(0.5)

            while True:
                action = task.next_action()
                if action is None:
                    break

                report_msg = action.action_running(task.id)
                server_connection.send_msg(report_msg)
                time.sleep(0.5)

                # A factory of actions is used to get the associated action executor based on the action name.
                action_exec = action_factory.get_action_executor(action)
                action_exec.set_server_connection(server_connection)
                if action_exec is not None:
                    action_output_summary, action_output = action_exec.run()
                    report_msg = action.action_completed(task.id, action_output_summary, action_output)
                else:
                    action_output_summary = "Cannot find the associated action executor. Please check if the action " \
                                            "name is correct or the corresponding action executor is defined in the " \
                                            "action_factory module! "
                    report_msg = action.action_notfound(task.id, action_output_summary)

                server_connection.send_msg(report_msg)
                time.sleep(0.5)

            print("Task Done!" + task.name + " id: " + task.id)
            report_msg = task.task_completed()
            server_connection.send_msg(report_msg)
