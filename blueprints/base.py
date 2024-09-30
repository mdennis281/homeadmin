from flask import Blueprint, render_template, request
from flask import session, redirect, url_for
from functools import wraps
from user_manager import UserManager
from homebridge.client import HomeBridgeClient
import os

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
    rooms = hbc.get_accessories_layout()
    return render_template('index.html', rooms=rooms, action_recording=action_recording)

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

@base_bp.route('/actions')
@login_required
def actions():
    return render_template('actions.html')
