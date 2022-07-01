# ====================================================================
#
# Licensed under the GNU General Public License v3.0;
# you may not use this file except in compliance with the License.
#
# ====================================================================

from actor_resource import ActorResource


class MessageHandler:
    def __init__(self):
        pass

    # Handle all different types of messages/requests from the actor
    # including "registration" when the actor registers for the first time,
    # "resource update" when the actor sends back the resource update,
    # and others.
    # Server-actor socket communications are all json-based. Two keys of "name", "type" are always required.
    def handle(self, actor, message):
        if message['type'] == "registration":
            actor.set_name(message['name'])
            message_sent = {"type": "registration confirmed"}
            print("Actor [" + actor.name + "] is registered!")
        elif message['type'] == "resource update":
            actor_resource = ActorResource(message['cpu'], message['mem'], message['sdr_size'])
            actor.update_resource(actor_resource)
            print("Actor [" + actor.name + "] updated its resource!")
            message_sent = {"type": "resource update confirmed"}
        elif message['type'] == "task completed":
            task_id = message['id']
            task_results = message['results']
            print("Actor [" + actor.name + "] completed the task!" + " Task ID: " + task_id)
            message_sent = {"type": "confirmed"}

        else:
            # TO DO: implement other message from the actor
            message_sent = {"type": "confirmed"}

        actor.send_msg_dict(message_sent)

message_handler = MessageHandler()
