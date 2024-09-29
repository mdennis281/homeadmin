function initDevice(uniqueId) {
    (function(uniqueId) {
        var deviceCard = $('.device-card[data-unique-id="' + uniqueId + '"]');

        // Door state change
        deviceCard.find('#doorstate-' + uniqueId).change(function() {
            var targetState = parseInt($(this).val());
            updateDeviceState(uniqueId, {'TargetDoorState': targetState}, function(response) {
                console.log('Device updated:', response);
            }, function(error) {
                console.error('Error updating device:', error);
            });
        });

        // Polling device state
        pollDeviceState(uniqueId, function(deviceData) {
            var values = deviceData.values;
            // Update UI elements with new values
            deviceCard.find('#doorstate-' + uniqueId).val(values.TargetDoorState);
            var currentStateText = '';
            switch (values.CurrentDoorState) {
                case 0:
                    currentStateText = 'Open';
                    break;
                case 1:
                    currentStateText = 'Closed';
                    break;
                case 2:
                    currentStateText = 'Opening';
                    break;
                case 3:
                    currentStateText = 'Closing';
                    break;
                case 4:
                    currentStateText = 'Stopped';
                    break;
                default:
                    currentStateText = 'Unknown';
            }
            deviceCard.find('#currentstate-' + uniqueId).text(currentStateText);
            deviceCard.find('#obstruction-' + uniqueId).text(values.ObstructionDetected == 1 ? 'Yes' : 'No');
        }, 5000); // Poll every 5 seconds
    })(uniqueId);
}