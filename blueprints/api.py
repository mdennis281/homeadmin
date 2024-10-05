from flask import Blueprint, request, jsonify, abort, session
from functools import wraps
from user_manager import UserManager
from typing import List

api_bp = Blueprint('api', __name__)

user_manager = UserManager()

def api_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for API key in headers or args
        api_key = request.headers.get('X-Api-Key') or request.args.get('api_key')
        if api_key:
            print('API KEY',api_key)
            username = user_manager.get_username_for_api_key(api_key)
            if username:
                # Optionally, you can set session or g.username = username
                return f(*args, **kwargs)
        # Check for session login
        elif 'username' in session:
            return f(*args, **kwargs)
        else:
            return jsonify({'error': 'Unauthorized'}), 401
    return decorated_function

# Import necessary modules and initialize HomeBridgeClient and ActionManager as in your original code

from homebridge.client import HomeBridgeClient
from homebridge.action_manager import ActionManager
from threading import Thread
import os

HOME_BRIDGE_HOST = os.getenv('HOME_BRIDGE_HOST')
HOME_BRIDGE_USER = os.getenv('HOME_BRIDGE_USER')
HOME_BRIDGE_PASSWORD = os.getenv('HOME_BRIDGE_PASSWORD')

hbc = HomeBridgeClient(
    HOME_BRIDGE_HOST,
    HOME_BRIDGE_USER,
    HOME_BRIDGE_PASSWORD
)

am = ActionManager()

@api_bp.route('/rooms', methods=['GET'])
@api_auth_required
def get_rooms():
    rooms = []
    for room in hbc.get_accessories_layout():
        room_dict = room.to_dict()
        rooms.append(room_dict)
    return jsonify(rooms)

@api_bp.route('/rooms/<room_name>/devices', methods=['GET'])
@api_auth_required
def get_room_devices(room_name: str):
    rooms = hbc.get_accessories_layout()
    for room in rooms:
        if room.name == room_name:
            devices = []
            for service in room.services:
                device = hbc.get_accessory(service.uniqueId)
                devices.append(device.get_summary())
            return jsonify(devices)
    return jsonify([])

@api_bp.route('/device/<unique_id>', methods=['GET'])
@api_auth_required
def get_device(unique_id):
    device = hbc.get_accessory(unique_id)
    device_dict = device.to_dict()
    return jsonify(device_dict)

@api_bp.route('/device/<unique_id>', methods=['POST'])
@api_auth_required
def update_device(unique_id, data=None):
    if data is None:
        data = request.json
    device = hbc.get_accessory(unique_id)
    for char_type, value in data.items():
        print(char_type, value)
        device.set_characteristic(char_type, value)
    updated_device = hbc.update_accessory_characteristic(device)
    return jsonify({
        'status': 'success',
        'updatedCharacteristics': updated_device.get_characteristics()
    })



@api_bp.route('/actions', methods=['GET'])
@api_auth_required
def list_actions():
    """Returns the list of all saved actions."""
    return jsonify(am.list())

@api_bp.route('/actions/<action_name>', methods=['GET'])
@api_auth_required
def get_action(action_name):
    """Returns the details of a specific action."""
    action = am.get(action_name)
    if action:
        return jsonify(action)
    else:
        return jsonify({'error': 'Action not found'}), 404

@api_bp.route('/actions/<action_name>', methods=['PUT'])
@api_auth_required
def save_action(action_name):
    """Saves a new action or updates an existing one."""
    action_data = request.get_json()
    if not action_data:
        return jsonify({'error': 'Invalid data'}), 400
    am.save(action_name, action_data)
    return jsonify({'message': 'Action saved successfully'})



@api_bp.route('/actions/<action_name>/run')
@api_auth_required
def run_action(action_name):
    updated_devices = []

    def do_update_device_threaded(unique_id,data):
        if data is None:
            data = request.json
        device = hbc.get_accessory(unique_id)
        for char_type, value in data.items():
            device.set_characteristic(char_type, value)
        updated_device = hbc.update_accessory_characteristic(device)
        if updated_device:
            updated_devices.append(updated_device.serviceName)

    action = am.get(action_name)
    threads: List[Thread] = []

    # thread off updates (this is slow for big action groups otherwise)
    for device, updates in action.items():
        threads.append(Thread(
                target=do_update_device_threaded, 
                args=(device, updates, updated_devices)
        ))
        threads[-1].start()

    for t in threads:
        t.join()

    # Will throw on failure
    return jsonify(
        {
            'status': 'success',
            'msg': f'{action_name} applied changes to {len(updated_devices)} device(s)'
        }
    )



@api_bp.errorhandler(Exception)
def handle_exception(e):
    response = {
        'status': 'error',
        'message': str(e)
    }
    return jsonify(response), 500
