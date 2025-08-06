function isDebug() { return (new URLSearchParams(window.location.search)).get('debug'); }
function recordingAction() { return (new URLSearchParams(window.location.search)).get('recordAction'); }


function loadDevice(uniqueId, deviceType) {
    $.get('/api/device/' + uniqueId, function(data) {
        var controlsDiv = $('#controls-' + uniqueId);
        $.getScript('/static/js/devices/' + deviceType + '.js', function() {
            initDeviceControls(data, controlsDiv);
            if (isDebug()) 
                debugTable(data.serviceCharacteristics, controlsDiv);
        });
    });
}

function initDevice(device) {
    var controlsDiv = $('#controls-' + device.uniqueId);
    $.getScript('/static/js/devices/' + device.type + '.js', function() {
        initDeviceControls(device, controlsDiv);
        if (isDebug()) 
            debugTable(device.serviceCharacteristics, controlsDiv);
    });
}

var antiFloodTimeout = null;
function updateDevice(uniqueId, characteristics) {
    function doUpdate(uniqueId, characteristics) {
        $.ajax({
            url: '/api/device/' + uniqueId,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(characteristics),
            success: function(response) {
                console.log('Device updated', response);
                if (recordingAction()) {
                    addActionStep(uniqueId,characteristics)
                }
                if (isDebug()) {
                    // update debug table with latest values
                    let controlsDiv = $(`#controls-${uniqueId}`);
                    debugTable(response.updatedCharacteristics,controlsDiv);
                }
                    
            }
        });
    }

    // Clear previous timeout to debounce the calls
    if (antiFloodTimeout) {
        clearTimeout(antiFloodTimeout);
    }

    antiFloodTimeout = setTimeout(() => {
        doUpdate(uniqueId, characteristics);
    }, 200); 
}


function debugTable(characteristics, controlsDiv) {
    console.log(characteristics)
    let table = `<tr><th>Characteristic</th><th>Value</th></tr>`;
    for (let c of characteristics) {
        table += `<tr><td>${c.description}</td><td>${c.value}</td></tr>`;
    }

    let existing = controlsDiv.find('.debug-table');
    if (existing.length > 0) {
        existing.html(table);
    } 
    else {
        const fullDiv = `
        <div class="debug-div">
            <table class="debug-table">${table}</table>
        </div>`;
        controlsDiv.append(fullDiv);
    }
        
}


function generateRandomString(length) {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    let nonce = ''
    while (nonce.length < length) {
      nonce += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    return nonce
}

function addActionStep(uniqueId,characteristics) {
    let actionName = recordingAction();

    let savedActions = JSON.parse(localStorage.getItem('savedActions') || '{}');
    // if action doesnt yet exist
    if (!savedActions[actionName]) savedActions[actionName] = {};
    let action = savedActions[actionName];

    // if changing properties on this device does not yet exist
    if (!action[uniqueId]) action[uniqueId] = {};
    for (const key in characteristics) {
        action[uniqueId][key] = characteristics[key];
    } 
    

    localStorage.setItem('savedActions',JSON.stringify(savedActions,null,2));
}