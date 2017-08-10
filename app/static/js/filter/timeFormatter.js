app.filter('time', function($filter) {
    return function(time_string, formatter) {
        var match = time_string.match(/\d{1,2}:\d{1,2}(:\d{1,2})?/);
        if (match !== null) {
            var datetime = new Date('The Jan 01 1970 ' + match[0] + ' GMT+0800');
            return $filter('date')(datetime, formatter);
        } else {
            return '';
        }
    };
});