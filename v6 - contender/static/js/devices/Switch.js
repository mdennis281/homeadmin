function initDevice(uniqueId) {
    (function(uniqueId) {
        var deviceCard = $('.device-card[data-unique-id="' + uniqueId + '"]');

        // On/Off toggle
        deviceCard.find('.toggle-on-off').change(function() {
            var isOn = $(this).is(':checked') ? 1 : 0;
            updateDeviceState(uniqueId, {'On': isOn}, function(response) {
                console.log('Device updated:', response);
            }, function(error) {
                console.error('Error updating device:', error);
            });
        });

        // Polling device state
        pollDeviceState(uniqueId, function(deviceData) {
            var values = deviceData.values;
            // Update UI elements with new values
            deviceCard.find('.toggle-on-off').prop('checked', values.On == 1);
        }, 5000); // Poll every 5 seconds
    })(uniqueId);
}