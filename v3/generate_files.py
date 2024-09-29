import os

# Define the project structure and file contents
project_structure = {
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
    # Get rooms
    rooms = []
    for room in hbc.get_accessories_layout():
        room_dict = room.to_dict()
        rooms.append(room_dict)
    return render_template('index.html', preferences=preferences, rooms=rooms)

@app.route('/room/<room_name>')
def room(room_name):
    preferences = load_preferences()
    # Get devices in the room
    rooms = hbc.get_accessories_layout()
    devices = []
    for room_obj in rooms:
        if room_obj.name == room_name:
            for service in room_obj.services:
                device = hbc.get_accessory(service.uniqueId)
                devices.append(device.get_summary())
            break
    return render_template('room.html', room_name=room_name, preferences=preferences, devices=devices)

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

    'config.py': '''
HOME_BRIDGE_HOST = 'your_home_bridge_host'
HOME_BRIDGE_USER = 'your_username'
HOME_BRIDGE_PASSWORD = 'your_password'
''',

    'user_data': {
        'preferences.json': '{}'
    },

    'templates': {
        'base.html': '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ title if title else "Smart Home Device Manager" }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Custom CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">

    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>

    <!-- Bootstrap Bundle JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

    <!-- Core JS -->
    <script src="{{ url_for('static', filename='js/core.js') }}"></script>

    {% block head %}{% endblock %}
</head>
<body class="bg-dark text-white">
    <div class="container">
        {% block content %}{% endblock %}
    </div>
    {% block scripts %}{% endblock %}
</body>
</html>
''',

        'index.html': '''
{% extends 'base.html' %}
{% block content %}
<h1 class="mt-4">Rooms</h1>
<ul class="list-group list-group-flush">
    {% for room in rooms %}
    <li class="list-group-item bg-dark">
        <a href="{{ url_for('room', room_name=room.name) }}" class="text-white">{{ room.name }}</a>
    </li>
    {% endfor %}
</ul>
{% endblock %}
''',

        'room.html': '''
{% extends 'base.html' %}
{% block content %}
<h1 class="mt-4">{{ room_name }}</h1>
<div class="devices">
  {% for device in devices %}
    {% include 'devices/' + device.type + '.html' %}
  {% endfor %}
</div>
{% endblock %}
{% block scripts %}
    {% set device_types = devices | map(attribute='type') | unique | list %}
    {% for device_type in device_types %}
    <script src="{{ url_for('static', filename='js/devices/' + device_type + '.js') }}"></script>
    {% endfor %}
{% endblock %}
''',

        'devices': {
            'Lightbulb.html': '''
<div class="device lightbulb mb-4" id="device-{{ device.uniqueId }}">
    <h3>{{ device.serviceName }}</h3>
    <div class="form-check form-switch">
        {% for characteristic in device.characteristics %}
            {% if characteristic.type == 'On' %}
                <input class="form-check-input" type="checkbox" id="on-{{ device.uniqueId }}" {% if characteristic.value %}checked{% endif %}>
                <label class="form-check-label" for="on-{{ device.uniqueId }}">On</label>
            {% endif %}
        {% endfor %}
    </div>
    {% for characteristic in device.characteristics %}
        {% if characteristic.type == 'Brightness' %}
            <label for="brightness-{{ device.uniqueId }}" class="form-label mt-2">Brightness</label>
            <input type="range" class="form-range" id="brightness-{{ device.uniqueId }}" min="{{ characteristic.minValue }}" max="{{ characteristic.maxValue }}" value="{{ characteristic.value }}">
        {% elif characteristic.type == 'Hue' %}
            <label for="hue-{{ device.uniqueId }}" class="form-label mt-2">Hue</label>
            <input type="range" class="form-range" id="hue-{{ device.uniqueId }}" min="{{ characteristic.minValue }}" max="{{ characteristic.maxValue }}" value="{{ characteristic.value }}">
        {% elif characteristic.type == 'Saturation' %}
            <label for="saturation-{{ device.uniqueId }}" class="form-label mt-2">Saturation</label>
            <input type="range" class="form-range" id="saturation-{{ device.uniqueId }}" min="{{ characteristic.minValue }}" max="{{ characteristic.maxValue }}" value="{{ characteristic.value }}">
        {% elif characteristic.type == 'ColorTemperature' %}
            <label for="colortemperature-{{ device.uniqueId }}" class="form-label mt-2">Color Temperature</label>
            <input type="range" class="form-range" id="colortemperature-{{ device.uniqueId }}" min="{{ characteristic.minValue }}" max="{{ characteristic.maxValue }}" value="{{ characteristic.value }}">
        {% endif %}
    {% endfor %}
</div>
''',

            'Switch.html': '''
<div class="device switch mb-4" id="device-{{ device.uniqueId }}">
    <h3>{{ device.serviceName }}</h3>
    <div class="form-check form-switch">
        {% for characteristic in device.characteristics %}
            {% if characteristic.type == 'On' %}
                <input class="form-check-input" type="checkbox" id="on-{{ device.uniqueId }}" {% if characteristic.value %}checked{% endif %}>
                <label class="form-check-label" for="on-{{ device.uniqueId }}">On</label>
            {% endif %}
        {% endfor %}
    </div>
</div>
''',

            'GarageDoorOpener.html': '''
{% set state_mapping = {
    0: 'Open',
    1: 'Closed',
    2: 'Opening',
    3: 'Closing',
    4: 'Stopped'
} %}
<div class="device garagedooropener mb-4" id="device-{{ device.uniqueId }}">
    <h3>{{ device.serviceName }}</h3>
    <div class="btn-group mb-2" role="group" aria-label="Garage Door Controls">
        <button type="button" class="btn btn-secondary" id="open-{{ device.uniqueId }}">Open</button>
        <button type="button" class="btn btn-secondary" id="close-{{ device.uniqueId }}">Close</button>
    </div>
    <p>Current State: <span id="state-{{ device.uniqueId }}">{{ state_mapping[device.values['CurrentDoorState']] }}</span></p>
</div>
'''
        }
    },

    'static': {
        'css': {
            'style.css': '''
body {
    background-color: #121212;
    color: #ffffff;
}

a {
    color: #ffffff;
}

.device {
    padding: 15px;
    border: 1px solid #333;
    border-radius: 5px;
}

.form-check-input {
    cursor: pointer;
}

.form-range {
    width: 100%;
}

.btn-secondary {
    background-color: #333;
    border-color: #333;
}

.btn-secondary:hover {
    background-color: #444;
    border-color: #444;
}
'''
        },

        'js': {
            'core.js': '''
var pollingIntervals = {};

function getDeviceState(uniqueId, callback) {
    $.ajax({
        url: '/api/device/' + uniqueId,
        method: 'GET',
        success: function(data) {
            callback(data);
        },
        error: function(err) {
            console.error('Error getting device state:', err);
        }
    });
}

function updateDevice(uniqueId, data, callback) {
    $.ajax({
        url: '/api/device/' + uniqueId,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function(response) {
            if (callback) callback(response);
        },
        error: function(err) {
            console.error('Error updating device:', err);
        }
    });
}

function startPolling(uniqueId, interval, callback) {
    if (pollingIntervals[uniqueId]) {
        clearInterval(pollingIntervals[uniqueId]);
    }
    pollingIntervals[uniqueId] = setInterval(function() {
        getDeviceState(uniqueId, callback);
    }, interval);
}

function stopPolling(uniqueId) {
    if (pollingIntervals[uniqueId]) {
        clearInterval(pollingIntervals[uniqueId]);
        delete pollingIntervals[uniqueId];
    }
}
''',

            'devices': {
                'Lightbulb.js': '''
$(document).ready(function() {
    $('.device.lightbulb').each(function() {
        var uniqueId = $(this).attr('id').replace('device-', '');
        var $device = $(this);

        // Event handlers
        var $onSwitch = $device.find('#on-' + uniqueId);
        $onSwitch.change(function() {
            var isOn = $(this).is(':checked') ? 1 : 0;
            updateDevice(uniqueId, { 'On': isOn });
        });

        var $brightnessSlider = $device.find('#brightness-' + uniqueId);
        $brightnessSlider.on('input change', function() {
            var brightness = parseInt($(this).val());
            updateDevice(uniqueId, { 'Brightness': brightness });
        });

        var $hueSlider = $device.find('#hue-' + uniqueId);
        $hueSlider.on('input change', function() {
            var hue = parseFloat($(this).val());
            updateDevice(uniqueId, { 'Hue': hue });
        });

        var $saturationSlider = $device.find('#saturation-' + uniqueId);
        $saturationSlider.on('input change', function() {
            var saturation = parseFloat($(this).val());
            updateDevice(uniqueId, { 'Saturation': saturation });
        });

        var $colorTempSlider = $device.find('#colortemperature-' + uniqueId);
        $colorTempSlider.on('input change', function() {
            var colorTemp = parseInt($(this).val());
            updateDevice(uniqueId, { 'ColorTemperature': colorTemp });
        });

        // Polling
        startPolling(uniqueId, 5000, function(data) {
            // Update UI with the latest values
            data = data.values;
            if (data['On'] !== undefined) {
                $onSwitch.prop('checked', data['On'] ? true : false);
            }
            if (data['Brightness'] !== undefined) {
                $brightnessSlider.val(data['Brightness']);
            }
            if (data['Hue'] !== undefined) {
                $hueSlider.val(data['Hue']);
            }
            if (data['Saturation'] !== undefined) {
                $saturationSlider.val(data['Saturation']);
            }
            if (data['ColorTemperature'] !== undefined) {
                $colorTempSlider.val(data['ColorTemperature']);
            }
        });
    });
});
''',

                'Switch.js': '''
$(document).ready(function() {
    $('.device.switch').each(function() {
        var uniqueId = $(this).attr('id').replace('device-', '');
        var $device = $(this);

        // Event handlers
        var $onSwitch = $device.find('#on-' + uniqueId);
        $onSwitch.change(function() {
            var isOn = $(this).is(':checked') ? 1 : 0;
            updateDevice(uniqueId, { 'On': isOn });
        });

        // Polling
        startPolling(uniqueId, 5000, function(data) {
            // Update UI with the latest values
            data = data.values;
            if (data['On'] !== undefined) {
                $onSwitch.prop('checked', data['On'] ? true : false);
            }
        });
    });
});
''',

                'GarageDoorOpener.js': '''
$(document).ready(function() {
    $('.device.garagedooropener').each(function() {
        var uniqueId = $(this).attr('id').replace('device-', '');
        var $device = $(this);

        var $openButton = $device.find('#open-' + uniqueId);
        var $closeButton = $device.find('#close-' + uniqueId);
        var $stateSpan = $device.find('#state-' + uniqueId);

        $openButton.click(function() {
            updateDevice(uniqueId, { 'TargetDoorState': 0 });
        });

        $closeButton.click(function() {
            updateDevice(uniqueId, { 'TargetDoorState': 1 });
        });

        var stateMapping = {
            0: 'Open',
            1: 'Closed',
            2: 'Opening',
            3: 'Closing',
            4: 'Stopped'
        };

        // Polling
        startPolling(uniqueId, 5000, function(data) {
            // Update UI with the latest values
            data = data.values;
            if (data['CurrentDoorState'] !== undefined) {
                $stateSpan.text(stateMapping[data['CurrentDoorState']]);
            }
        });
    });
});
'''
            }
        }
    }
}

def create_project_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            # It's a directory
            os.makedirs(path, exist_ok=True)
            create_project_structure(path, content)
        else:
            # It's a file
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content.strip('\n'))

if __name__ == '__main__':
    base_path = os.path.join(os.getcwd(), '')
    create_project_structure(base_path, project_structure)
    print(f"Project generated at {base_path}")
