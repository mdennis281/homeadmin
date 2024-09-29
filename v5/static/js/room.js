$(document).ready(function() {
    function loadDevices() {
        $.get('/api/rooms/' + encodeURIComponent(roomName) + '/devices', function(data) {
            var devicesList = $('#devices-list');
            devicesList.empty();
            data.forEach(function(device) {
                var deviceType = device.type;
                $.get('/static/js/devices/' + deviceType + '.js', function() {
                    $.get('/templates/devices/' + deviceType + '.html', function(template) {
                        var rendered = Mustache.render(template, { device: device });
                        devicesList.append(rendered);
                        // Initialize device handlers
                        if (typeof window['init' + deviceType] === 'function') {
                            window['init' + deviceType](device);
                        }
                    });
                });
            });
        });
    }

    loadDevices();
    setInterval(loadDevices, 5000); // Poll every 5 seconds
});
