import os

# Base directory
BASE_DIR = os.getcwd()

# Content for app.py
app_py_content = '''from flask import Flask, jsonify, render_template, request, redirect, url_for
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
    return render_template('index.html', preferences=preferences)

@app.route('/room/<room_name>')
def room(room_name):
    preferences = load_preferences()
    return render_template('room.html', room_name=room_name, preferences=preferences)

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
'''

# Content for templates/index.html
index_html_content = '''{% extends "layout.html" %}
{% block content %}
<div class="container">
    <h2 class="mt-4">Rooms</h2>
    <div id="rooms-list" class="list-group">
        <!-- Rooms will be loaded here -->
    </div>
</div>
<script src="{{ url_for('static', filename='js/index.js') }}"></script>
{% endblock %}
'''

# Content for templates/layout.html
layout_html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Smart Home Manager</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <!-- Dark theme -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    {% block content %}{% endblock %}
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <!-- Bootstrap JS and Popper.js -->
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    <!-- Core JS -->
    <script src="{{ url_for('static', filename='js/core.js') }}"></script>
</body>
</html>
'''

# Content for templates/room.html
room_html_content = '''{% extends "layout.html" %}
{% block content %}
<div class="container">
    <h2 class="mt-4">{{ room_name }}</h2>
    <div id="devices-list">
        <!-- Devices will be loaded here -->
    </div>
</div>
<script>
    var roomName = "{{ room_name }}";
</script>
<script src="{{ url_for('static', filename='js/room.js') }}"></script>
{% endblock %}
'''

# Content for templates/devices/Lightbulb.html
lightbulb_html_content = '''<div class="device card mb-3" data-unique-id="{{ device.uniqueId }}">
    <div class="card-body">
        <h5 class="card-title">{{ device.serviceName }}</h5>
        <div class="form-group">
            <label>On/Off</label>
            <input type="checkbox" class="toggle-on-off" {% if device.values.On %}checked{% endif %}>
        </div>
        {% if device.values.Brightness is not none %}
        <div class="form-group">
            <label>Brightness</label>
            <input type="range" class="brightness-slider" min="0" max="100" value="{{ device.values.Brightness }}">
        </div>
        {% endif %}
        {% if device.values.Hue is not none %}
        <div class="form-group">
            <label>Hue</label>
            <input type="range" class="hue-slider" min="0" max="360" value="{{ device.values.Hue }}">
        </div>
        {% endif %}
        {% if device.values.Saturation is not none %}
        <div class="form-group">
            <label>Saturation</label>
            <input type="range" class="saturation-slider" min="0" max="100" value="{{ device.values.Saturation }}">
        </div>
        {% endif %}
        {% if device.values.ColorTemperature is not none %}
        <div class="form-group">
            <label>Color Temperature</label>
            <input type="range" class="color-temperature-slider" min="140" max="500" value="{{ device.values.ColorTemperature }}">
        </div>
        {% endif %}
    </div>
</div>
'''

# Content for templates/devices/GarageDoorOpener.html
garagedooropener_html_content = '''<div class="device card mb-3" data-unique-id="{{ device.uniqueId }}">
    <div class="card-body">
        <h5 class="card-title">{{ device.serviceName }}</h5>
        <p>Current Door State: <span class="current-door-state">{{ device.values.CurrentDoorState }}</span></p>
        <div class="form-group">
            <label>Target Door State</label>
            <select class="form-control target-door-state">
                <option value="0" {% if device.values.TargetDoorState == 0 %}selected{% endif %}>Open</option>
                <option value="1" {% if device.values.TargetDoorState == 1 %}selected{% endif %}>Closed</option>
            </select>
        </div>
    </div>
</div>
'''

# Content for templates/devices/Switch.html
switch_html_content = '''<div class="device card mb-3" data-unique-id="{{ device.uniqueId }}">
    <div class="card-body">
        <h5 class="card-title">{{ device.serviceName }}</h5>
        <div class="form-group">
            <label>On/Off</label>
            <input type="checkbox" class="toggle-on-off" {% if device.values.On %}checked{% endif %}>
        </div>
    </div>
</div>
'''

# Content for static/css/style.css
style_css_content = '''body {
    background-color: #121212;
    color: #ffffff;
}

.card {
    background-color: #1e1e1e;
    border: none;
}

.card-title {
    color: #ffffff;
}

.container {
    margin-top: 20px;
}

.list-group-item {
    background-color: #1e1e1e;
    color: #ffffff;
    border: none;
}

.list-group-item:hover {
    background-color: #2a2a2a;
}

.navbar {
    background-color: #1e1e1e;
}

.nav-link {
    color: #ffffff !important;
}
'''

# Content for static/js/core.js
core_js_content = '''function getDeviceTypeTemplate(deviceType) {
    return '/templates/devices/' + deviceType + '.html';
}

function pollDeviceState(uniqueId, callback) {
    $.get('/api/device/' + uniqueId, function(data) {
        callback(data);
    });
}

function updateDevice(uniqueId, data, callback) {
    $.ajax({
        url: '/api/device/' + uniqueId,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function(response) {
            callback(response);
        }
    });
}
'''

# Content for static/js/index.js
index_js_content = '''$(document).ready(function() {
    $.get('/api/rooms', function(data) {
        var roomsList = $('#rooms-list');
        data.forEach(function(room) {
            var roomItem = $('<a href="/room/' + encodeURIComponent(room.name) + '" class="list-group-item list-group-item-action">' + room.name + '</a>');
            roomsList.append(roomItem);
        });
    });
});
'''

# Content for static/js/room.js
room_js_content = '''$(document).ready(function() {
    function loadDevices() {
        $.get('/api/rooms/' + encodeURIComponent(roomName) + '/devices', function(data) {
            var devicesList = $('#devices-list');
            devicesList.empty();
            data.forEach(function(device) {
                var deviceType = device.type;
                $.get('/static/js/devices/' + deviceType + '.js', function() {
                    $.get('/templates/devices/' + deviceType + '.html', function(template) {
                        var rendered = Mustache.render(template, { device: device });
                        devicesList.append(rendered);
                        // Initialize device handlers
                        if (typeof window['init' + deviceType] === 'function') {
                            window['init' + deviceType](device);
                        }
                    });
                });
            });
        });
    }

    loadDevices();
    setInterval(loadDevices, 5000); // Poll every 5 seconds
});
'''

# Content for static/js/devices/Lightbulb.js
lightbulb_js_content = '''function initLightbulb(device) {
    var deviceElement = $('[data-unique-id="' + device.uniqueId + '"]');

    function pollState() {
        pollDeviceState(device.uniqueId, function(data) {
            deviceElement.find('.toggle-on-off').prop('checked', data.values.On);
            deviceElement.find('.brightness-slider').val(data.values.Brightness);
            deviceElement.find('.hue-slider').val(data.values.Hue);
            deviceElement.find('.saturation-slider').val(data.values.Saturation);
            deviceElement.find('.color-temperature-slider').val(data.values.ColorTemperature);
        });
    }

    deviceElement.find('.toggle-on-off').change(function() {
        var isOn = $(this).is(':checked') ? 1 : 0;
        updateDevice(device.uniqueId, { 'On': isOn }, pollState);
    });

    deviceElement.find('.brightness-slider').change(function() {
        var brightness = parseInt($(this).val());
        updateDevice(device.uniqueId, { 'Brightness': brightness }, pollState);
    });

    deviceElement.find('.hue-slider').change(function() {
        var hue = parseFloat($(this).val());
        updateDevice(device.uniqueId, { 'Hue': hue }, pollState);
    });

    deviceElement.find('.saturation-slider').change(function() {
        var saturation = parseFloat($(this).val());
        updateDevice(device.uniqueId, { 'Saturation': saturation }, pollState);
    });

    deviceElement.find('.color-temperature-slider').change(function() {
        var colorTemperature = parseInt($(this).val());
        updateDevice(device.uniqueId, { 'ColorTemperature': colorTemperature }, pollState);
    });

    setInterval(pollState, 5000); // Poll every 5 seconds
}
'''

# Content for static/js/devices/GarageDoorOpener.js
garagedooropener_js_content = '''function initGarageDoorOpener(device) {
    var deviceElement = $('[data-unique-id="' + device.uniqueId + '"]');

    function pollState() {
        pollDeviceState(device.uniqueId, function(data) {
            deviceElement.find('.current-door-state').text(data.values.CurrentDoorState);
            deviceElement.find('.target-door-state').val(data.values.TargetDoorState);
        });
    }

    deviceElement.find('.target-door-state').change(function() {
        var targetState = parseInt($(this).val());
        updateDevice(device.uniqueId, { 'TargetDoorState': targetState }, pollState);
    });

    setInterval(pollState, 5000); // Poll every 5 seconds
}
'''

# Content for static/js/devices/Switch.js
switch_js_content = '''function initSwitch(device) {
    var deviceElement = $('[data-unique-id="' + device.uniqueId + '"]');

    function pollState() {
        pollDeviceState(device.uniqueId, function(data) {
            deviceElement.find('.toggle-on-off').prop('checked', data.values.On);
        });
    }

    deviceElement.find('.toggle-on-off').change(function() {
        var isOn = $(this).is(':checked') ? 1 : 0;
        updateDevice(device.uniqueId, { 'On': isOn }, pollState);
    });

    setInterval(pollState, 5000); // Poll every 5 seconds
}
'''

# Function to create directories and files
def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

# Create app.py
create_file(os.path.join(BASE_DIR, 'app.py'), app_py_content)

# Create templates
create_file(os.path.join(BASE_DIR, 'templates', 'layout.html'), layout_html_content)
create_file(os.path.join(BASE_DIR, 'templates', 'index.html'), index_html_content)
create_file(os.path.join(BASE_DIR, 'templates', 'room.html'), room_html_content)

# Create device templates
create_file(os.path.join(BASE_DIR, 'templates', 'devices', 'Lightbulb.html'), lightbulb_html_content)
create_file(os.path.join(BASE_DIR, 'templates', 'devices', 'GarageDoorOpener.html'), garagedooropener_html_content)
create_file(os.path.join(BASE_DIR, 'templates', 'devices', 'Switch.html'), switch_html_content)

# Create static files
create_file(os.path.join(BASE_DIR, 'static', 'css', 'style.css'), style_css_content)
create_file(os.path.join(BASE_DIR, 'static', 'js', 'core.js'), core_js_content)
create_file(os.path.join(BASE_DIR, 'static', 'js', 'index.js'), index_js_content)
create_file(os.path.join(BASE_DIR, 'static', 'js', 'room.js'), room_js_content)

# Create device JavaScript files
create_file(os.path.join(BASE_DIR, 'static', 'js', 'devices', 'Lightbulb.js'), lightbulb_js_content)
create_file(os.path.join(BASE_DIR, 'static', 'js', 'devices', 'GarageDoorOpener.js'), garagedooropener_js_content)
create_file(os.path.join(BASE_DIR, 'static', 'js', 'devices', 'Switch.js'), switch_js_content)

print("All files have been generated successfully.")
