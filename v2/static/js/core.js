// Core JavaScript functions
function pollDeviceState(uniqueId, callback) {
    $.getJSON('/api/device/' + uniqueId, function(data) {
        callback(data);
    });
}

function updateDeviceState(uniqueId, payload, callback) {
    $.ajax({
        url: '/api/device/' + uniqueId,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(payload),
        success: function(response) {
            callback(response);
        }
    });
}
