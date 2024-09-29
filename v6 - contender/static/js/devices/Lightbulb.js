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

        // Handle other characteristics
        deviceCard.find('input[type="range"]').on('input change', function() {
            var inputId = $(this).attr('id');
            var charType = inputId.split('-')[0];
            var value = $(this).val();
            var data = {};
            data[charType.charAt(0).toUpperCase() + charType.slice(1)] = parseFloat(value);
            updateDeviceState(uniqueId, data, function(response) {
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
            if (values.Brightness !== undefined) {
                deviceCard.find('#brightness-' + uniqueId).val(values.Brightness);
            }
            if (values.Hue !== undefined) {
                deviceCard.find('#hue-' + uniqueId).val(values.Hue);
            }
            if (values.Saturation !== undefined) {
                deviceCard.find('#saturation-' + uniqueId).val(values.Saturation);
            }
            if (values.ColorTemperature !== undefined) {
                deviceCard.find('#colortemperature-' + uniqueId).val(values.ColorTemperature);
            }
        }, 5000); // Poll every 5 seconds
    })(uniqueId);
}