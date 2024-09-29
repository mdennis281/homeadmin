
function initSwitch(element, device) {
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
}
