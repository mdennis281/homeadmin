function initGarageDoorOpener(device) {
    var deviceElement = $('[data-unique-id="' + device.uniqueId + '"]');

    function pollState() {
        pollDeviceState(device.uniqueId, function(data) {
            deviceElement.find('.current-door-state').text(data.values.CurrentDoorState);
            deviceElement.find('.target-door-state').val(data.values.TargetDoorState);
        });
    }

    deviceElement.find('.target-door-state').change(function() {
        var targetState = parseInt($(this).val());
        updateDevice(device.uniqueId, { 'TargetDoorState': targetState }, pollState);
    });

    setInterval(pollState, 5000); // Poll every 5 seconds
}
