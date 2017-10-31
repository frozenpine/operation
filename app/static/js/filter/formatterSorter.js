app.filter('formatterSorter', function() {
    return function(dt_object, formatter) {
        var result = [];
        angular.forEach(formatter, function(value, index) {
            result.push(dt_object[value.key]);
        });
        result.push(dt_object.updated_time);
        return result;
    };
});
