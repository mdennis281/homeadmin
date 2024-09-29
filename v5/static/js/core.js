function getDeviceTypeTemplate(deviceType) {
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
