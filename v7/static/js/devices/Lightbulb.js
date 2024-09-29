
function initDeviceControls(data, controlsDiv) {
    var onCharacteristic = data.values['On'];
    var brightnessCharacteristic = data.values['Brightness'];
    var hueCharacteristic = data.values['Hue'];
    var saturationCharacteristic = data.values['Saturation'];
    var colorTempCharacteristic = data.values['ColorTemperature']

    var switchHtml = '<div class="form-check form-switch">' +
        '<input class="form-check-input" type="checkbox" id="switch-' + data.uniqueId + '"' +
        (onCharacteristic ? ' checked' : '') + '>' +
        '<label class="form-check-label" for="switch-' + data.uniqueId + '">On/Off</label>' +
        '</div>';

    var brightnessHtml = '';
    if (brightnessCharacteristic !== undefined) {
        brightnessHtml = '<label for="brightness-' + data.uniqueId + '" class="form-label">Brightness</label>' +
            '<input type="range" class="form-range" id="brightness-' + data.uniqueId + '" min="0" max="100" value="' + brightnessCharacteristic + '">';
    }

    var colorHtml = '';
    if (hueCharacteristic !== undefined && saturationCharacteristic !== undefined) {
        colorHtml = '<label for="color-' + data.uniqueId + '" class="form-label">Color</label>' +
            '<input type="color" class="form-control form-control-color" id="color-' + data.uniqueId + '" value="' + hslToHex(hueCharacteristic, saturationCharacteristic, 50) + '" title="Choose your color">';
    }

    controlsDiv.html(switchHtml + brightnessHtml + colorHtml);

    $('#switch-' + data.uniqueId).change(function() {
        var newValue = $(this).is(':checked') ? 1 : 0;
        updateDevice(data.uniqueId, {'On': newValue});
    });

    $('#brightness-' + data.uniqueId).on('input change', function() {
        var newValue = parseInt($(this).val());
        updateDevice(data.uniqueId, {'Brightness': newValue});
    });

    $('#color-' + data.uniqueId).change(function() {
        var hexColor = $(this).val();
        var hsl = hexToHSL(hexColor);
        updateDevice(data.uniqueId, {'Hue': hsl.h, 'Saturation': hsl.s});
    });
    
}

function hslToHex(h, s, l){
    const hsl = `hsl(${h},${s},${l})`;
    s /= 100;
    l /= 100;

    let c = (1 - Math.abs(2 * l - 1)) * s,
        x = c * (1 - Math.abs((h / 60) % 2 - 1)),
        m = l - c/2,
        r = 0,
        g = 0,
        b = 0;

    if (0 <= h && h < 60) {
        r = c; g = x; b = 0;  
    } else if (60 <= h && h < 120) {
        r = x; g = c; b = 0;  
    } else if (120 <= h && h < 180) {
        r = 0; g = c; b = x;  
    } else if (180 <= h && h < 240) {
        r = 0; g = x; b = c;  
    } else if (240 <= h && h < 300) {
        r = x; g = 0; b = c;  
    } else if (300 <= h && h < 360) {
        r = c; g = 0; b = x;  
    }
    r = Math.round((r + m) * 255);
    g = Math.round((g + m) * 255);
    b = Math.round((b + m) * 255);
    const hex = "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
    console.log(`${hsl} > ${hex}`);
    return hex;
}

function hexToHSL(H) {
    let r = 0, g = 0, b = 0;
    if (H.length == 4) {
        r = "0x" + H[1] + H[1];
        g = "0x" + H[2] + H[2];
        b = "0x" + H[3] + H[3];
    } else if (H.length == 7) {
        r = "0x" + H[1] + H[2];
        g = "0x" + H[3] + H[4];
        b = "0x" + H[5] + H[6];
    }
    r /= 255;
    g /= 255;
    b /= 255;
    let cmin = Math.min(r,g,b),
        cmax = Math.max(r,g,b),
        delta = cmax - cmin,
        h = 0,
        s = 0,
        l = 0;
    if (delta == 0)
        h = 0;
    else if (cmax == r)
        h = ((g - b) / delta) % 6;
    else if (cmax == g)
        h = (b - r) / delta + 2;
    else
        h = (r - g) / delta + 4;
    h = Math.round(h * 60);
    if (h < 0)
        h += 360;
    l = (cmax + cmin) / 2;
    s = delta == 0 ? 0 : delta / (1 - Math.abs(2 * l - 1));
    s = +(s * 100).toFixed(1);
    l = +(l * 100).toFixed(1);
    const hsl = `hsl(${h},${s},${l})`;
    console.log(`${H} > ${hsl}`);
    return {h: Math.round(h), s: Math.round(s), l: Math.round(l)};
}