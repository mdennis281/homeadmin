$(document).ready(function() {
    $('.device.lightbulb').each(function() {
        var uniqueId = $(this).attr('id').replace('device-', '');
        var $device = $(this);

        // Event handlers
        var $onSwitch = $device.find('#on-' + uniqueId);
        $onSwitch.change(function() {
            var isOn = $(this).is(':checked') ? 1 : 0;
            updateDevice(uniqueId, { 'On': isOn });
        });

        var $brightnessSlider = $device.find('#brightness-' + uniqueId);
        $brightnessSlider.on('input change', function() {
            var brightness = parseInt($(this).val());
            updateDevice(uniqueId, { 'Brightness': brightness });
        });

        var $hueSlider = $device.find('#hue-' + uniqueId);
        $hueSlider.on('input change', function() {
            var hue = parseFloat($(this).val());
            updateDevice(uniqueId, { 'Hue': hue });
        });

        var $saturationSlider = $device.find('#saturation-' + uniqueId);
        $saturationSlider.on('input change', function() {
            var saturation = parseFloat($(this).val());
            updateDevice(uniqueId, { 'Saturation': saturation });
        });

        var $colorTempSlider = $device.find('#colortemperature-' + uniqueId);
        $colorTempSlider.on('input change', function() {
            var colorTemp = parseInt($(this).val());
            updateDevice(uniqueId, { 'ColorTemperature': colorTemp });
        });

        // Polling
        startPolling(uniqueId, 5000, function(data) {
            // Update UI with the latest values
            data = data.values;
            if (data['On'] !== undefined) {
                $onSwitch.prop('checked', data['On'] ? true : false);
            }
            if (data['Brightness'] !== undefined) {
                $brightnessSlider.val(data['Brightness']);
            }
            if (data['Hue'] !== undefined) {
                $hueSlider.val(data['Hue']);
            }
            if (data['Saturation'] !== undefined) {
                $saturationSlider.val(data['Saturation']);
            }
            if (data['ColorTemperature'] !== undefined) {
                $colorTempSlider.val(data['ColorTemperature']);
            }
        });
    });
});