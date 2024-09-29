import os

def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

# Base project directory
base_dir = os.getcwd()

# 1. Write app.py
app_py_content = """
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
        # room_devices = []
        # for service in room.services:
        #     device = hbc.get_accessory(service.uniqueId)
        #     room_devices.append(device.get_summary())
        # room_dict['devices'] = room_devices
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
"""
write_file(os.path.join(base_dir, 'app.py'), app_py_content)

# 2. Create templates directory and subdirectories
templates_dir = os.path.join(base_dir, 'templates')
os.makedirs(templates_dir, exist_ok=True)

# Create devices templates directory
devices_templates_dir = os.path.join(templates_dir, 'devices')
os.makedirs(devices_templates_dir, exist_ok=True)

# 3. Create static directory and subdirectories
static_dir = os.path.join(base_dir, 'static')
os.makedirs(static_dir, exist_ok=True)

# Create js directories
static_js_dir = os.path.join(static_dir, 'js')
os.makedirs(static_js_dir, exist_ok=True)

devices_js_dir = os.path.join(static_js_dir, 'devices')
os.makedirs(devices_js_dir, exist_ok=True)

# Create css directory (if needed)
static_css_dir = os.path.join(static_dir, 'css')
os.makedirs(static_css_dir, exist_ok=True)

# Now, create the templates

# base.html
base_html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Smart Home Device Manager</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css">
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
</head>
<body class="bg-dark">
    {% block content %}{% endblock %}
    <!-- jQuery and Bootstrap JS -->
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <!-- Core JS -->
    <script src="{{ url_for('static', filename='js/core.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
"""
write_file(os.path.join(templates_dir, 'base.html'), base_html_content)

# index.html
index_html_content = """
{% extends 'base.html' %}

{% block content %}
<div class="container mt-4">
    <h1 class="text-center text-white">Rooms</h1>
    <div class="list-group">
        <!-- Rooms will be loaded here -->
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    $(document).ready(function() {
        $.getJSON('/api/rooms', function(rooms) {
            var listGroup = $('.list-group');
            listGroup.empty();
            $.each(rooms, function(index, room) {
                var roomLink = $('<a></a>')
                    .addClass('list-group-item list-group-item-action bg-dark text-white')
                    .attr('href', '/room/' + encodeURIComponent(room.name))
                    .text(room.name);
                listGroup.append(roomLink);
            });
        });
    });
</script>
{% endblock %}
"""
write_file(os.path.join(templates_dir, 'index.html'), index_html_content)

# room.html
room_html_content = """
{% extends 'base.html' %}

{% block content %}
<div class="container mt-4">
    <h1 class="text-center text-white">{{ room_name }}</h1>
    <div id="devices-container">
        <!-- Devices will be loaded here -->
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    $(document).ready(function() {
        var roomName = "{{ room_name }}";
        function loadDevices() {
            $.getJSON('/api/rooms/' + encodeURIComponent(roomName) + '/devices', function(devices) {
                var container = $('#devices-container');
                container.empty();
                $.each(devices, function(index, device) {
                    var deviceType = device.type;
                    // Load the device template
                    var deviceDiv = $('<div></div>');
                    deviceDiv.load('/devices/' + deviceType + '.html', function() {
                        // Render the template with device data
                        var rendered = Mustache.render(deviceDiv.html(), { device: device });
                        deviceDiv.html(rendered);
                        // Initialize the device
                        initDevice(deviceDiv, device);
                        container.append(deviceDiv);
                    });
                });
            });
        }

        loadDevices();

        // Poll device states every 5 seconds
        setInterval(loadDevices, 5000);
    });
</script>
{% endblock %}
"""
write_file(os.path.join(templates_dir, 'room.html'), room_html_content)

# devices templates
# Lightbulb.html
lightbulb_html_content = """
<div class="card bg-secondary text-white mb-3">
    <div class="card-header">{{ device.serviceName }}</div>
    <div class="card-body">
        <div class="form-group">
            <label>On/Off</label>
            <input type="checkbox" class="toggle-on-off" {{#device.values.On}}checked{{/device.values.On}}>
        </div>
        {{#device.values.Brightness}}
        <div class="form-group">
            <label>Brightness</label>
            <input type="range" class="form-control-range brightness-slider" min="0" max="100" value="{{ device.values.Brightness }}">
        </div>
        {{/device.values.Brightness}}
        {{#device.values.Hue}}
        <div class="form-group">
            <label>Color</label>
            <input type="color" class="form-control color-picker">
        </div>
        {{/device.values.Hue}}
        {{#device.values.ColorTemperature}}
        <div class="form-group">
            <label>Color Temperature</label>
            <input type="range" class="form-control-range color-temp-slider" min="140" max="500" value="{{ device.values.ColorTemperature }}">
        </div>
        {{/device.values.ColorTemperature}}
    </div>
</div>
"""
write_file(os.path.join(devices_templates_dir, 'Lightbulb.html'), lightbulb_html_content)

# Switch.html
switch_html_content = """
<div class="card bg-secondary text-white mb-3">
    <div class="card-header">{{ device.serviceName }}</div>
    <div class="card-body">
        <div class="form-group">
            <label>On/Off</label>
            <input type="checkbox" class="toggle-on-off" {{#device.values.On}}checked{{/device.values.On}}>
        </div>
    </div>
</div>
"""
write_file(os.path.join(devices_templates_dir, 'Switch.html'), switch_html_content)

# GarageDoorOpener.html
garage_door_opener_html_content = """
<div class="card bg-secondary text-white mb-3">
    <div class="card-header">{{ device.serviceName }}</div>
    <div class="card-body">
        <div class="form-group">
            <label>Door State</label>
            <select class="form-control target-door-state">
                <option value="0" {{#if_eq device.values.TargetDoorState 0}}selected{{/if_eq}}>Open</option>
                <option value="1" {{#if_eq device.values.TargetDoorState 1}}selected{{/if_eq}}>Closed</option>
            </select>
        </div>
        <p>Current State: {{ device.values.CurrentDoorState }}</p>
        {{#if device.values.ObstructionDetected}}
        <p class="text-danger">Obstruction Detected!</p>
        {{/if}}
    </div>
</div>
"""
write_file(os.path.join(devices_templates_dir, 'GarageDoorOpener.html'), garage_door_opener_html_content)

# Now, create the JS files

# core.js
core_js_content = """
function initDevice(deviceElement, deviceData) {
    var deviceType = deviceData.type;
    if (deviceType === 'Lightbulb') {
        initLightbulb(deviceElement, deviceData);
    } else if (deviceType === 'Switch') {
        initSwitch(deviceElement, deviceData);
    } else if (deviceType === 'GarageDoorOpener') {
        initGarageDoorOpener(deviceElement, deviceData);
    }
}
"""
write_file(os.path.join(static_js_dir, 'core.js'), core_js_content)

# devices JavaScript files

# Lightbulb.js
lightbulb_js_content = """
function initLightbulb(element, device) {
    var uniqueId = device.uniqueId;
    var toggle = element.find('.toggle-on-off');
    toggle.change(function() {
        var isOn = $(this).is(':checked') ? 1 : 0;
        $.ajax({
            url: '/api/device/' + uniqueId,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'On': isOn })
        });
    });
    var brightnessSlider = element.find('.brightness-slider');
    brightnessSlider.change(function() {
        var brightness = $(this).val();
        $.ajax({
            url: '/api/device/' + uniqueId,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'Brightness': parseInt(brightness) })
        });
    });
    var colorPicker = element.find('.color-picker');
    colorPicker.change(function() {
        var color = $(this).val();
        var rgb = hexToRgb(color);
        var hsv = rgbToHsv(rgb.r, rgb.g, rgb.b);
        $.ajax({
            url: '/api/device/' + uniqueId,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                'Hue': parseInt(hsv.h * 360),
                'Saturation': parseInt(hsv.s * 100)
            })
        });
    });
    var colorTempSlider = element.find('.color-temp-slider');
    colorTempSlider.change(function() {
        var temp = $(this).val();
        $.ajax({
            url: '/api/device/' + uniqueId,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'ColorTemperature': parseInt(temp) })
        });
    });
}

function hexToRgb(hex) {
    var bigint = parseInt(hex.replace('#', ''), 16);
    var r = (bigint >> 16) & 255;
    var g = (bigint >> 8) & 255;
    var b = bigint & 255;
    return { r: r, g: g, b: b };
}

function rgbToHsv(r, g, b) {
    r /= 255; g /= 255; b /= 255;
    var max = Math.max(r, g, b), min = Math.min(r, g, b);
    var h, s, v = max;
    var d = max - min;
    s = max == 0 ? 0 : d / max;
    if (max == min) {
        h = 0; // achromatic
    } else {
        switch (max) {
            case r: h = (g - b) / d + (g < b ? 6 : 0); break;
            case g: h = (b - r) / d + 2; break;
            case b: h = (r - g) / d + 4; break;
        }
        h /= 6;
    }
    return { h: h, s: s, v: v };
}
"""
write_file(os.path.join(devices_js_dir, 'Lightbulb.js'), lightbulb_js_content)

# Switch.js
switch_js_content = """
function initSwitch(element, device) {
    var uniqueId = device.uniqueId;
    var toggle = element.find('.toggle-on-off');
    toggle.change(function() {
        var isOn = $(this).is(':checked') ? 1 : 0;
        $.ajax({
            url: '/api/device/' + uniqueId,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'On': isOn })
        });
    });
}
"""
write_file(os.path.join(devices_js_dir, 'Switch.js'), switch_js_content)

# GarageDoorOpener.js
garage_door_opener_js_content = """
function initGarageDoorOpener(element, device) {
    var uniqueId = device.uniqueId;
    var select = element.find('.target-door-state');
    select.change(function() {
        var state = $(this).val();
        $.ajax({
            url: '/api/device/' + uniqueId,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'TargetDoorState': parseInt(state) })
        });
    });
}
"""
write_file(os.path.join(devices_js_dir, 'GarageDoorOpener.js'), garage_door_opener_js_content)

# Optional: Add styles.css for custom styles
styles_css_content = """
body {
    background-color: #121212;
    color: #ffffff;
}

.card {
    background-color: #1e1e1e;
}

"""
write_file(os.path.join(static_css_dir, 'styles.css'), styles_css_content)
