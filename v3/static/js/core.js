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