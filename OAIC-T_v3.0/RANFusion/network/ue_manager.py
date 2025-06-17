##############################################################################################################
# this is ue_manager.py inside the network folder to manage all UE.The UEManager class is responsible for    #
# managing User Equipment (UE) instances within the network simulation. It provides functionalities to       #
# create, update, delete, and manage UEs across the network. This class follows the Singleton design pattern #
# to ensure that only one instance of the UEManager exists throughout the application lifecycle.             #
##############################################################################################################

import os
from network.ue import UE
from network.utils import allocate_ues, create_ue
from Config_files.config import Config
from logs.logger_config import ue_logger
from network.sector_manager import SectorManager
from network.sector import global_ue_ids  # Ensure this import is correct
import threading
# Get base path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = Config(base_dir)
ue_config = config.ue_config

class UEManager:
    _instance = None
    _lock = threading.Lock()
    _call_count = 0  # Add a class variable to count calls of this isntance

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(UEManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, base_dir):
        if not hasattr(self, 'initialized'):  # This ensures __init__ is only called once
            self.config = Config(base_dir)
            self.base_dir = base_dir
            self.config_path = os.path.join(self.base_dir, 'Config_files', 'gNodeB_config.json')
            self.ue_config = self.config.ue_config
            self.ues = {}  # Ensure this is a dictionary
            self.initialized = True

    @classmethod
    def get_instance(cls, base_dir):
        cls._call_count += 1
        ue_logger.debug(f"UEManager get_instance called {cls._call_count} times.")
        with cls._lock:
            if not cls._instance:
                ue_logger.debug("Creating a new instance of UEManager.")
                cls._instance = UEManager(base_dir)
            elif base_dir and not hasattr(cls._instance, 'base_dir'):
                ue_logger.debug("Initializing existing instance of UEManager with new base_dir.")
                cls._instance.initialize(base_dir)
            else:
                ue_logger.debug("Returning existing instance of UEManager.")
            ue_logger.debug(f"UEManager instance: {cls._instance}")
        return cls._instance

    def initialize(self, base_dir=None):
        if base_dir and not hasattr(self, 'base_dir'):
            self.base_dir = base_dir
            self.config = Config(base_dir)
            self.ue_config = self.config.ue_config

    def initialize_ues(self, num_ues_to_launch, cells, gNodeBs, ue_config):
        """Initialize UEs and allocate them to sectors."""
        all_sectors = []
        for cell in cells.values():
            all_sectors.extend(cell.sectors)

        if not all_sectors:
            print("Error: No sectors found")
            return []

        ue_instances = allocate_ues(num_ues_to_launch, all_sectors, self.ue_config)

        # Debug logging or print statements
        print(f"Number of UE instances created: {len(ue_instances)}")
        # Convert list of UE instances to a dictionary with UE ID as keys
        self.ues = {ue.ID: ue for ue in ue_instances}

        # Debug logging or print statements
        print(f"UE instances added to ues dictionary:")
        for ue_id, ue in self.ues.items():
            ue_logger.info(f"Added UE instance with ID: {ue.instance_id} to UEManager")
            print(f"UE ID: {ue_id}, Connected Cell: {ue.ConnectedCellID}, ...")
            ue_logger.info(f"Added UE instance with ID: {ue.instance_id} to UEManager")
        ue_logger.info(f"Contents of ues dictionary after initialization: {self.ues}")

        return list(self.ues.values())  # Return a list of UE objects

    def create_ue(self, config, **kwargs):
        # Logic to create a single UE instance
        with UEManager._lock:  # Acquire the global lock
            new_ue = UE(config, **kwargs)
            self.ues[new_ue.ID] = new_ue
            global_ue_ids.add(new_ue.ID)  # Add the new UE ID to the global set

            # Log the addition and current state of the ues dictionary
            ue_logger.info(f"UE with ID {new_ue.ID} created and added to ues dictionary.")
            ue_logger.info(f"Current contents of ues dictionary: {self.ues}")

        return new_ue

    def get_ue_by_id(self, ue_id):
        ue_id_str = str(ue_id).strip().lower()  # Normalize ue_id to lowercase
        ue_logger.debug(f"Looking for UE with ID: {ue_id_str}")
        ue_logger.debug(f"Contents of ues dictionary: {self.ues}")
        
        # Try to get the UE from the ues dictionary
        ue = self.ues.get(ue_id_str)
        
        if ue is None:
            # If not found, try to get the UE using the static method from UE class
            ue = UE.get_ue_instance_by_id(ue_id_str)
        
        if ue is None:
            ue_logger.error(f"UE with ID {ue_id_str} not found.")
        else:
            ue_logger.info(f"Found UE instance: {ue}")
            ue_logger.debug(f"UE instance ID: {id(ue)}")  # Log the object ID
            
            # Ensure the UE is in the ues dictionary
            if ue_id_str not in self.ues:
                self.ues[ue_id_str] = ue
                ue_logger.info(f"Added UE {ue_id_str} to ues dictionary.")
        
        return ue


    def update_ue(self, ue_id, **kwargs):
        """
        Update the parameters of an existing UE.
        
        :param ue_id: The ID of the UE to update.
        :param kwargs: Parameters to update.
        :return: True if the update was successful, False otherwise.
        """
        ue = self.get_ue_by_id(ue_id)
        print(f"UE instance found for ID {ue_id}: {ue}")
        if ue:
            ue.update_parameters(**kwargs)
            ue_logger.info(f"UE {ue_id} updated successfully with parameters {kwargs}.")
            return True
        else:
            print(f"UE {ue_id} not found")
            ue_logger.info(f"Attempted to update UE {ue_id}, but it was not found.")
            return False

    def list_all_ues(self):
        # Now this will correctly return a list of UE IDs
        ue_logger.debug(f"Listing all UEs: {self.ues.keys()}")
        return list(self.ues.keys())

    def delete_ue(self, ue_id):
        # Retrieve the UE instance
        with UEManager._lock:  # Acquire the global lock
            ue = self.get_ue_by_id(ue_id)
            if ue is None:
                print(f"UE with ID {ue_id} not found.")
                ue_logger.info(f"Attempted to delete UE {ue_id}, but it was not found.")
                return False

        # Assuming you have a way to access the SectorManager instance
        sector_manager = SectorManager.get_instance()

        # Remove the UE from its connected sector
        sector_id = ue.ConnectedSector  # Use the correct attribute here
        if sector_manager.remove_ue_from_sector(sector_id, ue_id):
            print(f"UE {ue_id} successfully removed from sector {sector_id}.")
            global_ue_ids.discard(ue_id)  # Correctly modify global_ue_ids
            # Now, delete the UE instance from UEManager's ues dictionary
            del self.ues[ue_id]
            ue_logger.debug(f"UE {ue_id} successfully deleted from ues dictionary.")
            ue_logger.debug(f"Current contents of ues dictionary: {self.ues}")
            return True
        else:
            print(f"Failed to remove UE {ue_id} from sector {sector_id}.")
            return False

    def stop_ue_traffic(self, ue_id):
        from traffic.traffic_generator import TrafficController
        """Stop traffic generation for the given UE"""
        ue = self.get_ue_by_id(ue_id)
        
        if not ue:
            ue_logger.info(f"Attempted to stop traffic for UE {ue_id}, but it was not found.")
            print(f"UE {ue_id} not found")
            return
        # Get reference to traffic generator 
        traffic_controller = TrafficController.get_instance()
        if ue.generating_traffic:
            traffic_controller.stop_ue_traffic(ue)
            ue.generating_traffic = False
            ue.throughput = 0.0
            ue_logger.info(f"Traffic stopped for UE {ue_id}.")
            print(f"Traffic stopped for UE {ue_id}")
        else:
            print(f"UE {ue_id} does not have active traffic generation")