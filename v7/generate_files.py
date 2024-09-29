import os

# Create necessary directories
os.makedirs('templates/devices', exist_ok=True)
os.makedirs('static/js/devices', exist_ok=True)
os.makedirs('static/css', exist_ok=True)

# Content for app.py
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
    os.makedirs(os.path.dirname(PREFERENCES_FILE), exist_ok=True)
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
                devices.append(device)
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

# Write app.py
with open('app.py', 'w') as f:
    f.write(app_py_content)

# Content for templates/index.html
index_html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Smart Home Manager</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- CSS and JS imports -->
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body class="bg-dark text-white">
    <div class="container">
        <h1 class="mt-4">Welcome to Your Smart Home</h1>
        <div class="list-group mt-4">
            {% for room in rooms %}
            <a href="{{ url_for('room', room_name=room.name) }}" class="list-group-item list-group-item-action bg-dark text-white">
                {{ room.name }}
            </a>
            {% endfor %}
        </div>
    </div>
    <!-- jQuery and Bootstrap JS -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# Write index.html
with open('templates/index.html', 'w') as f:
    f.write(index_html_content)

# Content for templates/room.html
room_html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ room_name }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- CSS and JS imports -->
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body class="bg-dark text-white">
    <div class="container">
        <h1 class="mt-4">{{ room_name }}</h1>
        <div class="device-list mt-4">
            {% for device in devices %}
                {% set device_type = device.type %}
                {% include 'devices/' + device_type + '.html' %}
            {% endfor %}
        </div>
    </div>
    <!-- jQuery and Bootstrap JS -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Core JS -->
    <script src="{{ url_for('static', filename='js/core.js') }}"></script>
    <script>
        $(document).ready(function() {
            {% for device in devices %}
                loadDevice('{{ device.uniqueId }}', '{{ device.type }}');
            {% endfor %}
        });
    </script>
</body>
</html>
"""

# Write room.html
with open('templates/room.html', 'w') as f:
    f.write(room_html_content)

# Content for templates/devices/<deviceType>.html
device_types = ['Lightbulb', 'GarageDoorOpener', 'Switch']

lightbulb_template = """
<div class="device mb-3" id="device-{{ device.uniqueId }}">
    <div class="card bg-secondary text-white">
        <div class="card-body">
            <h5 class="card-title">{{ device.serviceName }}</h5>
            <div id="controls-{{ device.uniqueId }}">
                <!-- Controls will be loaded here -->
            </div>
        </div>
    </div>
</div>
"""

garagedooropener_template = """
<div class="device mb-3" id="device-{{ device.uniqueId }}">
    <div class="card bg-secondary text-white">
        <div class="card-body">
            <h5 class="card-title">{{ device.serviceName }}</h5>
            <div id="controls-{{ device.uniqueId }}">
                <!-- Controls will be loaded here -->
            </div>
        </div>
    </div>
</div>
"""

switch_template = """
<div class="device mb-3" id="device-{{ device.uniqueId }}">
    <div class="card bg-secondary text-white">
        <div class="card-body">
            <h5 class="card-title">{{ device.serviceName }}</h5>
            <div id="controls-{{ device.uniqueId }}">
                <!-- Controls will be loaded here -->
            </div>
        </div>
    </div>
</div>
"""

device_templates = {
    'Lightbulb': lightbulb_template,
    'GarageDoorOpener': garagedooropener_template,
    'Switch': switch_template
}

for device_type in device_types:
    with open(f'templates/devices/{device_type}.html', 'w') as f:
        f.write(device_templates.get(device_type, ''))

# Content for static/js/core.js
core_js_content = """
function loadDevice(uniqueId, deviceType) {
    $.get('/api/device/' + uniqueId, function(data) {
        var controlsDiv = $('#controls-' + uniqueId);
        $.getScript('/static/js/devices/' + deviceType + '.js', function() {
            initDeviceControls(data, controlsDiv);
        });
    });
}
"""

with open('static/js/core.js', 'w') as f:
    f.write(core_js_content)

# Content for static/js/devices/Lightbulb.js
lightbulb_js_content = """
function initDeviceControls(data, controlsDiv) {
    var onCharacteristic = data.values['On'];
    var brightnessCharacteristic = data.values['Brightness'];
    var hueCharacteristic = data.values['Hue'];
    var saturationCharacteristic = data.values['Saturation'];

    var switchHtml = '<div class="form-check form-switch">' +
        '<input class="form-check-input" type="checkbox" id="switch-' + data.uniqueId + '"' +
        (onCharacteristic ? ' checked' : '') + '>' +
        '<label class="form-check-label" for="switch-' + data.uniqueId + '">On/Off</label>' +
        '</div>';

    var brightnessHtml = '';
    if (brightnessCharacteristic !== undefined) {
        brightnessHtml = '<label for="brightness-' + data.uniqueId + '" class="form-label">Brightness</label>' +
            '<input type="range" class="form-range" id="brightness-' + data.uniqueId + '" min="0" max="100" value="' + brightnessCharacteristic + '">';
    }

    var colorHtml = '';
    if (hueCharacteristic !== undefined && saturationCharacteristic !== undefined) {
        colorHtml = '<label for="color-' + data.uniqueId + '" class="form-label">Color</label>' +
            '<input type="color" class="form-control form-control-color" id="color-' + data.uniqueId + '" value="' + hslToHex(hueCharacteristic, saturationCharacteristic, 50) + '" title="Choose your color">';
    }

    controlsDiv.html(switchHtml + brightnessHtml + colorHtml);

    $('#switch-' + data.uniqueId).change(function() {
        var newValue = $(this).is(':checked') ? 1 : 0;
        updateDevice(data.uniqueId, {'On': newValue});
    });

    $('#brightness-' + data.uniqueId).on('input change', function() {
        var newValue = parseInt($(this).val());
        updateDevice(data.uniqueId, {'Brightness': newValue});
    });

    $('#color-' + data.uniqueId).change(function() {
        var hexColor = $(this).val();
        var hsl = hexToHSL(hexColor);
        updateDevice(data.uniqueId, {'Hue': hsl.h, 'Saturation': hsl.s});
    });
}

function updateDevice(uniqueId, characteristics) {
    $.ajax({
        url: '/api/device/' + uniqueId,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(characteristics),
        success: function(response) {
            console.log('Device updated', response);
        }
    });
}

function hslToHex(h, s, l){
    s /= 100;
    l /= 100;

    let c = (1 - Math.abs(2 * l - 1)) * s,
        x = c * (1 - Math.abs((h / 60) % 2 - 1)),
        m = l - c/2,
        r = 0,
        g = 0,
        b = 0;

    if (0 <= h && h < 60) {
        r = c; g = x; b = 0;  
    } else if (60 <= h && h < 120) {
        r = x; g = c; b = 0;  
    } else if (120 <= h && h < 180) {
        r = 0; g = c; b = x;  
    } else if (180 <= h && h < 240) {
        r = 0; g = x; b = c;  
    } else if (240 <= h && h < 300) {
        r = x; g = 0; b = c;  
    } else if (300 <= h && h < 360) {
        r = c; g = 0; b = x;  
    }
    r = Math.round((r + m) * 255);
    g = Math.round((g + m) * 255);
    b = Math.round((b + m) * 255);

    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}

function hexToHSL(H) {
    let r = 0, g = 0, b = 0;
    if (H.length == 4) {
        r = "0x" + H[1] + H[1];
        g = "0x" + H[2] + H[2];
        b = "0x" + H[3] + H[3];
    } else if (H.length == 7) {
        r = "0x" + H[1] + H[2];
        g = "0x" + H[3] + H[4];
        b = "0x" + H[5] + H[6];
    }
    r /= 255;
    g /= 255;
    b /= 255;
    let cmin = Math.min(r,g,b),
        cmax = Math.max(r,g,b),
        delta = cmax - cmin,
        h = 0,
        s = 0,
        l = 0;
    if (delta == 0)
        h = 0;
    else if (cmax == r)
        h = ((g - b) / delta) % 6;
    else if (cmax == g)
        h = (b - r) / delta + 2;
    else
        h = (r - g) / delta + 4;
    h = Math.round(h * 60);
    if (h < 0)
        h += 360;
    l = (cmax + cmin) / 2;
    s = delta == 0 ? 0 : delta / (1 - Math.abs(2 * l - 1));
    s = +(s * 100).toFixed(1);
    l = +(l * 100).toFixed(1);
    return {h: h, s: s, l: l};
}
"""

with open('static/js/devices/Lightbulb.js', 'w') as f:
    f.write(lightbulb_js_content)

# Content for static/js/devices/GarageDoorOpener.js
garagedooropener_js_content = """
function initDeviceControls(data, controlsDiv) {
    var targetDoorState = data.values['TargetDoorState'];
    var currentDoorState = data.values['CurrentDoorState'];
    var obstructionDetected = data.values['ObstructionDetected'];

    var doorStateHtml = '<label for="doorstate-' + data.uniqueId + '" class="form-label">Door State</label>' +
        '<select class="form-select" id="doorstate-' + data.uniqueId + '">' +
        '<option value="0"' + (targetDoorState == 0 ? ' selected' : '') + '>Open</option>' +
        '<option value="1"' + (targetDoorState == 1 ? ' selected' : '') + '>Closed</option>' +
        '</select>';

    controlsDiv.html(doorStateHtml);

    $('#doorstate-' + data.uniqueId).change(function() {
        var newValue = parseInt($(this).val());
        updateDevice(data.uniqueId, {'TargetDoorState': newValue});
    });
}

function updateDevice(uniqueId, characteristics) {
    $.ajax({
        url: '/api/device/' + uniqueId,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(characteristics),
        success: function(response) {
            console.log('Device updated', response);
        }
    });
}
"""

with open('static/js/devices/GarageDoorOpener.js', 'w') as f:
    f.write(garagedooropener_js_content)

# Content for static/js/devices/Switch.js
switch_js_content = """
function initDeviceControls(data, controlsDiv) {
    var onCharacteristic = data.values['On'];

    var switchHtml = '<div class="form-check form-switch">' +
        '<input class="form-check-input" type="checkbox" id="switch-' + data.uniqueId + '"' +
        (onCharacteristic ? ' checked' : '') + '>' +
        '<label class="form-check-label" for="switch-' + data.uniqueId + '">On/Off</label>' +
        '</div>';

    controlsDiv.html(switchHtml);

    $('#switch-' + data.uniqueId).change(function() {
        var newValue = $(this).is(':checked') ? 1 : 0;
        updateDevice(data.uniqueId, {'On': newValue});
    });
}

function updateDevice(uniqueId, characteristics) {
    $.ajax({
        url: '/api/device/' + uniqueId,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(characteristics),
        success: function(response) {
            console.log('Device updated', response);
        }
    });
}
"""

with open('static/js/devices/Switch.js', 'w') as f:
    f.write(switch_js_content)

# Content for static/css/style.css
style_css_content = """
body {
    background-color: #121212;
    color: #ffffff;
}
.card {
    background-color: #1e1e1e;
}
.form-control, .form-select {
    background-color: #1e1e1e;
    color: #ffffff;
}
.form-range {
    accent-color: #007bff;
}
.form-check-input {
    background-color: #1e1e1e;
    border-color: #6c757d;
}
"""

with open('static/css/style.css', 'w') as f:
    f.write(style_css_content)
