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
            logger.info("Task running: " + task.name + " id: " + task.id)
            while True:
                action = task.next_action()
                if action is None:
                    break

                # A factory of actions is used to get the associated action executor based on the action name.
                action_exec = action_factory.get_action_executor(action)
                if action_exec is not None:
                    results = action_exec.run()
                    action.set_exec_done(results)
                else:
                    action.set_exec_failed("Cannot find the associated action executor. Please check if the action "
                                           "name is correct or the corresponding action executor is defined in the "
                                           "action_factory module!")

            logger.info("Task Done!" + task.name + " id: " + task.id)
            report_msg = task.task_completed()
            server_connection.send_msg(report_msg)

