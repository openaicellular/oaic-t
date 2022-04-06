from actor_resource import ActorResource


class MessageHandler:
    def __init__(self):
        pass

    def handle(self, actor, message):
        ## TO DO: this function should handle different messages from the actor, depending on the type of the message.

        ## This is just an example for testing
        # reverse the given string from client
        if (message['type'] == "registration"):
            actor.set_name(message['name'])
            message_sent = {"type": "registration confirmed"}
        elif (message['type'] == "resource udpate"):
            actor_resource = ActorResource(message['cpu'], message['mem'], message['sdr_size'])
            actor.update_resource(actor_resource)
            message_sent = {"type": "resource update confirmed"}
        else:
            ## TO DO: implement other message from the actor
            message_sent = {"type": "confirmed"}

        actor.send_msg_dict(message_sent)

message_handler = MessageHandler()
