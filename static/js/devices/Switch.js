
function initDeviceControls(data, controlsDiv) {
    var onCharacteristic = data.values['On'];

    var switchHtml = '<div class="form-check form-switch">' +
        '<input class="form-check-input" type="checkbox" id="switch-' + data.uniqueId + '"' +
        (onCharacteristic ? ' checked' : '') + '>' +
        '<label class="form-check-label" for="switch-' + data.uniqueId + '">On/Off</label>' +
        '</div>';

    controlsDiv.html(switchHtml);

    $('#switch-' + data.uniqueId).change(function() {
        var newValue = $(this).is(':checked') ? 1 : 0;
        updateDevice(data.uniqueId, {'On': newValue});
    });
}

