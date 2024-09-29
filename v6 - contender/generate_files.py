import os

# File contents
files = {
    'app.py': '''
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_cors import CORS
from homebridge.client import HomeBridgeClient
import json
import os

app = Flask(__name__)
CORS(app)

# Initialize HomeBridgeClient with your credentials
from config import HOME_BRIDGE_HOST, HOME_BRIDGE_USER, HOME_BRIDGE_PASSWORD
hbc = HomeBridgeClient(HOME_BRIDGE_HOST, HOME_BRIDGE_USER, HOME_BRIDGE_PASSWORD)

# Path to user preferences
PREFERENCES_FILE = os.path.join('user_data', 'preferences.json')

def load_preferences():
    if os.path.exists(PREFERENCES_FILE):
        with open(PREFERENCES_FILE, 'r') as f:
            return json.load(f)
    else:
        return {'favorites': [], 'actions': []}

def save_preferences(prefs):
    with open(PREFERENCES_FILE, 'w') as f:
        json.dump(prefs, f)

@app.route('/')
def index():
    preferences = load_preferences()
    rooms = hbc.get_accessories_layout()
    return render_template('index.html', preferences=preferences, rooms=rooms)

@app.route('/room/<room_name>')
def room(room_name):
    preferences = load_preferences()
    devices = []
    rooms = hbc.get_accessories_layout()
    for room in rooms:
        if room.name == room_name:
            for service in room.services:
                device = hbc.get_accessory(service.uniqueId)
                devices.append(device.to_dict())
            break
    return render_template('room.html', room_name=room_name, devices=devices, preferences=preferences)

@app.route('/favorites')
def favorites():
    preferences = load_preferences()
    return render_template('favorites.html', preferences=preferences)

@app.route('/actions')
def actions():
    preferences = load_preferences()
    return render_template('actions.html', preferences=preferences)

@app.route('/create_action', methods=['GET', 'POST'])
def create_action():
    if request.method == 'POST':
        action_data = request.json
        preferences = load_preferences()
        preferences['actions'].append(action_data)
        save_preferences(preferences)
        return jsonify({'status': 'success'})
    else:
        preferences = load_preferences()
        return render_template('create_action.html', preferences=preferences)

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    rooms = []
    for room in hbc.get_accessories_layout():
        room_dict = room.to_dict()
        rooms.append(room_dict)
    return jsonify(rooms)

@app.route('/api/rooms/<room_name>/devices', methods=['GET'])
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

@app.route('/api/device/<unique_id>', methods=['GET'])
def get_device(unique_id):
    device = hbc.get_accessory(unique_id)
    device_dict = device.to_dict()
    return jsonify(device_dict)

@app.route('/api/device/<unique_id>', methods=['POST'])
def update_device(unique_id):
    data = request.json
    device = hbc.get_accessory(unique_id)
    for char_type, value in data.items():
        device.set_characteristic(char_type, value)
    updated_device = hbc.update_accessory_characteristic(device)
    return jsonify({
        'status': 'success',
        'updatedCharacteristics': updated_device.get_characteristics()
    })

@app.route('/api/preferences', methods=['POST'])
def update_preferences():
    data = request.json
    preferences = load_preferences()
    preferences.update(data)
    save_preferences(preferences)
    return jsonify({'status': 'success'})

@app.route('/api/actions/<int:action_id>', methods=['POST'])
def execute_action(action_id):
    preferences = load_preferences()
    try:
        action = preferences['actions'][action_id]
        devices_actions = action['devices']
        for device_action in devices_actions:
            unique_id = device_action['uniqueId']
            characteristics = device_action['characteristics']
            device = hbc.get_accessory(unique_id)
            for char in characteristics:
                device.set_characteristic(char['type'], char['value'])
            hbc.update_accessory_characteristic(device)
        return jsonify({'status': 'success'})
    except IndexError:
        return jsonify({'status': 'error', 'message': 'Action not found'}), 404

@app.errorhandler(Exception)
def handle_exception(e):
    response = {
        'status': 'error',
        'message': str(e)
    }
    return jsonify(response), 500

if __name__ == '__main__':
    app.run(debug=True)
''',
    'templates/base.html': '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ title or 'Smart Home Device Manager' }}</title>
    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <!-- Bootstrap JS -->
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.bundle.min.js"></script>
    <!-- Core JS -->
    <script src="{{ url_for('static', filename='js/core.js') }}"></script>
    {% block head %}
    {% endblock %}
</head>
<body class="bg-dark text-white">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <a class="navbar-brand" href="{{ url_for('index') }}">Smart Home</a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            {% if preferences %}
            <ul class="navbar-nav">
                <li class="nav-item">
                    <a class="nav-link" href="{{ url_for('favorites') }}">Favorites</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{{ url_for('actions') }}">Actions</a>
                </li>
            </ul>
            {% endif %}
        </div>
    </nav>
    <div class="container mt-4">
        {% block content %}
        {% endblock %}
    </div>
    {% block scripts %}
    {% endblock %}
</body>
</html>
''',
    'templates/index.html': '''
{% extends 'base.html' %}
{% block content %}
<h1>Rooms</h1>
<div class="list-group">
    {% for room in rooms %}
    <a href="{{ url_for('room', room_name=room.name) }}" class="list-group-item list-group-item-action bg-dark text-white">
        {{ room.name }}
    </a>
    {% endfor %}
</div>
{% endblock %}
''',
    'templates/room.html': '''
{% extends 'base.html' %}
{% block content %}
<h1>{{ room_name }}</h1>
<div id="devices-container">
    {% for device in devices %}
        {% set uniqueId = device.uniqueId %}
        {% set serviceName = device.serviceName %}
        {% set characteristics = device.serviceCharacteristics %}
        {% set values = device.values %}
        {% include 'devices/' + device.type + '.html' %}
    {% endfor %}
</div>
{% endblock %}
{% block scripts %}
<script>
$(document).ready(function() {
    // Initialize device-specific JS
    {% for device in devices %}
        $.getScript('{{ url_for('static', filename='js/devices/' + device.type + '.js') }}', function() {
            if (typeof initDevice === 'function') {
                initDevice('{{ device.uniqueId }}');
            }
        });
    {% endfor %}
});
</script>
{% endblock %}
''',
    'templates/devices/Lightbulb.html': '''
<div class="card device-card mb-3" data-unique-id="{{ uniqueId }}">
    <div class="card-body">
        <h5 class="card-title">{{ serviceName }}</h5>
        <div class="form-group form-check">
            <input type="checkbox" id="on-{{ uniqueId }}" class="form-check-input toggle-on-off" {% if values.On %}checked{% endif %}>
            <label class="form-check-label" for="on-{{ uniqueId }}">On/Off</label>
        </div>
        {% for char in characteristics %}
            {% if char.type == 'Brightness' %}
                <div class="form-group">
                    <label for="brightness-{{ uniqueId }}">Brightness</label>
                    <input type="range" id="brightness-{{ uniqueId }}" min="{{ char.minValue }}" max="{{ char.maxValue }}" value="{{ values.Brightness }}" class="custom-range">
                </div>
            {% elif char.type == 'Hue' %}
                <div class="form-group">
                    <label for="hue-{{ uniqueId }}">Hue</label>
                    <input type="range" id="hue-{{ uniqueId }}" min="{{ char.minValue }}" max="{{ char.maxValue }}" value="{{ values.Hue }}" class="custom-range">
                </div>
            {% elif char.type == 'Saturation' %}
                <div class="form-group">
                    <label for="saturation-{{ uniqueId }}">Saturation</label>
                    <input type="range" id="saturation-{{ uniqueId }}" min="{{ char.minValue }}" max="{{ char.maxValue }}" value="{{ values.Saturation }}" class="custom-range">
                </div>
            {% elif char.type == 'ColorTemperature' %}
                <div class="form-group">
                    <label for="colortemperature-{{ uniqueId }}">Color Temperature</label>
                    <input type="range" id="colortemperature-{{ uniqueId }}" min="{{ char.minValue }}" max="{{ char.maxValue }}" value="{{ values.ColorTemperature }}" class="custom-range">
                </div>
            {% endif %}
        {% endfor %}
    </div>
</div>
''',
    'templates/devices/Switch.html': '''
<div class="card device-card mb-3" data-unique-id="{{ uniqueId }}">
    <div class="card-body">
        <h5 class="card-title">{{ serviceName }}</h5>
        <div class="form-group form-check">
            <input type="checkbox" id="on-{{ uniqueId }}" class="form-check-input toggle-on-off" {% if values.On %}checked{% endif %}>
            <label class="form-check-label" for="on-{{ uniqueId }}">On/Off</label>
        </div>
    </div>
</div>
''',
    'templates/devices/GarageDoorOpener.html': '''
<div class="card device-card mb-3" data-unique-id="{{ uniqueId }}">
    <div class="card-body">
        <h5 class="card-title">{{ serviceName }}</h5>
        <div class="form-group">
            <label for="doorstate-{{ uniqueId }}">Target Door State</label>
            <select id="doorstate-{{ uniqueId }}" class="form-control">
                <option value="0" {% if values.TargetDoorState == 0 %}selected{% endif %}>Open</option>
                <option value="1" {% if values.TargetDoorState == 1 %}selected{% endif %}>Closed</option>
            </select>
        </div>
        <p>Current Door State: <span id="currentstate-{{ uniqueId }}">
            {% if values.CurrentDoorState == 0 %}Open{% elif values.CurrentDoorState == 1 %}Closed{% elif values.CurrentDoorState == 2 %}Opening{% elif values.CurrentDoorState == 3 %}Closing{% elif values.CurrentDoorState == 4 %}Stopped{% else %}Unknown{% endif %}
        </span></p>
        <p>Obstruction Detected: <span id="obstruction-{{ uniqueId }}">{{ 'Yes' if values.ObstructionDetected == 1 else 'No' }}</span></p>
    </div>
</div>
''',
    'static/css/style.css': '''
body {
    background-color: #121212;
    color: #ffffff;
}

.card {
    background-color: #1e1e1e;
    color: #ffffff;
    margin-bottom: 1rem;
}

.navbar {
    background-color: #1e1e1e;
}

.btn {
    margin-right: 0.5rem;
}

.custom-range {
    width: 100%;
}
''',
    'static/js/core.js': '''
function updateDeviceState(uniqueId, data, successCallback, errorCallback) {
    $.ajax({
        url: '/api/device/' + uniqueId,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: successCallback,
        error: errorCallback
    });
}

function getDeviceState(uniqueId, successCallback, errorCallback) {
    $.ajax({
        url: '/api/device/' + uniqueId,
        method: 'GET',
        success: successCallback,
        error: errorCallback
    });
}

function pollDeviceState(uniqueId, callback, interval) {
    setInterval(function() {
        getDeviceState(uniqueId, callback, function(error) {
            console.error('Error polling device state:', error);
        });
    }, interval);
}
''',
    'static/js/devices/Lightbulb.js': '''
function initDevice(uniqueId) {
    (function(uniqueId) {
        var deviceCard = $('.device-card[data-unique-id="' + uniqueId + '"]');

        // On/Off toggle
        deviceCard.find('.toggle-on-off').change(function() {
            var isOn = $(this).is(':checked') ? 1 : 0;
            updateDeviceState(uniqueId, {'On': isOn}, function(response) {
                console.log('Device updated:', response);
            }, function(error) {
                console.error('Error updating device:', error);
            });
        });

        // Handle other characteristics
        deviceCard.find('input[type="range"]').on('input change', function() {
            var inputId = $(this).attr('id');
            var charType = inputId.split('-')[0];
            var value = $(this).val();
            var data = {};
            data[charType.charAt(0).toUpperCase() + charType.slice(1)] = parseFloat(value);
            updateDeviceState(uniqueId, data, function(response) {
                console.log('Device updated:', response);
            }, function(error) {
                console.error('Error updating device:', error);
            });
        });

        // Polling device state
        pollDeviceState(uniqueId, function(deviceData) {
            var values = deviceData.values;
            // Update UI elements with new values
            deviceCard.find('.toggle-on-off').prop('checked', values.On == 1);
            if (values.Brightness !== undefined) {
                deviceCard.find('#brightness-' + uniqueId).val(values.Brightness);
            }
            if (values.Hue !== undefined) {
                deviceCard.find('#hue-' + uniqueId).val(values.Hue);
            }
            if (values.Saturation !== undefined) {
                deviceCard.find('#saturation-' + uniqueId).val(values.Saturation);
            }
            if (values.ColorTemperature !== undefined) {
                deviceCard.find('#colortemperature-' + uniqueId).val(values.ColorTemperature);
            }
        }, 5000); // Poll every 5 seconds
    })(uniqueId);
}
''',
    'static/js/devices/Switch.js': '''
function initDevice(uniqueId) {
    (function(uniqueId) {
        var deviceCard = $('.device-card[data-unique-id="' + uniqueId + '"]');

        // On/Off toggle
        deviceCard.find('.toggle-on-off').change(function() {
            var isOn = $(this).is(':checked') ? 1 : 0;
            updateDeviceState(uniqueId, {'On': isOn}, function(response) {
                console.log('Device updated:', response);
            }, function(error) {
                console.error('Error updating device:', error);
            });
        });

        // Polling device state
        pollDeviceState(uniqueId, function(deviceData) {
            var values = deviceData.values;
            // Update UI elements with new values
            deviceCard.find('.toggle-on-off').prop('checked', values.On == 1);
        }, 5000); // Poll every 5 seconds
    })(uniqueId);
}
''',
    'static/js/devices/GarageDoorOpener.js': '''
function initDevice(uniqueId) {
    (function(uniqueId) {
        var deviceCard = $('.device-card[data-unique-id="' + uniqueId + '"]');

        // Door state change
        deviceCard.find('#doorstate-' + uniqueId).change(function() {
            var targetState = parseInt($(this).val());
            updateDeviceState(uniqueId, {'TargetDoorState': targetState}, function(response) {
                console.log('Device updated:', response);
            }, function(error) {
                console.error('Error updating device:', error);
            });
        });

        // Polling device state
        pollDeviceState(uniqueId, function(deviceData) {
            var values = deviceData.values;
            // Update UI elements with new values
            deviceCard.find('#doorstate-' + uniqueId).val(values.TargetDoorState);
            var currentStateText = '';
            switch (values.CurrentDoorState) {
                case 0:
                    currentStateText = 'Open';
                    break;
                case 1:
                    currentStateText = 'Closed';
                    break;
                case 2:
                    currentStateText = 'Opening';
                    break;
                case 3:
                    currentStateText = 'Closing';
                    break;
                case 4:
                    currentStateText = 'Stopped';
                    break;
                default:
                    currentStateText = 'Unknown';
            }
            deviceCard.find('#currentstate-' + uniqueId).text(currentStateText);
            deviceCard.find('#obstruction-' + uniqueId).text(values.ObstructionDetected == 1 ? 'Yes' : 'No');
        }, 5000); // Poll every 5 seconds
    })(uniqueId);
}
'''
}

for filepath, content in files.items():
    # Ensure directory exists
    dirpath = os.path.dirname(filepath)
    if dirpath and not os.path.exists(dirpath):
        os.makedirs(dirpath)
    # Write file
    with open(filepath, 'w') as f:
        f.write(content.strip())
