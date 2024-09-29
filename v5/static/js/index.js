$(document).ready(function() {
    $.get('/api/rooms', function(data) {
        var roomsList = $('#rooms-list');
        data.forEach(function(room) {
            var roomItem = $('<a href="/room/' + encodeURIComponent(room.name) + '" class="list-group-item list-group-item-action">' + room.name + '</a>');
            roomsList.append(roomItem);
        });
    });
});
