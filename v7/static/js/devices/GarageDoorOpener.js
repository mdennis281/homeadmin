
function initDeviceControls(data, controlsDiv) {
    var targetDoorState = data.values['TargetDoorState'];
    var currentDoorState = data.values['CurrentDoorState'];
    var obstructionDetected = data.values['ObstructionDetected'];

    var doorStateHtml = '<label for="doorstate-' + data.uniqueId + '" class="form-label">Door State</label>' +
        '<select class="form-select" id="doorstate-' + data.uniqueId + '">' +
        '<option value="0"' + (targetDoorState == 0 ? ' selected' : '') + '>Open</option>' +
        '<option value="1"' + (targetDoorState == 1 ? ' selected' : '') + '>Closed</option>' +
        '</select>';

    controlsDiv.html(doorStateHtml);

    $('#doorstate-' + data.uniqueId).change(function() {
        var newValue = parseInt($(this).val());
        updateDevice(data.uniqueId, {'TargetDoorState': newValue});
    });
}


