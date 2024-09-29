$(document).ready(function() {
    $('.device.garagedooropener').each(function() {
        var uniqueId = $(this).attr('id').replace('device-', '');
        var $device = $(this);

        var $openButton = $device.find('#open-' + uniqueId);
        var $closeButton = $device.find('#close-' + uniqueId);
        var $stateSpan = $device.find('#state-' + uniqueId);

        $openButton.click(function() {
            updateDevice(uniqueId, { 'TargetDoorState': 0 });
        });

        $closeButton.click(function() {
            updateDevice(uniqueId, { 'TargetDoorState': 1 });
        });

        var stateMapping = {
            0: 'Open',
            1: 'Closed',
            2: 'Opening',
            3: 'Closing',
            4: 'Stopped'
        };

        // Polling
        startPolling(uniqueId, 5000, function(data) {
            // Update UI with the latest values
            data = data.values;
            if (data['CurrentDoorState'] !== undefined) {
                $stateSpan.text(stateMapping[data['CurrentDoorState']]);
            }
        });
    });
});
