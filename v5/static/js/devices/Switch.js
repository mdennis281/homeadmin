function initSwitch(device) {
    var deviceElement = $('[data-unique-id="' + device.uniqueId + '"]');

    function pollState() {
        pollDeviceState(device.uniqueId, function(data) {
            deviceElement.find('.toggle-on-off').prop('checked', data.values.On);
        });
    }

    deviceElement.find('.toggle-on-off').change(function() {
        var isOn = $(this).is(':checked') ? 1 : 0;
        updateDevice(device.uniqueId, { 'On': isOn }, pollState);
    });

    setInterval(pollState, 5000); // Poll every 5 seconds
}
