# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

from actor_resource import ActorResource
import json

class MessageHandler:
    def __init__(self):
        pass

    # Handle all different types of messages/requests from the actor
    # including "registration" when the actor registers for the first time,
    # "resource update" when the actor sends back the resource update,
    # and others.
    # Server-actor socket communications are all json-based. Two keys of "name", "type" are always required.
    def handle(self, actor, message, actor_manager):
        if message['type'] == "registration":
            actor.set_name(message['name'])
            message_sent = {"type": "registration confirmed"}
            print("Actor [" + actor.name + "] is registered!")
            actor_manager.register_actor_with_name(actor)
        elif message['type'] == "resource update":
            actor_resource = ActorResource(message['cpu'], message['mem'], message['sdr_size'])
            actor.update_resource(actor_resource)
            # print("Actor [" + actor.name + "] updated its resource!" + actor_resource.cpu + ": " + actor_resource.mem)
            actor_manager.update_actor_rsc(actor.name, actor_resource)
            message_sent = {"type": "resource update confirmed"}
        elif message['type'] == "task running":
            task_id = message['id']
            task_results = message['results']
            message_sent = {"type": "confirmed"}
            actor_manager.update_test_logs(task_id, task_results)
            actor_manager.update_test_status(task_id, "Running")
        elif message['type'] == "task completed":
            task_id = message['id']
            task_results = message['results']
            # print("Actor [" + actor.name + "] completed the task!" + " Task ID: " + task_id)
            message_sent = {"type": "confirmed"}
            actor_manager.update_test_logs(task_id, task_results)
            actor_manager.update_test_status(task_id, "Completed")
        elif message['type'] == "action running":
            task_id = message['id']
            action_results = message['results']
            message_sent = {"type": "confirmed"}
            actor_manager.update_test_logs(task_id, action_results)
        elif message['type'] == "action completed":
            task_id = message['id']
            action_results = message['results']
            message_sent = {"type": "confirmed"}
            actor_manager.update_test_logs(task_id, action_results)
            output_summary = message['output summary']
            actor_manager.update_test_logs(task_id, ">>>>>> Details:" + output_summary)
        elif message['type'] == "action failed":
            task_id = message['id']
            action_results = message['results']
            message_sent = {"type": "confirmed"}
            actor_manager.update_test_logs(task_id, action_results)
            output_summary = message['output summary']
            actor_manager.update_test_logs(task_id, ">>>>>> Details:" + output_summary)
        elif message['type'] == "KPI xApp":
            print("Received KPI xApp data: ")
            print(message)
            message_sent = {"type": "confirmed"}
            kpi_all_dict = dict()
            ue_kpi_kept = ["PRB-Usage-DL", "PRB-Usage-UL", "QCI", "fiveQI", "MeasPeriodUEPRBUsage", "Meas-Period-PDCP", "Meas-Period-RF", "Number-of-Active-UEs"]
            cell_kpi_kept = ["PDCP-Bytes-DL", "PDCP-Bytes-UL", "Avail-PRB-DL", "Avail-PRB-UL", "Meas-Period-PDCPBytes", "MeasPeriodAvailPRB", "Total-Available-PRBs-DL",
                           "Total-Available-PRBs-UL"]

            count_ue = 0
            count_cell = 0
            count = 0
            if "UE Metrics" in message.keys():
                ue_metrics = message["UE Metrics"]
                ue_metrics = json.loads(ue_metrics[0][0], strict=False)
                for k in ue_metrics.keys():
                    # if k.startswith("kpi"):
                    if k in ue_kpi_kept:
                        kpi_all_dict["UE_"+k] = float(ue_metrics[k])
                        count_ue += 1
                        count += 1
            if "Cell Metrics" in message.keys():
                cell_metrics = message["Cell Metrics"]
                cell_metrics = json.loads(cell_metrics[0][0], strict=False)
                for k in cell_metrics.keys():
                    #if k.startswith("kpi"):
                    if k in cell_kpi_kept:
                        kpi_all_dict["Cell_"+k] = float(cell_metrics[k])
                        count_cell += 1
                        count += 1
            #timestamp = message["timestamp"]
            print("KPI metrics received: " + str(count_ue) + " UE metrics, " + str(count_cell) + " Cell metrics!")
            if (count_ue + count_cell) >= 1:
                timestamp = str(count_ue + count_cell)
                actor_manager.update_kpi_xapp(timestamp, kpi_all_dict)

        else:
            # TO DO: implement other message from the actor
            message_sent = {"type": "confirmed"}

        actor.send_msg_dict(message_sent)

message_handler = MessageHandler()
