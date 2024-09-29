function initLightbulb(device) {
    var deviceElement = $('[data-unique-id="' + device.uniqueId + '"]');

    function pollState() {
        pollDeviceState(device.uniqueId, function(data) {
            deviceElement.find('.toggle-on-off').prop('checked', data.values.On);
            deviceElement.find('.brightness-slider').val(data.values.Brightness);
            deviceElement.find('.hue-slider').val(data.values.Hue);
            deviceElement.find('.saturation-slider').val(data.values.Saturation);
            deviceElement.find('.color-temperature-slider').val(data.values.ColorTemperature);
        });
    }

    deviceElement.find('.toggle-on-off').change(function() {
        var isOn = $(this).is(':checked') ? 1 : 0;
        updateDevice(device.uniqueId, { 'On': isOn }, pollState);
    });

    deviceElement.find('.brightness-slider').change(function() {
        var brightness = parseInt($(this).val());
        updateDevice(device.uniqueId, { 'Brightness': brightness }, pollState);
    });

    deviceElement.find('.hue-slider').change(function() {
        var hue = parseFloat($(this).val());
        updateDevice(device.uniqueId, { 'Hue': hue }, pollState);
    });

    deviceElement.find('.saturation-slider').change(function() {
        var saturation = parseFloat($(this).val());
        updateDevice(device.uniqueId, { 'Saturation': saturation }, pollState);
    });

    deviceElement.find('.color-temperature-slider').change(function() {
        var colorTemperature = parseInt($(this).val());
        updateDevice(device.uniqueId, { 'ColorTemperature': colorTemperature }, pollState);
    });

    setInterval(pollState, 5000); // Poll every 5 seconds
}
