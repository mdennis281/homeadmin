
function initDevice(deviceElement, deviceData) {
    var deviceType = deviceData.type;
    if (deviceType === 'Lightbulb') {
        initLightbulb(deviceElement, deviceData);
    } else if (deviceType === 'Switch') {
        initSwitch(deviceElement, deviceData);
    } else if (deviceType === 'GarageDoorOpener') {
        initGarageDoorOpener(deviceElement, deviceData);
    }
}
