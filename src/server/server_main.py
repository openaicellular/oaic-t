# import thread module
from actor_manager import ActorManager


if __name__ == '__main__':
    #### TO DO: The port will be configured from configuration file.
    host = "127.0.0.1"
    port = 12345

    actor_manager = ActorManager(host, port)
    actor_manager.run()


