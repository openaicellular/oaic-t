# API_Gateway/API.py modifications
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
from network.command_handler import CommandHandler
from logs.logger_config import API_logger
import traceback
from flask import Flask, request, jsonify, Response
from dotenv import load_dotenv
import logging

app = Flask(__name__)
load_dotenv()


#########################################################################################################
@app.route('/remove_ue', methods=['POST'])
def remove_ue():
    data = request.json
    
    # Validate input data
    if 'ue_id' not in data:
        API_logger.error("Missing 'ue_id' in request data")
        return jsonify({'error': "Missing 'ue_id'"}), 400
    
    ue_id = data['ue_id']
    
    try:
        # Assuming CommandHandler.handle_command is properly implemented to handle 'remove_ue' command
        # and now returns a boolean indicating success or failure
        result, message = CommandHandler.handle_command('remove_ue', {'ue_id': ue_id})
        
        if result:
            API_logger.info(f"UE {ue_id} successfully removed.")
            return jsonify({'message': f'UE {ue_id} successfully removed', 'ue_id': ue_id}), 200
        else:
            API_logger.warning(f"Failed to remove UE {ue_id}: {message}")
            return jsonify({'error': f'Failed to remove UE {ue_id}', 'details': message}), 400
    except Exception as e:
        API_logger.error(f"An error occurred while removing UE {ue_id}: {e}")
        return jsonify({'error': 'An error occurred while removing UE', 'details': str(e)}), 500
    
#########################################################################################################
@app.route('/metrics', methods=['GET'])
def metrics():
    # Existing implementation for metrics endpoint
    # ...
    return Response

#########################################################################################################
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

#########################################################################################################
@app.route('/update_ue', methods=['POST'])
def update_ue():
    data = request.json
    # Existing validation and logging logic
    # ...
    try:
        CommandHandler.handle_command('update_ue', data)
        return jsonify({'message': 'UE updated successfully'}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An error occurred while updating UE'}), 500

#########################################################################################################
if __name__ == '__main__':
    print("Starting API server...")
    app.run(debug=True)