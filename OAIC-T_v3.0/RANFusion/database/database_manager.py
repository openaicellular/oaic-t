#########################################################################################################
# This is database manager class "database_manager.py" located in datbase folderThe DatabaseManager     #
# class is responsible for managing all interactions with the InfluxDB database. It provides methods    #
# for inserting, querying, and deleting data related to the network simulation, including metrics for   #
# sectors, cells, UEs (User Equipments), and network performance. This class implements the Singleton   #
# design pattern to ensure that only one instance of the database connection is created and used        #
# throughout the application.                                                                           #
#########################################################################################################
import os
from influxdb_client import InfluxDBClient, WritePrecision, Point, QueryApi
from influxdb_client.client.delete_api import DeleteApi
from influxdb_client.client.write_api import SYNCHRONOUS
from logs.logger_config import database_logger  # Import the configured logger
from datetime import datetime
import json
import threading

# Read from environment variables or use default values
INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN')
if not INFLUXDB_TOKEN:
    raise ValueError("INFLUXDB_TOKEN environment variable is not set.")
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'ranfusion')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'RAN_metrics')

class DatabaseManager:
    _instance = None
    _lock = threading.Lock()  # Add a class-level lock
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseManager, cls).__new__(cls)
                    cls._instance.client_init()
        return cls._instance

    def client_init(self):
        self.client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
        self.bucket = INFLUXDB_BUCKET
        self.org = INFLUXDB_ORG

    @classmethod
    def get_instance(cls):
        return cls()
    

    #@classmethod
    #def get_instance(cls):
        #if cls._instance is None:
            #with cls._lock:
                #if cls._instance is None:
                #  cls._instance = super(DatabaseManager, cls).__new__(cls)
                # cls._instance.client_init()
        #return cls._instance

    def get_sector_by_id(self, sector_id):
        query = f'from(bucket: "{self.bucket}") |> range(start: -1d) |> filter(fn: (r) => r._measurement == "sector_metrics" and r.sector_id == "{sector_id}")'
        result = self.query_api.query(query=query)
        for table in result:
            for record in table.records:
                if record.values.get('sector_id') == sector_id:
                    return record.values  # Adjust based on what you need
        return None

    def insert_sector_state(self, sector):
        """Inserts the state of a sector into InfluxDB."""
        point = sector.serialize_for_influxdb()  # Assuming serialize_for_influxdb() prepares the data correctly
        self.insert_data(point)

    def get_sectors(self):
        try:
            query = f'from(bucket:"{self.bucket}") |> range(start: -30d) |> filter(fn:(r) => r._measurement == "sectors")'
            result = self.query_api.query(query=query)
            sectors = []
            for table in result:
                for record in table.records:
                    sector_data = json.loads(record.get_value())
                    sectors.append(sector_data)
            return sectors
        except Exception as e:
            print(f"Failed to retrieve sectors: {e}")
            return []

    def remove_ue_state(self, ue_id, sector_id):
        """
        Removes the state of a UE from InfluxDB within the last 24 hours.
        
        :param ue_id: The ID of the UE to remove.
        :param sector_id: The ID of the sector associated with the UE.
        """
        # Define the time range for deletion. Here, we use 24 hours as an example.
        start_time = "now() - 24h"
        stop_time = "now()"
        
        # Construct the delete predicate function
        predicate = f'_measurement="ue_metrics" AND ue_id="{ue_id}" AND sector_id="{sector_id}"'
        
        try:
            # Perform the deletion
            self.client.delete_api().delete(start_time, stop_time, predicate, bucket=self.bucket, org=INFLUXDB_ORG)
            database_logger.info(f"Successfully removed state for UE {ue_id} in sector {sector_id}.")
        except Exception as e:
            database_logger.error(f"Failed to remove state for UE {ue_id} in sector {sector_id}: {e}")

    def test_connection(self):
        """Test if the connection to the database is successful."""
        try:
            self.client.ping()
            database_logger.info("Database connection successful.")
            return True
        except Exception as e:
            database_logger.error(f"Database connection test failed: {e}")
            return False

    def insert_data_batch(self, points):
        """Inserts a batch of Point objects into InfluxDB."""
        try:
            self.write_api.write(bucket=self.bucket, record=points)
        except Exception as e:
            database_logger.error(f"Failed to insert batch data into InfluxDB: {e}")

    def insert_data(self, measurement_or_point, tags=None, fields=None, timestamp=None):
        """Inserts or updates data into InfluxDB. Can handle both Point objects and separate parameters."""
        try:
            if isinstance(measurement_or_point, Point):
                point = measurement_or_point
                if 'throughput' in point._fields:
                    point._fields['throughput'] = float(point._fields['throughput'])
            else:
                measurement = measurement_or_point
                point = Point(measurement)
                if fields and 'throughput' in fields:
                    fields['throughput'] = float(fields['throughput'])
                for tag_key, tag_value in (tags or {}).items():
                    point.tag(tag_key, tag_value)
                for field_key, field_value in (fields or {}).items():
                    point.field(field_key, field_value)
                if timestamp is None:
                    timestamp = datetime.utcnow()
                point.time(timestamp, WritePrecision.S)
            self.write_api.write(bucket=self.bucket, record=point)
        except Exception as e:
            print(f"Failed to insert data into InfluxDB: {e}")

    def close_connection(self):
        """Closes the database connection."""
        try:
            self.client.close()
        except Exception as e:
            print(f"Failed to close database connection: {e}")

    def get_all_ue_ids(self):
        """Retrieves all unique UE IDs from InfluxDB."""
        try:
            query = f'from(bucket: "{self.bucket}") |> range(start: -1d) |> filter(fn: (r) => r._measurement == "ue_metrics")'
            result = self.query_api.query(query=query, org=INFLUXDB_ORG)
            ue_ids = set()  # Use a set to ensure uniqueness
            for table in result:
                for record in table.records:
                    if 'ue_id' in record.values:
                        ue_ids.add(record.values['ue_id'])  # Add to set
            database_logger.info(f"Retrieved UE IDs: {ue_ids}")  # Log the retrieved UE IDs
        except Exception as e:
            database_logger.error(f"Failed to retrieve UE IDs from InfluxDB: {e}")
            return []  # Return an empty list in case of any exception
        return sorted(list(ue_ids))  # Convert set to sorted list

    def insert_log(self, log_point):
        """Inserts log data into the logs bucket in InfluxDB."""
        log_bucket = 'RAN_logs'
        try:
            self.write_api.write(bucket=log_bucket, record=log_point)
            database_logger.info(f"Log data inserted into bucket {log_bucket}")
        except Exception as e:
            database_logger.error(f"Failed to insert log data into InfluxDB: {e}")

    def update_ue_association(self, ue_id, new_cell_id):
        """
        Updates the association of a UE with a new cell in the database by writing a new point.
        :param ue_id: The ID of the UE to update.
        :param new_cell_id: The ID of the new cell to associate the UE with.
        """
        try:
            point = Point("ue_metrics")\
                .tag("ue_id", str(ue_id))\
                .tag("connected_cell_id", str(new_cell_id)) \
                .field("update_type", "cell_association_change")\
                .time(datetime.utcnow())
            self.write_api.write(bucket=self.bucket, record=point)
            database_logger.info(f"UE {ue_id} association updated to cell {new_cell_id}")
        except Exception as e:
            database_logger.error(f"Failed to update UE association in the database: {e}")
            raise

    def write_sector_load(self, sector_id, load):
        point = Point("sector_metrics") \
            .tag("sector_id", sector_id) \
            .field("sector_load", load) \
            .time(datetime.utcnow(), WritePrecision.S)
        self.write_api.write(bucket=self.bucket, record=point)

    def write_cell_load(self, cell_id, load):
        point = Point("cell_metrics") \
            .tag("cell_id", cell_id) \
            .field("cell_load", load) \
            .time(datetime.utcnow(), WritePrecision.S)
        self.write_api.write(bucket=self.bucket, record=point)

    def write_network_measurement(self, network_load, network_delay, total_handover_success_count, total_handover_failure_count):
        point = Point("network_metrics") \
            .field("network_load", float(network_load)) \
            .field("network_delay", float(network_delay)) \
            .field("total_handover_success_count", int(total_handover_success_count)) \
            .field("total_handover_failure_count", int(total_handover_failure_count)) \
            .time(datetime.utcnow(), WritePrecision.NS)
        self.write_api.write(bucket=self.bucket, record=point)

    def get_ue_metrics(self, ue_id):
        #print(f"Attempting to fetch UE metrics for ue_id: {ue_id}")  # Debug message 1
        query = f'''
            from(bucket: "{self.bucket}")
                |> range(start: -1d)
                |> filter(fn: (r) => r._measurement == "ue_metrics" and r.ue_id == "{ue_id}")
                |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
        result = self.query_api.query(query=query)
        #print(f'Result of the query inside the get_ue_metrics for ue_id {ue_id}:', result)  # Debug message 2
        metrics = []
        if result:
            for table in result:
                #print('--------inside for loop DB Manager----table:', table)
                for record in table.records:
                    #print(f'Record from table: {record}')  # Debug message 3
                    #print('----DB Manager-------record:', record)
                    #print('--------------throughput:', record.values.get('throughput', None))
                    #print('-------------------time:', record.get_time())
                    metrics.append({
                        'timestamp': record.get_time(),
                        'throughput': record.values.get('throughput', None),
                        'ue_jitter': record.values.get('jitter', None),
                        'ue_packet_loss_rate': record.values.get('packet_loss', None),
                        'ue_delay': record.values.get('delay', None)
                    })
        else:
            print("No results found for the query.")
        return metrics

    def get_sector_load(self, sector_id):
        query = f'''
        from(bucket: "{self.bucket}")
            |> range(start: -1d)
            |> filter(fn: (r) => r["_measurement"] == "sector" and r["sector_id"] == "{sector_id}")
            |> filter(fn: (r) => r["_field"] == "load")
        '''
        result = self.query_api.query(query=query)
        load_metrics = []
        for table in result:
            for record in table.records:
                load_metrics.append({
                    'load': record.get_value(),
                    'time': record.get_time()
                })
        return load_metrics

    def flush_all_data(self):
        from datetime import datetime, timezone
        import requests

        try:
            if not hasattr(self, 'client'):
                self.client_init()

            bucket_to_clear = self.bucket
            start = "1970-01-01T00:00:00Z"
            stop = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

            url = f"{self.client.url}/api/v2/delete?org={self.org}&bucket={bucket_to_clear}"
            headers = {
                'Authorization': f'Token {self.client.token}',
                'Content-Type': 'application/json',
            }
            data = {
                "start": start,
                "stop": stop,
            }

            response = requests.post(url, headers=headers, json=data, timeout=10)

            if response.status_code == 204:
                print(f"All data in the bucket {bucket_to_clear} has been deleted successfully.")
                return True
            else:
                print(f"Failed to delete data from bucket {bucket_to_clear}: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Request exception occurred: {e}")
            return False
        except Exception as e:
            print(f"General exception occurred: {e}")
            return False