#############################################################################################################################
# Class for generating different types of traffic (voice, video, gaming, IoT).# traffic_generator.py is in traffic folder   #
# The TrafficController class is responsible for simulating different types of network traffic for User Equipments (UEs)    #
# in a 5G network simulation environment. It generates traffic based on predefined parameters for voice, video, gaming, IoT,#
# and data services. The class also supports custom traffic generation based on severity levels, allowing for the simulation#
# of network conditions ranging from low to ultra severity.                                                                 #
#############################################################################################################################
import random
import time
from datetime import datetime
from logs.logger_config import traffic_update_logger
from network.ue import UE
from database.database_manager import DatabaseManager
import threading
from network.ue_manager import UEManager
import os
class TrafficController:
    _instance = None
    _lock = threading.Lock()  # Ensure thread-safe singleton access
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TrafficController, cls).__new__(cls)
                cls._instance.__initialized = False
            return cls._instance

    def __init__(self):
        if self.__initialized: return
        self.__initialized = True
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.ue_manager = UEManager.get_instance(base_dir)
        self.ues = {} # Dictionary to track UEs
        self.traffic_logs = []
        self.voice_traffic_params = {'bitrate': (8, 16)}  # in Kbps
        self.video_traffic_params = {'num_streams': (1, 5), 'stream_bitrate': (3, 8)}  # in Mbps
        self.gaming_traffic_params = {'bitrate': (30, 70)}  # in Kbps
        self.iot_traffic_params = {'packet_size': (5, 15), 'interval': (10, 60)}  # packet size in KB, interval in seconds
        self.data_traffic_params = {'bitrate': (10, 100), 'interval': (0.5, 2)}  # in Mbps
        # Initialize jitter, delay, and packet loss for each traffic type
        #for example (5, 15)  # Jitter range in milliseconds or (10, 50)  # Delay range in milliseconds or (0.01, 0.05)  # Packet loss rate range
        self.ue_voice_jitter = 0
        self.ue_voice_delay = 0
        self.ue_voice_packet_loss_rate = 0
        self.ue_video_jitter = 0
        self.ue_video_delay = 0
        self.ue_video_packet_loss_rate = 0
        self.ue_gaming_jitter = 0
        self.ue_gaming_delay = 0
        self.ue_gaming_packet_loss_rate = 0
        self.ue_iot_jitter = 0
        self.ue_iot_delay = 0
        self.ue_iot_packet_loss_rate = 0
        self.ue_data_jitter = 0
        self.ue_data_delay = 0
        self.ue_data_packet_loss_rate = 0.1
    
    #Defines parameters for different severity levels of network conditions
    SEVERITY_LEVELS = {
        'zero': {
            'multiplier': 1,
            'delay': (0, 0),
            'jitter': (0, 0),
            'packet_loss_rate': 0.0
        },

        'low': {
            'multiplier': 1,
            'delay': (0, 5),
            'jitter': (0, 5),
            'packet_loss_rate': 0.01
        },
        'medium': {
            'multiplier': 5,
            'delay': (5, 15),
            'jitter': (5, 10),
            'packet_loss_rate': 0.05
        },
        'harsh': {
            'multiplier': 10,
            'delay': (15, 50),
            'jitter': (10, 20),
            'packet_loss_rate': 0.1
        },
        'ultra': {
        'multiplier': 20,
        'delay': (50, 100),
        'jitter': (20, 50),
        'packet_loss_rate': 0.02
    },
    }
    def generate_traffic(self, ue, severity='zero'):
        #print(f"---------Inside traffic_generator.py --------Generating traffic for UE: {ue.ID}")
        if not ue.generating_traffic:
            print(f"Traffic generation for UE {ue.ID} is stopped.")
            return {
                'data_size': 0,
                'start_timestamp': datetime.now(),
                'end_timestamp': datetime.now(),
                'interval': 1,
                'ue_delay': 0,
                'ue_jitter': 0,
                'ue_packet_loss_rate': 0
            }
        if ue.ServiceType.lower() == 'voice':
            traffic_data = self.generate_voice_traffic(ue, severity)
        elif ue.ServiceType.lower() == 'video':
            traffic_data = self.generate_video_traffic(ue, severity)
        elif ue.ServiceType.lower() == 'game':
            traffic_data = self.generate_gaming_traffic(ue, severity)
        elif ue.ServiceType.lower() == 'iot':
            traffic_data = self.generate_iot_traffic(ue, severity)
        elif ue.ServiceType.lower() == 'data':
            traffic_data = self.generate_data_traffic(ue, severity)
        else:
            raise ValueError(f"Unknown service type: {ue.ServiceType}")
        
        traffic_data['data_size'] = int(traffic_data['data_size'] * ue.traffic_factor)
        
        # Update UE class attributes directly after generating traffic data
        ue.ue_delay = traffic_data['ue_delay']
        ue.ue_jitter = traffic_data['ue_jitter']
        ue.ue_packet_loss_rate = traffic_data['ue_packet_loss_rate']

        # Get instance of DatabaseManager
        db_manager = DatabaseManager.get_instance()

        # Prepare data for InfluxDB
        influxdb_data = {
            "measurement": "ue_metrics",
            "tags": {
                "ue_id": ue.ID,
                "service_type": ue.ServiceType,
            },
            "fields": {
                "ue_jitter": float(ue.ue_jitter),
                "ue_packet_loss_rate": float(ue.ue_packet_loss_rate),
                "ue_delay": float(ue.ue_delay),
            },
            "time": datetime.utcnow().isoformat(),
        }

        # Write to InfluxDB
        db_manager.insert_data(
            measurement_or_point=influxdb_data["measurement"],
            tags=influxdb_data["tags"],
            fields=influxdb_data["fields"],
            timestamp=influxdb_data["time"]
        )

        return traffic_data
##############################################################################################################################
    def generate_voice_traffic(self, ue, severity='zero'):
        severity_settings = self.SEVERITY_LEVELS.get(severity, self.SEVERITY_LEVELS['zero'])
        # Adjust parameters based on severity
        start_time = datetime.now()
        delay = random.uniform(*severity_settings['delay'])
        time.sleep(delay)  # Use severity-specific delay

        # Ensure jitter is an integer before comparison
        jitter_setting = severity_settings['jitter']
        jitter_max = jitter_setting if isinstance(jitter_setting, int) else jitter_setting[1]  # Use the second value if it's a tuple
        jitter = random.uniform(0, jitter_max) if jitter_max > 0 else 0

        bitrate = random.uniform(*self.voice_traffic_params['bitrate']) * severity_settings['multiplier']
        interval = 0.02  # Interval duration in seconds
        data_size = int((bitrate * interval) / 8 * 1024)

        # Apply UE's traffic_factor to scale the data size (use for dynamic increase or decrease of the ue traffic)
        scaled_data_size = int(data_size * ue.traffic_factor)  # Scaling the data size according to the UE's traffic factor     

        time.sleep(jitter)
        packet_loss_occurred = random.random() < severity_settings['packet_loss_rate']

        if packet_loss_occurred:
            data_size = 0  # Packet is lost
        end_time = datetime.now()
        traffic_data = {
            'data_size': scaled_data_size,
            'start_timestamp': start_time,
            'end_timestamp': end_time,
            'interval': interval,
            'ue_delay': delay,
            'ue_jitter': jitter,
            'ue_packet_loss_rate': severity_settings['packet_loss_rate']
        }
        self.traffic_logs.append(traffic_data)
        return traffic_data
###################################################################################################################
    def generate_video_traffic(self,ue, severity='zero'):
        severity_settings = self.SEVERITY_LEVELS.get(severity, self.SEVERITY_LEVELS['zero'])
        # Adjust parameters based on severity
        start_time = datetime.now()
        delay = random.uniform(*severity_settings['delay'])
        time.sleep(delay)  # Use severity-specific delay

        # Ensure jitter is an integer before comparison
        jitter_setting = severity_settings['jitter']
        jitter_max = jitter_setting if isinstance(jitter_setting, int) else jitter_setting[1]  # Use the second value if it's a tuple
        jitter = random.uniform(0, jitter_max) if jitter_max > 0 else 0
        time.sleep(jitter)  # Apply jitter

        # Adjust the number of streams and bitrate based on severity
        num_streams = random.randint(*self.video_traffic_params['num_streams']) * severity_settings['multiplier']
        data_size = 0  # Initialize data_size as 0 bytes
        interval = 1  # Interval duration in seconds
        # Apply UE's traffic_factor to scale the data size (use for dynamic increase or decrease of the ue traffic)
        scaled_data_size = int(data_size * ue.traffic_factor)  # Scaling the data size according to the UE's traffic factor
        
        for _ in range(num_streams):
            stream_bitrate = random.uniform(*self.video_traffic_params['stream_bitrate']) * severity_settings['multiplier']  # Adjust bitrate based on severity
            if random.random() < severity_settings['packet_loss_rate']:
                continue  # Skip this stream due to packet loss based on severity
            # Convert to MB, then to bytes, and accumulate
            scaled_data_size += int((stream_bitrate * interval) / 8 * 1024 * 1024)

        # Record the end timestamp
        end_time = datetime.now()
        traffic_data = {
            'data_size': scaled_data_size,  # Now in bytes and ensured to be an integer
            'start_timestamp': start_time,
            'end_timestamp': end_time,
            'num_streams': num_streams,
            'interval': interval,
            'ue_delay': delay,
            'ue_jitter': jitter,
            'ue_packet_loss_rate': severity_settings['packet_loss_rate']
        }
        self.traffic_logs.append(traffic_data)
        return traffic_data
###################################################################################################################
    def generate_gaming_traffic(self, ue, severity='zero'):
        severity_settings = self.SEVERITY_LEVELS.get(severity, self.SEVERITY_LEVELS['zero'])

        try:
            # Record the start timestamp
            start_time = datetime.now()
            # Adjust delay based on severity
            delay = random.uniform(*severity_settings['delay'])
            time.sleep(delay)  # Use gaming-specific delay adjusted for severity

            # Ensure jitter is an integer before comparison
            jitter_setting = severity_settings['jitter']
            jitter_max = jitter_setting if isinstance(jitter_setting, int) else jitter_setting[1]  # Use the second value if it's a tuple
            jitter = random.uniform(0, jitter_max) if jitter_max > 0 else 0

            # Adjust bitrate based on severity
            bitrate = random.uniform(*self.gaming_traffic_params['bitrate']) * severity_settings['multiplier']  # Adjust bitrate for severity
            interval = 0.1  # Interval duration in seconds

            # Convert to KB, then to bytes, and ensure it's an integer
            data_size = int((bitrate * interval) / 8 * 1024)  
            
            # Apply UE's traffic_factor to scale the data size (use for dynamic increase or decrease of the ue traffic)
            scaled_data_size = int(data_size * ue.traffic_factor)  # Scaling the data size according to the UE's traffic factor

            # Apply jitter
            time.sleep(jitter)

            # Simulate packet loss based on severity
            packet_loss_occurred = random.random() < severity_settings['packet_loss_rate']
            if packet_loss_occurred:
                scaled_data_size = 0  # Packet is lost

            # Record the end timestamp
            end_time = datetime.now()
            traffic_data = {
                'data_size': scaled_data_size,  # Now in bytes and ensured to be an integer
                'start_timestamp': start_time,
                'end_timestamp': end_time,
                'interval': interval,
                'ue_delay': delay,
                'ue_jitter': jitter,
                'ue_packet_loss_rate': severity_settings['packet_loss_rate']
            }
            self.traffic_logs.append(traffic_data)
            return traffic_data
        except Exception as e:
            traffic_update_logger.error(f"Failed to generate gaming traffic: {e}")
            # Handle the exception by returning a default data structure with severity-adjusted parameters
            return {
                'data_size': 0,  # Ensure this is consistent even in error handling
                'start_timestamp': datetime.now(),
                'end_timestamp': datetime.now(),
                'interval': 0.1,
                'ue_delay': severity_settings['delay'][0],  # Use the lower bound of the delay range for simplicity
                'ue_jitter': 0,
                'ue_packet_loss_rate': severity_settings['packet_loss_rate']
            }
#####################################################################################
    def generate_iot_traffic(self, ue, severity='zero'):
        severity_settings = self.SEVERITY_LEVELS.get(severity, self.SEVERITY_LEVELS['zero'])

        # Record the start timestamp
        start_time = datetime.now()
        # Adjust delay based on severity
        delay = random.uniform(*severity_settings['delay'])
        time.sleep(delay)  # Use IoT-specific delay adjusted for severity

        # Ensure jitter is an integer before comparison
        jitter_setting = severity_settings['jitter']
        jitter_max = jitter_setting if isinstance(jitter_setting, int) else jitter_setting[1]  # Use the second value if it's a tuple
        jitter = random.uniform(0, jitter_max) if jitter_max > 0 else 0

        # Adjust packet size and interval based on severity
        packet_size = random.randint(*self.iot_traffic_params['packet_size']) * severity_settings['multiplier']  # Adjust packet size for severity
        interval = random.uniform(*self.iot_traffic_params['interval']) * severity_settings['multiplier']  # Adjust interval for severity
        # Convert packet_size from KB to bytes, and ensure it's an integer
        data_size = int(packet_size * 1024)  

        # Apply UE's traffic_factor to scale the data size (use for dynamic increase or decrease of the ue traffic)
        scaled_data_size = int(data_size * ue.traffic_factor)  # Scaling the data size according to the UE's traffic factor

        # Apply jitter
        time.sleep(jitter)

        # Simulate packet loss based on severity
        if random.random() < severity_settings['packet_loss_rate']:
            scaled_data_size = 0  # Packet is lost

        # Record the end timestamp
        end_time = datetime.now()
        traffic_data = {
            'data_size': scaled_data_size,  # Now in bytes and ensured to be an integer
            'start_timestamp': start_time,
            'end_timestamp': end_time,
            'interval': interval,
            'ue_delay': delay,
            'ue_jitter': jitter,
            'ue_packet_loss_rate': severity_settings['packet_loss_rate']
        }
        self.traffic_logs.append(traffic_data)
        return traffic_data
###########################################################################################
    def generate_data_traffic(self, ue, severity='zero'):
        severity_settings = self.SEVERITY_LEVELS.get(severity, self.SEVERITY_LEVELS['zero'])

        # Record the start timestamp
        start_time = datetime.now()
        # Adjust delay based on severity
        delay = random.uniform(*severity_settings['delay'])
        time.sleep(delay)  # Use data-specific delay adjusted for severity

        # Ensure jitter is an integer before comparison
        jitter_setting = severity_settings['jitter']
        jitter_max = jitter_setting if isinstance(jitter_setting, int) else jitter_setting[1]  # Use the second value if it's a tuple
        jitter = random.uniform(0, jitter_max) if jitter_max > 0 else 0

        # Adjust bitrate and interval based on severity
        bitrate = random.uniform(*self.data_traffic_params['bitrate']) * severity_settings['multiplier']  # Adjust bitrate for severity
        interval = random.uniform(*self.data_traffic_params['interval']) * severity_settings['multiplier']  # Adjust interval for severity
        # Convert bitrate from Mbps to bytes, then calculate data_size for the interval, and ensure it's an integer
        data_size = int((bitrate * interval) / 8 * 1024 * 1024)

        # Apply UE's traffic_factor to scale the data size (use for dynamic increase or decrease of the ue traffic)
        scaled_data_size = int(data_size * ue.traffic_factor)  # Scaling the data size according to the UE's traffic factor

        # Apply jitter
        time.sleep(jitter)

        # Simulate packet loss based on severity
        if random.random() < severity_settings['packet_loss_rate']:
            scaled_data_size = 0  # Packet is lost

        # Record the end timestamp
        end_time = datetime.now()
        traffic_data = {
            'data_size': scaled_data_size,  # Now in bytes and ensured to be an integer
            'start_timestamp': start_time,
            'end_timestamp': end_time,
            'interval': interval,
            'ue_delay': delay,
            'ue_jitter': jitter,
            'ue_packet_loss_rate': severity_settings['packet_loss_rate']
        }
        self.traffic_logs.append(traffic_data)
        return traffic_data
############################################################################################
    def get_all_traffic_data(self):
            """Retrieve current traffic data for all UEs."""
            all_traffic_data = []
            for ue_id, ue in self.ues.items():
                # Assuming generate_traffic returns the latest traffic data for a UE
                traffic_data = self.generate_traffic(ue)
                all_traffic_data.append(traffic_data)
            return all_traffic_data
############################################################################################
    def add_ue(self, ue):
        if ue.ID not in self.ues:
            self.ues[ue.ID] = ue
            print(f"UE {ue.ID} added.")  # Example print message for debugging

    def remove_ue(self, ue_id):
        if ue_id in self.ues:
            del self.ues[ue_id]
            print(f"UE {ue_id} removed.")  # Example print message for debugging
############################################################################################
    def start_ue_traffic(self, ue_or_id):
        # Check if the input is an UE ID instead of an object and retrieve the UE object
        if isinstance(ue_or_id, int):
            ue = self.ues.get(ue_or_id)
            if not ue:
                print(f"UE with ID {ue_or_id} not found.")
                return
        else:
            ue = ue_or_id

        # Check if traffic is already running for this UE
        if ue.generating_traffic:
            traffic_update_logger(f"Traffic already on for UE {ue.ID}")
            return

        # If not generating traffic, start traffic generation
        with self._lock:  # Ensure thread-safe access to ue.generating_traffic
            ue.generating_traffic = True

        try:
            # Additional setup for starting traffic (if needed)
            # ...
            print(f"Traffic generation started for UE {ue.ID}")
        except Exception as e:
            traffic_update_logger.error(f"Failed to start traffic for UE {ue.ID}: {e}")

############################################################################################
    def stop_ue_traffic(self, ue):
        """Stops traffic generation for the given UE"""
        if ue.ID in self.ues and ue.generating_traffic:
            with self._lock:  # Ensure thread-safe access to ue.generating_traffic
                ue.generating_traffic = False
                ue.throughput = 0

            try:
                # Additional cleanup (if needed)
                # For example, you might need to:
                # - Stop any threads or processes related to traffic generation for this UE.
                # - Close any open sockets or connections.
                # - Release any resources associated with the UE's traffic.
                pass  # Replace this with your actual cleanup logic
            except Exception as e:
                traffic_update_logger.error(f"Error during cleanup for UE {ue.ID}: {e}")
                # Handle the error (e.g., log the error and continue)

            traffic_update_logger.info(f"Traffic stopped for {ue.ID}")
            self.remove_ue(ue.ID)

#########################################################################################################################
    # Note:Throughput measures the rate at which data is successfully transmitted over the network,typically expressed  #
    # in bits per second (bps). It's crucial for evaluating network performance, especially in scenarios where the      #
    # speed of data transmission is critical, such as streaming or real-time applications. Data Volume (Traffic Volume) #
    # on the other hand, refers to the total amount of data [sent or received ] by a UE over a certain period,          #
    # often measured in bytes or multiples thereof (e.g., MB, GB).                                                      #
    # This metric is vital for assessing network load, data consumption patterns, and for planning network capacity.    #
#########################################################################################################################
    def set_custom_traffic(self, ue_id, traffic_factor):
        # Assuming self.ue_manager is an instance of UEManager
        ue = self.ue_manager.get_ue_by_id(ue_id)
        if not ue:
            print(f"UE with ID {ue_id} not found.")
            return

        # Apply the custom traffic parameters
        ue.traffic_factor = traffic_factor
        print(f"Set custom traffic factor for UE {ue_id}: {traffic_factor}")
############################################################################################
    def find_ue_by_id(self, ue_id):
        """
        Finds a UE by its ID.

        :param ue_id: The ID of the UE to find.
        :return: The UE instance with the matching ID, or None if not found.
        """
        # Assuming self.ues is a dictionary or list of UE instances
        for ue in self.ues:
            if ue.ue_id == ue_id:
                return ue
        return None
############################################################################################
    def calculate_throughput(self, ue):
        # Parameter validation
        if not isinstance(ue, UE):
            raise TypeError("Invalid UE object")

        # Generate traffic and retrieve traffic parameters for the UE
        traffic_data = self.generate_traffic(ue)

        # Assertions to fail fast if assumptions are violated
        assert isinstance(traffic_data['data_size'], int), "Invalid data type for data_size"
        assert traffic_data['interval'] >= 0, "Negative interval is not allowed"

        # Retrieve jitter, packet loss, and delay from the traffic data
        jitter = traffic_data['ue_jitter']  # Adjusted to use 'ue_jitter'
        packet_loss_rate = traffic_data['ue_packet_loss_rate']  # Adjusted to use 'ue_packet_loss_rate'
        interval = traffic_data['interval']
        ue_delay = traffic_data['ue_delay']
        
        # data_size is expected to be in bytes (as an integer)
        scaled_data_size_bytes  = traffic_data['data_size']
        data_size_bits = scaled_data_size_bytes  * 8  # Convert bytes to bits

        # Calculate throughput
        throughput = data_size_bits / interval if interval > 0 else 0
        # Update the UE's throughput attribute with the calculated value
        throughput = float(throughput) # Before preparing influxdb_data, ensure throughput is a float
        
        ue.throughput = throughput

        #print(f"UE {ue.ID} throughput: {throughput} bits/s")
        # Prepare the data for InfluxDB with units for clarity
        influxdb_data = {
            "measurement": "ue_metrics",
            "tags": {
                "ue_id": ue.ID,
                "service_type": ue.ServiceType,
            },
            "fields": {
                "throughput": throughput, 
            },
            "time": datetime.utcnow().isoformat(),
        }
        #print('******traffic Gen******influxdb_data:', influxdb_data)
        # Assuming DatabaseManager and other necessary imports are correctly handled
        database_manager = DatabaseManager()
        # If preparing a data dictionary for insertion
        influxdb_data['fields']['throughput'] = int(influxdb_data['fields']['throughput'])

        database_manager.insert_data(
            measurement_or_point=influxdb_data["measurement"],
            tags=influxdb_data["tags"],
            fields=influxdb_data["fields"],
            timestamp=influxdb_data["time"]
        )
        #print('--------------------------ue.ID-----------------------------------:',ue.ID)
        ue_ID = ue.ID
        database_manager.get_ue_metrics(ue_ID)
        database_manager.close_connection()

        # Return the raw numeric value of throughput along with other metrics
        return {
            'throughput': throughput,
            'ue_jitter': jitter,  
            'ue_packet_loss_rate': packet_loss_rate,  
            "ue_delay": ue_delay,  
            'interval': interval
        }
############################################################################################
