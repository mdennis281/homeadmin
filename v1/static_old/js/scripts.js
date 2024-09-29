$(document).ready(function() {
    // Existing functions remain unchanged unless specified

    // Function to load rooms on the index page
    function loadRooms() {
        $.getJSON('/api/rooms', function(rooms) {
            $('#rooms-container').empty();
            rooms.forEach(function(room) {
                let roomCard = $('<div>').addClass('col-12 mb-3');
                let roomDiv = $('<div>').addClass('room');
                roomDiv.append($('<h3>').text(room.name));
                let viewButton = $('<a>')
                    .attr('href', `/room/${encodeURIComponent(room.name)}`)
                    .addClass('btn btn-secondary mt-2')
                    .text('View Room');
                roomDiv.append(viewButton);
                roomCard.append(roomDiv);
                $('#rooms-container').append(roomCard);
            });
        });
    }

    // Function to load devices in a room
    function loadRoomDevices(roomName) {
        $.getJSON(`/api/rooms/${roomName}/devices`, function(devices) {
            $('#room-devices').empty();
            devices.forEach(function(device) {
                let deviceCard = createDeviceCard(device);
                $('#room-devices').append(deviceCard);
            });
        });
    }

    // Function to load favorite devices
    function loadFavorites() {
        $.getJSON('/api/rooms', function(rooms) {
            $('#favorites-container').empty();
            let favoriteDevices = [];
            rooms.forEach(function(room) {
                room.devices.forEach(function(device) {
                    if (preferences.favorites.includes(device.uniqueId)) {
                        favoriteDevices.push(device);
                    }
                });
            });
            favoriteDevices.forEach(function(device) {
                let deviceCard = createDeviceCard(device);
                $('#favorites-container').append(deviceCard);
            });
        });
    }

    // Function to create a device card with controls
    function createDeviceCard(device) {
        let deviceCard = $('<div>').addClass('col-12 mb-3');
        let deviceDiv = $('<div>').addClass('device');
        deviceDiv.append($('<h5>').text(device.serviceName));

        let favoriteIcon = $('<span>')
            .addClass('favorite-icon')
            .html(preferences.favorites.includes(device.uniqueId) ? '★' : '☆')
            .click(function() {
                toggleFavorite(device.uniqueId, $(this));
            });
        deviceDiv.append(favoriteIcon);

        let controlsDiv = $('<div>').addClass('controls');

        device.characteristics.forEach(function(char) {
            if (char.canRead) {
                if (char.type === 'On') {
                    let toggleBtn = $('<div>')
                        .addClass('btn-toggle' + (char.value ? ' active' : ''))
                        .click(function() {
                            let newValue = char.value ? 0 : 1;
                            updateDevice(device.uniqueId, { 'On': newValue });
                            char.value = newValue;
                            $(this).toggleClass('active');
                        });
                    controlsDiv.append($('<div>').append(toggleBtn));
                } else if (char.type === 'Brightness') {
                    let valueDisplay = $('<span>').addClass('slider-value').text(char.value);
                    let slider = $('<input>')
                        .attr('type', 'range')
                        .attr('min', char.minValue || 0)
                        .attr('max', char.maxValue || 100)
                        .val(char.value)
                        .on('input change', function() {
                            let newValue = parseInt($(this).val());
                            valueDisplay.text(newValue);
                            updateDevice(device.uniqueId, { 'Brightness': newValue });
                        });
                    controlsDiv.append(
                        $('<div>').addClass('slider-label').append('Brightness', slider, valueDisplay)
                    );
                } else if (char.type === 'Hue') {
                    // Use color wheel only for Hue
                    let colorPickerDiv = $('<div>').addClass('color-picker');
                    controlsDiv.append(colorPickerDiv);
                    let initialColor = {
                        h: char.value || 0,
                        s: device.characteristics.find(c => c.type === 'Saturation').value || 100,
                        v: 100
                    };
                    let colorPicker = new iro.ColorPicker(colorPickerDiv[0], {
                        width: 200,
                        color: initialColor,
                        layout: [
                            { component: iro.ui.Wheel }
                        ]
                    });
                    colorPicker.on('color:change', function(color) {
                        // Update only the hue
                        updateDevice(device.uniqueId, {
                            'Hue': color.hsv.h,
                            'Saturation': color.hsv.s
                        });
                    });
                } else if (char.type === 'Saturation') {
                    let valueDisplay = $('<span>').addClass('slider-value').text(char.value);
                    let slider = $('<input>')
                        .attr('type', 'range')
                        .attr('min', char.minValue || 0)
                        .attr('max', char.maxValue || 100)
                        .val(char.value)
                        .on('input change', function() {
                            let newValue = parseInt($(this).val());
                            valueDisplay.text(newValue);
                            updateDevice(device.uniqueId, { 'Saturation': newValue });
                        });
                    controlsDiv.append(
                        $('<div>').addClass('slider-label').append('Saturation', slider, valueDisplay)
                    );
                } else if (char.type === 'TargetDoorState') {
                    let doorBtn = $('<button>')
                        .addClass('btn btn-primary mt-2')
                        .text(char.value === 1 ? 'Open Door' : 'Close Door')
                        .click(function() {
                            let newState = char.value === 1 ? 0 : 1;
                            updateDevice(device.uniqueId, { 'TargetDoorState': newState });
                            char.value = newState;
                            $(this).text(newState === 1 ? 'Open Door' : 'Close Door');
                        });
                    controlsDiv.append(doorBtn);
                } else if (char.type === 'ColorTemperature') {
                    let valueDisplay = $('<span>').addClass('slider-value').text(char.value);
                    let slider = $('<input>')
                        .attr('type', 'range')
                        .attr('min', char.minValue || 140)
                        .attr('max', char.maxValue || 500)
                        .val(char.value)
                        .on('input change', function() {
                            let newValue = parseInt($(this).val());
                            valueDisplay.text(newValue);
                            updateDevice(device.uniqueId, { 'ColorTemperature': newValue });
                        });
                    controlsDiv.append(
                        $('<div>').addClass('slider-label').append('Color Temp', slider, valueDisplay)
                    );
                }
            }
        });

        deviceDiv.append(controlsDiv);
        deviceCard.append(deviceDiv);
        return deviceCard;
    }

    // Update function to send only changed characteristics
    let updateDevice = (function() {
        let debounceTimers = {};
        return function(uniqueId, data) {
            clearTimeout(debounceTimers[uniqueId]);
            debounceTimers[uniqueId] = setTimeout(function() {
                $.ajax({
                    url: `/api/device/${uniqueId}`,
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify(data),
                    success: function(response) {
                        console.log('Device updated:', response);
                    },
                    error: function(error) {
                        console.error('Error updating device:', error);
                    }
                });
            }, 200); // Debounce to prevent multiple rapid requests
        };
    })();

    // Function to periodically poll for device updates
    function pollDeviceUpdates() {
        if (window.location.pathname.startsWith('/room/')) {
            let roomName = decodeURIComponent(window.location.pathname.split('/').pop());
            loadRoomDevices(roomName);
        } else if (window.location.pathname === '/favorites') {
            loadFavorites();
        }
    }

    // Polling every 10 seconds
    setInterval(pollDeviceUpdates, 10000);

    // Actions page functions
    function loadActions() {
        $('#actions-container').empty();
        preferences.actions.forEach(function(action, index) {
            let actionDiv = $('<div>').addClass('action');
            actionDiv.append($('<h5>').text(action.name));
            let executeBtn = $('<button>')
                .addClass('btn btn-success')
                .text('Execute')
                .click(function() {
                    executeAction(index);
                });
            let deleteBtn = $('<button>')
                .addClass('btn btn-danger')
                .text('Delete')
                .click(function() {
                    preferences.actions.splice(index, 1);
                    savePreferences();
                    loadActions();
                });
            actionDiv.append(executeBtn, deleteBtn);
            $('#actions-container').append(actionDiv);
        });
    }

    function executeAction(actionId) {
        $.ajax({
            url: `/api/actions/${actionId}`,
            type: 'POST',
            success: function(response) {
                console.log('Action executed:', response);
            },
            error: function(error) {
                console.error('Error executing action:', error);
            }
        });
    }

    // Create action functions
    function loadDeviceList() {
        $.getJSON('/api/rooms', function(rooms) {
            let allDevices = [];
            rooms.forEach(function(room) {
                allDevices = allDevices.concat(room.devices);
            });
            displayDeviceList(allDevices);
        });
    }

    function displayDeviceList(devices) {
        $('#device-list').empty();
        devices.forEach(function(device) {
            let deviceDiv = $('<div>').addClass('device-select');
            let deviceName = $('<h5>').text(device.serviceName);
            let selectCheckbox = $('<input>')
                .attr('type', 'checkbox')
                .data('device', device)
                .change(function() {
                    if ($(this).is(':checked')) {
                        let deviceCard = createDeviceCardForAction(device);
                        $('#action-form').append(deviceCard);
                    } else {
                        $('#action-form').find(`[data-unique-id="${device.uniqueId}"]`).remove();
                    }
                });
            deviceDiv.append(deviceName, selectCheckbox);
            $('#device-list').append(deviceDiv);
        });
    }

    function createDeviceCardForAction(device) {
        let deviceCard = $('<div>').addClass('device mb-3').attr('data-unique-id', device.uniqueId);
        deviceCard.append($('<h5>').text(device.serviceName));

        let controlsDiv = $('<div>').addClass('controls');

        device.characteristics.forEach(function(char) {
            if (char.canWrite) {
                if (char.type === 'On') {
                    let toggleBtn = $('<div>')
                        .addClass('btn-toggle')
                        .click(function() {
                            let newValue = $(this).hasClass('active') ? 0 : 1;
                            $(this).toggleClass('active');
                            $(this).data('value', newValue);
                        })
                        .data('value', 0);
                    controlsDiv.append($('<div>').append(toggleBtn));
                } else if (char.type === 'Brightness' || char.type === 'Saturation' || char.type === 'ColorTemperature') {
                    let valueDisplay = $('<span>').addClass('slider-value').text(char.minValue || 0);
                    let slider = $('<input>')
                        .attr('type', 'range')
                        .attr('min', char.minValue || 0)
                        .attr('max', char.maxValue || 100)
                        .val(char.minValue || 0)
                        .on('input change', function() {
                            let newValue = parseInt($(this).val());
                            valueDisplay.text(newValue);
                            $(this).data('value', newValue);
                        })
                        .data('value', char.minValue || 0);
                    controlsDiv.append(
                        $('<div>').addClass('slider-label').append(char.type, slider, valueDisplay)
                    );
                } else if (char.type === 'Hue') {
                    let colorPickerDiv = $('<div>').addClass('color-picker');
                    controlsDiv.append(colorPickerDiv);
                    let colorPicker = new iro.ColorPicker(colorPickerDiv[0], {
                        width: 200,
                        color: { h: 0, s: 100, v: 100 },
                        layout: [
                            { component: iro.ui.Wheel }
                        ]
                    });
                    colorPicker.on('color:change', function(color) {
                        colorPickerDiv.data('value', color.hsv.h);
                    });
                    colorPickerDiv.data('value', 0);
                }
            }
        });

        deviceCard.append(controlsDiv);
        return deviceCard;
    }

    function saveAction() {
        let actionName = $('#action-name').val();
        if (!actionName) {
            alert('Please enter an action name.');
            return;
        }
        let devices = [];
        $('#action-form').find('.device').each(function() {
            let uniqueId = $(this).data('unique-id');
            let deviceAction = { uniqueId: uniqueId, characteristics: [] };
            $(this).find('.controls').children().each(function() {
                let control = $(this);
                if (control.find('.btn-toggle').length) {
                    let charType = 'On';
                    let value = control.find('.btn-toggle').data('value');
                    deviceAction.characteristics.push({ type: charType, value: value });
                } else if (control.find('input[type="range"]').length) {
                    let charType = control.find('.slider-label').contents().get(0).nodeValue.trim();
                    let value = control.find('input[type="range"]').data('value');
                    deviceAction.characteristics.push({ type: charType, value: value });
                } else if (control.find('.color-picker').length) {
                    let charType = 'Hue';
                    let value = control.find('.color-picker').data('value');
                    deviceAction.characteristics.push({ type: charType, value: value });
                }
            });
            devices.push(deviceAction);
        });

        let actionData = { name: actionName, devices: devices };
        preferences.actions.push(actionData);
        savePreferences();
        window.location.href = '/actions';
    }

    // Function to toggle favorites
    function toggleFavorite(uniqueId, iconElement) {
        if (preferences.favorites.includes(uniqueId)) {
            preferences.favorites = preferences.favorites.filter(id => id !== uniqueId);
            iconElement.html('☆');
        } else {
            preferences.favorites.push(uniqueId);
            iconElement.html('★');
        }
        savePreferences();
    }

    // Function to save preferences
    function savePreferences() {
        $.ajax({
            url: '/api/preferences',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(preferences),
            success: function(response) {
                console.log('Preferences saved');
            },
            error: function(error) {
                console.error('Error saving preferences:', error);
            }
        });
    }

    // Event Listeners
    $('#create-action-btn').click(function() {
        window.location.href = '/create_action';
    });

    $('#save-action-btn').click(function() {
        saveAction();
    });

    if (window.location.pathname === '/create_action') {
        loadDeviceList();

        // Search functionality
        $('#device-search').on('input', function() {
            let searchTerm = $(this).val().toLowerCase();
            $('#device-list .device-select').each(function() {
                let deviceName = $(this).find('h5').text().toLowerCase();
                if (deviceName.includes(searchTerm)) {
                    $(this).show();
                } else {
                    $(this).hide();
                }
            });
        });
    } else if (window.location.pathname === '/actions') {
        loadActions();
    }

    // Initial load based on the page
    if (window.location.pathname === '/') {
        loadRooms();
    } else if (window.location.pathname.startsWith('/room/')) {
        let roomName = decodeURIComponent(window.location.pathname.split('/').pop());
        loadRoomDevices(roomName);
    } else if (window.location.pathname === '/favorites') {
        loadFavorites();
    }

    // Function to periodically poll for device updates
    function pollDeviceUpdates() {
        if (window.location.pathname.startsWith('/room/')) {
            let roomName = decodeURIComponent(window.location.pathname.split('/').pop());
            loadRoomDevices(roomName);
        } else if (window.location.pathname === '/favorites') {
            loadFavorites();
        }
    }
});
