import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    handlers=[
                        logging.FileHandler("actor_log_debug.log"),
                        logging.StreamHandler()
                    ]
                    )
logger = logging.getLogger('OAIC-T Server')
