
from flask import Flask, jsonify, render_template, request, redirect, url_for,Response,abort
from flask_cors import CORS
from homebridge.client import HomeBridgeClient
import threading
from homebridge.action_manager import ActionManager
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize HomeBridgeClient with your credentials
HOME_BRIDGE_HOST = os.getenv('HOME_BRIDGE_HOST')
HOME_BRIDGE_USER = os.getenv('HOME_BRIDGE_USER')
HOME_BRIDGE_PASSWORD = os.getenv('HOME_BRIDGE_PASSWORD')

hbc = HomeBridgeClient(
    HOME_BRIDGE_HOST, 
    HOME_BRIDGE_USER, 
    HOME_BRIDGE_PASSWORD
)

@app.before_request
def validate_user():
    
    auth = request.headers.get('SecretAuth')
    ip = request.remote_addr
    if not ip.startswith('10.0.'):
        if auth != HOME_BRIDGE_PASSWORD:
            abort(401)




@app.route('/')
def index():
    action_recording = request.args.get('recordAction')
    rooms = hbc.get_accessories_layout()
    return render_template('index.html',  rooms=rooms,action_recording=action_recording)

@app.route('/room/<room_name>')
def room(room_name):
    
    devices = []
    rooms = hbc.get_accessories_layout()
    action_recording = request.args.get('recordAction')
    for room in rooms:
        if room.name == room_name:
            for service in room.services:
                device = hbc.get_accessory(service.uniqueId)
                devices.append(device)
            break
    return render_template('room.html', room_name=room_name, devices=devices, action_recording=action_recording)


@app.route('/actions')
def actions():

    return render_template('actions.html')



@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    rooms = []
    for room in hbc.get_accessories_layout():
        room_dict = room.to_dict()
        rooms.append(room_dict)
    return jsonify(rooms)

@app.route('/api/rooms/<room_name>/devices',methods=['GET'])
def get_room_devices(room_name:str):
    rooms = hbc.get_accessories_layout()
    for room in rooms:
        if room.name == room_name:
            devices = []
            for service in room.services:
                device = hbc.get_accessory(service.uniqueId)
                devices.append(device.get_summary())
            return jsonify(devices)
    return jsonify([])

@app.route('/api/device/<unique_id>', methods=['GET'])
def get_device(unique_id):
    device = hbc.get_accessory(unique_id)
    device_dict = device.to_dict()
    return jsonify(device_dict)

@app.route('/api/device/<unique_id>', methods=['POST'])
def update_device(unique_id,data=None) -> Response:
    if data is None: data = request.json
    device = hbc.get_accessory(unique_id)
    for char_type, value in data.items():
        print(char_type,value)
        device.set_characteristic(char_type, value)
    updated_device = hbc.update_accessory_characteristic(device)
    return jsonify({
        'status': 'success',
        'updatedCharacteristics': updated_device.get_characteristics()
    })

am = ActionManager()

@app.route('/api/actions', methods=['GET'])
def list_actions():
    """Returns the list of all saved actions."""
    return jsonify(am.list())

@app.route('/api/actions/<action_name>', methods=['GET'])
def get_action(action_name):
    """Returns the details of a specific action."""
    action = am.get(action_name)
    if action:
        return jsonify(action)
    else:
        return jsonify({'error': 'Action not found'}), 404

@app.route('/api/actions/<action_name>', methods=['PUT'])
def save_action(action_name):
    """Saves a new action or updates an existing one."""
    action_data = request.get_json()
    if not action_data:
        return jsonify({'error': 'Invalid data'}), 400
    am.save(action_name, action_data)
    return jsonify({'message': 'Action saved successfully'})

@app.route('/api/actions/<action_name>/run')
def run_action(action_name):
    action = am.get(action_name)
    threads = []
    for device, updates in action.items():
        threads.append(threading.Thread(target=update_device,args=(device,updates)))
        threads[-1].start()
    for t in threads:
        t.join()
        
    # will throw on failure
    return jsonify(
        {
            'status': 'success', 
            'msg': f'{action_name} applied changes to {len(action.keys())} device(s)'
        }
    )
        

    



@app.errorhandler(Exception)
def handle_exception(e):
    response = {
        'status': 'error',
        'message': str(e)
    }
    return jsonify(response), 500

if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0',ssl_context=('george.dipduo.com.crt', 'george.dipduo.com.key'))
