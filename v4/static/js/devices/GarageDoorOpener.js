
function initGarageDoorOpener(element, device) {
    var uniqueId = device.uniqueId;
    var select = element.find('.target-door-state');
    select.change(function() {
        var state = $(this).val();
        $.ajax({
            url: '/api/device/' + uniqueId,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'TargetDoorState': parseInt(state) })
        });
    });
}
