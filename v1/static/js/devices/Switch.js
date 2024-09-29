$(document).ready(function() {
    $('.device.switch').each(function() {
        var uniqueId = $(this).attr('id').replace('device-', '');
        var $device = $(this);

        // Event handlers
        var $onSwitch = $device.find('#on-' + uniqueId);
        $onSwitch.change(function() {
            var isOn = $(this).is(':checked') ? 1 : 0;
            updateDevice(uniqueId, { 'On': isOn });
        });

        // Polling
        startPolling(uniqueId, 5000, function(data) {
            // Update UI with the latest values
            data = data.values;
            if (data['On'] !== undefined) {
                $onSwitch.prop('checked', data['On'] ? true : false);
            }
        });
    });
});
