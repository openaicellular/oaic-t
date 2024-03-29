################################################################################################################################
# Defines the Cell class, which is part of a gNodeB and located inside network directory. The Cell class represents a cell     #
# in a cellular network, which is a part of a gNodeB. Cells are the basic units of a cellular network that provide radio       #
# coverage to geographical areas and manage radio communications with User Equipments (UEs) within those areas. This class is  #
# designed to simulate the behavior and characteristics of real-world network cells, including managing connections to UEs,    #
# handling cell-specific configurations, and reporting metrics for network simulation and analysis. This class plays a crucial #
# role in the network simulation by managing the radio resources assigned to each cell, tracking the UEs connected to each cell#
# and simulating cell-specific behaviors such as load balancing and handovers.                                                 #
################################################################################################################################
from logs.logger_config import cell_logger, ue_logger, cell_logger, database_logger
import datetime
import time 
import uuid
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS
from database.time_utils import get_current_time_ntp, server_pools
from influxdb_client.client.write_api import WritePrecision
from datetime import datetime
cell_instances = {}

class Cell:
    def __init__(self, cell_id, gnodeb_id, frequencyBand, duplexMode, tx_power, bandwidth, ssbPeriodicity, ssbOffset, maxConnectUes, max_throughput,  channelModel, sectorCount, trackingArea=None, is_active=True, technology="5GNR"):
        #debug_print(f"START-Creating cell {cell_id} from cell class")
        self.ID = cell_id                     # Unique identifier for the Cell
        self.instance_id = str(uuid.uuid4())  # Generic unique identifier for the instance  of the cell 
        cell_instances[cell_id] = self       # global registry   
        self.gNodeB_ID = gnodeb_id          # Identifier for the associated gNodeB of this cell
        self.FrequencyBand = frequencyBand  # Frequency band in which the cell operates
        self.DuplexMode = duplexMode        # Duplex mode of the cell (e.g., FDD, TDD)
        self.TxPower = tx_power             # Transmission power of the cell in Watts
        self.Bandwidth = bandwidth          # Bandwidth allocated to the cell in MHz
        self.SSBPeriodicity = ssbPeriodicity# Periodicity of the SSB (Synchronization Signal Block) in ms    
        self.SSBOffset = ssbOffset          # Offset for the SSB in terms of the number of symbols     
        self.maxConnectUes = maxConnectUes  # Maximum number of UEs that can connect to the cell, total UEs a cell can handle
        self.max_throughput = max_throughput# Maximum throughput the cell can handle in Mbps
        self.ChannelModel = channelModel     # Channel model used for the cell (e.g., urban, rural)
        self.TrackingArea = trackingArea     # Tracking area code, if applicable
        self.ConnectedUEs = []              # List of UEs currently connected to the cell
        self.assigned_UEs = []              # Initialize the list of assigned UEs
        self.last_ue_update = None          # Timestamp of the last update to the UE list
        self.last_update = None             # Timestamp of the last update to any cell attribute
        self.IsActive = is_active           # Indicates whether the cell is active or not
        self.current_ue_count = int(0)           # Current count of UEs connected to the cell
        self.sectors = []                   # List of sectors associated with the cell
        self.SectorCount = sectorCount      # Number of sectors the cell is divided into
        self.gNodeB = None                  # Initialize with None
        self.Technology = technology
        self.cell_load = float(0)           # this is cell load for each cell and shoudl be float!
        current_time = get_current_time_ntp()
        # Logging statement should be here, after all attributes are set
        cell_logger.info(f" A Cell '{cell_id}' has been created at '{current_time}' in gNodeB '{gnodeb_id}' with max capacity {self.maxConnectUes} ue.")
        time.sleep(1)
    @staticmethod
    def from_json(json_data):
        return Cell(
            cell_id=json_data["cell_id"],
            gnodeb_id=json_data["gnodeb_id"],
            frequencyBand=json_data["frequencyBand"],
            duplexMode=json_data["duplexMode"],
            tx_power=json_data["tx_power"],
            bandwidth=json_data["bandwidth"],
            ssb_periodicity=json_data["ssbPeriodicity"],
            ssb_offset=json_data["ssbOffset"],
            max_connect_ues=json_data["maxConnectUes"],
            channel_model=json_data["channelModel"],
            trackingArea=json_data.get("trackingArea"),
            is_active=json_data.get("is_active", True),
            max_throughput=json_data["max_throughput"],

        )
    def to_dict(self):
        return {
            'ID': self.ID,
            'gNodeB_ID': self.gNodeB_ID,
            'FrequencyBand': self.FrequencyBand,
            'DuplexMode': self.DuplexMode,
            'TxPower': self.TxPower,
            'Bandwidth': self.Bandwidth,
            'SSBPeriodicity': self.SSBPeriodicity,
            'SSBOffset': self.SSBOffset,
            'MaxConnectedUEs': self.MaxConnectedUEs,
            'max_throughput': self.max_throughput,
            'ChannelModel': self.ChannelModel,
            'TrackingArea': self.TrackingArea,
            'CellisActive': self.IsActive,
            'is_active': self.IsActive,


        }
####################################################################################### 
    def serialize_for_influxdb(self, cell_load):
        try:
            # Convert current UTC time to a UNIX timestamp in seconds
            unix_timestamp_seconds = int(datetime.utcnow().timestamp())
    
            point = Point("cell_metrics") \
                .tag("cell_id", str(self.ID)) \
                .tag("gnodeb_id", str(self.gNodeB_ID)) \
                .tag("entity_type", "cell") \
                .tag("instance_id", str(self.instance_id)) \
                .field("frequencyBand", str(self.FrequencyBand)) \
                .field("duplexMode", str(self.DuplexMode)) \
                .field("tx_power", int(self.TxPower)) \
                .field("bandwidth", int(self.Bandwidth)) \
                .field("ssb_periodicity", int(self.SSBPeriodicity)) \
                .field("ssb_offset", int(self.SSBOffset)) \
                .field("max_connect_ues", int(self.maxConnectUes)) \
                .field("max_throughput", int(self.max_throughput)) \
                .field("channel_model", str(self.ChannelModel)) \
                .field("trackingArea", str(self.TrackingArea)) \
                .field("CellisActive", bool(self.IsActive)) \
                .field("sector_count", int(self.SectorCount)) \
                .field("is_active", bool(self.IsActive)) \
                .field("cell_load", self.cell_load)\
                .time(unix_timestamp_seconds, WritePrecision.S)  # Set the timestamp in seconds
    
            return point
        except Exception as e:
            database_logger.error(f"Error serializing cell data for InfluxDB: {e}")
            # Depending on your error handling policy, you might want to re-raise the exception or return None
            raise

####################################################################################
    def add_sector_to_cell(self, sector):
    # Directly work with the self instance, no need to find by cell_id
        if not hasattr(self, 'sectors'):
            self.sectors = []

    # Check if sector already exists in the cell
        if sector.sector_id not in [s.sector_id for s in self.sectors]:
            self.sectors.append(sector)
            cell_logger.info(f"Sector '{sector.sector_id}' added to Cell '{self.ID}'.")
        else:
        # Log duplicate sector
            cell_logger.warning(f"Sector {sector.sector_id} already exists in Cell {self.ID}.")
#########################################################################################
    def add_ue(self, ue):
        if len(self.ConnectedUEs) < self.maxConnectUes:
            # Check if the UE already exists
            if ue.ID not in self.ConnectedUEs:
                self.ConnectedUEs.append(ue.ID)
                self.current_ue_count += 1
                # Log the addition of the UE
                ue_logger.info(f"UE with ID {ue.ID} has been added to Cell {self.ID}")
            else:
                # Log or handle the case where the UE already exists
                ue_logger.warning(f"UE with ID {ue.ID} already exists in Cell {self.ID}")
        else:
            # Handle the case where the cell is at capacity
            ue_logger.warning(f"Cell {self.ID} is at maximum capacity. Cannot add UE with ID {ue.ID}")
            
    def set_gNodeB(self, gNodeB):
        self.gNodeB = gNodeB
        
    def has_sector(self, sector_id):
        return any(sector.ID == sector_id for sector in self.sectors)
    
    def get_sector(self, sector_id):
        """
        Retrieve a sector by its sector_id from the sectors associated with this cell.

        :param sector_id: The sector_id of the sector to retrieve.
        :return: The sector with the matching sector_id, or None if no match is found.
        """
        for sector in self.sectors:
            if sector.sector_id == sector_id:  # Use sector.sector_id instead of sector.ID
                return sector
        return None  # Or, alternatively, raise an exception if the sector is not found.
    
    def update_ue_lists(self):
        # Reset the lists to ensure they only contain current UEs
        self.ConnectedUEs = []
        self.assigned_UEs = []
        # Aggregate UE information from all sectors
        for sector in self.sectors:  # Assuming self.sectors is a list of Sector objects
            self.ConnectedUEs.extend(sector.connected_ues)  # Assuming sector.connected_ues is a list of UE IDs
            self.assigned_UEs.extend(sector.connected_ues)  # Similarly for assigned UEs
        # Optionally, remove duplicates if any UE is connected or assigned to multiple sectors
        self.ConnectedUEs = list(set(self.ConnectedUEs))
        self.assigned_UEs = list(set(self.assigned_UEs))
    
        # Update the IsActive attribute based on the presence of connected UEs
        self.IsActive = len(self.ConnectedUEs) > 0