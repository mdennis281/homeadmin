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