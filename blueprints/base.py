from flask import Blueprint, render_template, request
from flask import session, redirect, url_for
from functools import wraps
from user_manager import UserManager
from homebridge.client import HomeBridgeClient
import os
from homebridge.action_manager import ActionManager

base_bp = Blueprint('base', __name__, template_folder='../templates')

HOME_BRIDGE_HOST = os.getenv('HOME_BRIDGE_HOST')
HOME_BRIDGE_USER = os.getenv('HOME_BRIDGE_USER')
HOME_BRIDGE_PASSWORD = os.getenv('HOME_BRIDGE_PASSWORD')

hbc = HomeBridgeClient(
    HOME_BRIDGE_HOST,
    HOME_BRIDGE_USER,
    HOME_BRIDGE_PASSWORD
)

user_manager = UserManager()
am = ActionManager()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@base_bp.route('/')
@login_required
def index():
    action_recording = request.args.get('recordAction')
    return render_template(
        'index.html', 
        rooms=hbc.get_accessories_layout(), 
        actions=am.list(),
        action_recording=action_recording
    )

@base_bp.route('/room/<room_name>')
@login_required
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

@base_bp.route('/action/<action_name>')
@login_required
def view_action(action_name):
    devices = []
    action = am.get(action_name)
    for device_id,characteristics in action.items():
        device = hbc.get_accessory(device_id)
        for type,v in characteristics.items():
            device.set_characteristic(type,v)
        devices.append(device)
    return render_template(
        'action_editor.html',
        room_name=action_name,
        devices=devices,
        action_recording=False
    )


    

@base_bp.route('/actions')
@login_required
def actions():
    return render_template('actions.html')
