##########################################################################################
# API.py is API Gateway of RANFusion and work with command_handler.py and also RANFUsion #
# Architecture to do some task.                                                          #
#                                                                                        #
##########################################################################################
from dotenv import load_dotenv
import os
import sys
from multiprocessing import Queue
import threading
import time

# Build the path to the .env file in the root directory of your project
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')

# Load the .env file
load_dotenv(dotenv_path)
#print(dotenv_path)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
from network.command_handler import CommandHandler
from logs.logger_config import API_logger
import traceback
from flask import Flask, request, jsonify, Response
import logging
from database.database_manager import DatabaseManager
import re
from influxdb_client import InfluxDBClient

app = Flask(__name__)

INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG')
INFLUXDB_URL = os.getenv('INFLUXDB_URL') 
client = InfluxDBClient(url=INFLUXDB_URL,token=INFLUXDB_TOKEN,org=INFLUXDB_ORG)

def check_for_shutdown_command(queue):
    """
    Periodically checks the queue for the shutdown command.
    If found, stops the Flask application.
    """
    while True:
        if not queue.empty():
            message = queue.get()
            if message == "SHUTDOWN":
                # Implement your shutdown logic here
                # For development server, you might set a global flag
                # For production with a server like Gunicorn, you would send a signal to shut down
                print("Shutdown command received. Implement shutdown logic here.")
                break
        time.sleep(1)  # Check every second

def run_api(queue):
    """
    Starts the API server and begins checking the queue for messages.
    """
    shutdown_thread = threading.Thread(target=check_for_shutdown_command, args=(queue,))
    shutdown_thread.start()
    
    # Start the Flask application
    app.run(debug=True, use_reloader=False)  # use_reloader=False is important to not spawn child processes
    
######################################################################################################################
#This is an API for delete one ue from all place!
@app.route('/del_ue', methods=['POST'])
def del_ue():
    data = request.json
    
    # Validate input data
    if 'ue_id' not in data:
        API_logger.error("Missing 'ue_id' in request data")
        return jsonify({'error': "Missing 'ue_id'"}), 400
    
    ue_id = data['ue_id']
    
    try:
        # Assuming CommandHandler.handle_command is properly implemented to handle 'del_ue' command
        # and now returns a boolean indicating success or failure
        result, message = CommandHandler.handle_command('del_ue', {'ue_id': ue_id})
        
        if result:
            API_logger.info(f"UE {ue_id} successfully removed.")
            return jsonify({'message': f'UE {ue_id} successfully removed', 'ue_id': ue_id}), 200
        else:
            API_logger.warning(f"Failed to remove UE {ue_id}: {message}")
            return jsonify({'error': f'Failed to remove UE {ue_id}', 'details': message}), 400
    except Exception as e:
        API_logger.error(f"An error occurred while removing UE {ue_id}: {e}")
        return jsonify({'error': 'An error occurred while removing UE', 'details': str(e)}), 500
    
########################################################################################################################
#This is an API for get ue metric  like throuput, jitter, packet loss and so on via API from influxDB with json format
@app.route('/ue_metrics', methods=['GET'])
def ue_metrics():
    ue_id = request.args.get('ue_id')

    # Validation for alphanumeric ue_id
    if not ue_id:
        return jsonify({'error': "Missing 'ue_id' parameter"}), 400
    elif not re.match("^[a-zA-Z0-9]+$", ue_id):
        return jsonify({'error': "Invalid 'ue_id' format. 'ue_id' must be alphanumeric."}), 400

    try:
        # Check if UE exists in the system
        from network.ue_manager import UEManager  # Ensure this import is at the top of your file
        ue_manager = UEManager.get_instance()
        if not ue_manager.get_ue_by_id(ue_id):
            return jsonify({'error': f"UE {ue_id} not found in the system"}), 404

        db_manager = DatabaseManager.get_instance()
        metrics = db_manager.get_ue_metrics(ue_id)
        if metrics:
            response = jsonify({'metrics': metrics})
            response.headers['Content-Type'] = 'application/json'
            return response, 200
        else:
            return jsonify({'message': f'No metrics found for UE {ue_id}'}), 404
    except Exception as e:
        API_logger.error(f"An error occurred while retrieving metrics for UE {ue_id}: {e}")
        return jsonify({'error': 'An error occurred while retrieving metrics'}), 500

########################################################################################################################
#This is an API for add a ue instance via API, we should send a jason format of the ue info to add it.
@app.route('/add_ue', methods=['POST'])
def add_ue():
    data = request.json
    
    # Validate input data for required fields, for example, 'ue_id'
    if 'ue_id' not in data:
        API_logger.error("Missing 'ue_id' in request data")
        return jsonify({'error': "Missing 'ue_id'"}), 400
    
    try:
        # Pass the entire data dictionary to the CommandHandler
        result, message = CommandHandler.handle_command('add_ue', data)
        
        if result:
            API_logger.info(f"UE {data['ue_id']} added successfully.")
            return jsonify({'message': f"UE {data['ue_id']} added successfully"}), 200
        else:
            API_logger.warning(f"Failed to add UE {data['ue_id']}: {message}")
            return jsonify({'error': f"Failed to add UE {data['ue_id']}", 'details': message}), 400
    except Exception as e:
        API_logger.error(f"An error occurred while adding UE {data.get('ue_id', 'unknown')}: {e}")
        traceback.print_exc()
        return jsonify({'error': 'An error occurred while adding UE', 'details': str(e)}), 500

#########################################################################################################################
#This is a API for chnage one or more attribute of the ue instance! for example chnage one parameter but in live network.
@app.route('/update_ue', methods=['POST'])
def update_ue():
    data = request.json

    # Validate input data
    if 'ue_id' not in data:
        API_logger.error("Missing 'ue_id' in request data")
        return jsonify({'error': "Missing 'ue_id' in request data"}), 400

    # Extract UE ID and parameters to be updated
    ue_id = data['ue_id']
    update_params = {key: value for key, value in data.items() if key != 'ue_id'}

    try:
        # Use CommandHandler to update the UE
        update_result, message = CommandHandler._update_ue({'ue_id': ue_id, **update_params})

        if update_result:
            API_logger.info(f'UE {ue_id} updated successfully')
            return jsonify({'message': message}), 200
        else:
            API_logger.error(f'UE {ue_id} not found or update failed')
            return jsonify({'error': message}), 404

    except Exception as e:
        API_logger.error(f'An error occurred while updating UE: {str(e)}')
        return jsonify({'error': 'An error occurred while updating UE'}), 500

#########################################################################################################
#This is A API for start the traffic of the each UE
@app.route('/start_ue_traffic', methods=['POST'])
def start_ue_traffic():
    data = request.json
    if 'ue_id' not in data:
        API_logger.error("Missing 'ue_id' in request data")
        return jsonify({'error': "Missing 'ue_id'"}), 400

    result, message = CommandHandler.handle_command('start_ue_traffic', data)
    if result:
        return jsonify({'message': message}), 200
    else:
        API_logger.error(f"An error occurred while starting UE {data.get('ue_id', 'unknown')}")
        return jsonify({'error': message}), 400

#########################################################################################################
#This is a API for Stop the traffic of the each UE
@app.route('/stop_ue_traffic', methods=['POST'])
def stop_ue_traffic():
    data = request.json
    if 'ue_id' not in data:
        API_logger.error("Missing 'ue_id' in request data")
        return jsonify({'error': "Missing 'ue_id'"}), 400

    result, message = CommandHandler.handle_command('stop_ue_traffic', data)
    if result:
        return jsonify({'message': message}), 200
    else:
        API_logger.error(f"An error occurred while stopping UE {data.get('ue_id', 'unknown')}:")
        return jsonify({'error': message}), 400
#########################################################################################################
# This is an API for get the load of the each sector.
@app.route('/sector_load', methods=['GET'])
def sector_load():
    sector_id = request.args.get('sector_id')

    if not sector_id:
        return jsonify({'error': "Missing 'sector_id' parameter"}), 400
    # Additional validation can be added here

    try:
        db_manager = DatabaseManager.get_instance()
        load_metrics = db_manager.get_sector_load(sector_id)
        if load_metrics:
            return jsonify({'load_metrics': load_metrics}), 200
        else:
            return jsonify({'message': f'No load metrics found for sector {sector_id}'}), 404
    except Exception as e:
        API_logger.error(f"An error occurred while retrieving load metrics for sector {sector_id}: {e}")
        return jsonify({'error': 'An error occurred while retrieving load metrics'}), 500
######################################################################################################### 
#This is an API for change the traffic pattern
@app.route('/set_traffic', methods=['POST'])
def set_traffic():
    data = request.json
    command_result, message = CommandHandler.handle_command('set_custom_traffic', data)
    if command_result:
        return jsonify({'message': message}), 200
    else:
        API_logger.error(f"Failed to set custom traffic: {message}")
        return jsonify({'error': message}), 500
#########################################################################################################
# This is an API for delete all information inside the databse.
@app.route('/flush_database', methods=['POST'])
def flush_database():
    data = request.get_json()
    if not data or data.get('confirm') != 'yes':
        return jsonify({'error': 'Confirmation required'}), 400

    # Passing an empty dictionary as data for commands that do not require additional data.
    result, message = CommandHandler.handle_command('flush_all_data', {})

    if result:
        return jsonify({'message': message}), 200
    else:
        API_logger.error(f"Database flush failed: {message}")
        return jsonify({'error': message}), 500
#########################################################################################################
# this API return the list of the current ue in database
@app.route('/api/ues', methods=['GET'])
def get_ues():
    try:
        # Initialize your DatabaseManager
        db_manager = DatabaseManager.get_instance()
        # Fetch UE IDs from the database
        ue_ids = db_manager.get_all_ue_ids()
        # Return the list of UE IDs
        return jsonify({'ue_ids': ue_ids}), 200
    except Exception as e:
        # Log the error and return an error message
        # Make sure to set up logging appropriately
        API_logger.error(f"Failed to retrieve UE IDs: {e}")  
        return jsonify({'error': 'Failed to retrieve UE IDs'}), 500
#########################################################################################################
#This is an API for for moving a UE  from one sector, to another place (sector!)
#@app.route('/move_ue', methods=['POST'])
#def move_ue():
    #data = request.get_json()
    #ue_id = data.get('ue_id')

    # Retrieve UE and validate existence
    #ue_manager = UEManager.get_instance()
    #ue = ue_manager.get_ue_by_id(ue_id)
    #if not ue:
        #return jsonify({'error': 'UE not found'}), 404
    
    # Logic to move UE to new cell (simplified for example)
    # This would involve more detailed logic to handle sector/gNodeB changes
    #success = ue_manager.move_ue_to_cell(ue_id,)
    
    #if success:
        #return jsonify({'message': 'UE moved successfully'}), 200
# else:
        #return jsonify({'error': 'Failed to move UE'}), 500
###########################################################################################################