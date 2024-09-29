
function initLightbulb(element, device) {
    var uniqueId = device.uniqueId;
    var toggle = element.find('.toggle-on-off');
    toggle.change(function() {
        var isOn = $(this).is(':checked') ? 1 : 0;
        $.ajax({
            url: '/api/device/' + uniqueId,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'On': isOn })
        });
    });
    var brightnessSlider = element.find('.brightness-slider');
    brightnessSlider.change(function() {
        var brightness = $(this).val();
        $.ajax({
            url: '/api/device/' + uniqueId,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'Brightness': parseInt(brightness) })
        });
    });
    var colorPicker = element.find('.color-picker');
    colorPicker.change(function() {
        var color = $(this).val();
        var rgb = hexToRgb(color);
        var hsv = rgbToHsv(rgb.r, rgb.g, rgb.b);
        $.ajax({
            url: '/api/device/' + uniqueId,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                'Hue': parseInt(hsv.h * 360),
                'Saturation': parseInt(hsv.s * 100)
            })
        });
    });
    var colorTempSlider = element.find('.color-temp-slider');
    colorTempSlider.change(function() {
        var temp = $(this).val();
        $.ajax({
            url: '/api/device/' + uniqueId,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'ColorTemperature': parseInt(temp) })
        });
    });
}

function hexToRgb(hex) {
    var bigint = parseInt(hex.replace('#', ''), 16);
    var r = (bigint >> 16) & 255;
    var g = (bigint >> 8) & 255;
    var b = bigint & 255;
    return { r: r, g: g, b: b };
}

function rgbToHsv(r, g, b) {
    r /= 255; g /= 255; b /= 255;
    var max = Math.max(r, g, b), min = Math.min(r, g, b);
    var h, s, v = max;
    var d = max - min;
    s = max == 0 ? 0 : d / max;
    if (max == min) {
        h = 0; // achromatic
    } else {
        switch (max) {
            case r: h = (g - b) / d + (g < b ? 6 : 0); break;
            case g: h = (b - r) / d + 2; break;
            case b: h = (r - g) / d + 4; break;
        }
        h /= 6;
    }
    return { h: h, s: s, v: v };
}
