app.filter('processesFilter', function() {
    return function(process_list, filter) {
        var result = [];
        angular.forEach(process_list, function(value, index) {
            var filted = false;
            if (filter.system !== undefined && value.system.id !== filter.system.id) {
                filted = true;
            }
            if (filter.server !== undefined && value.server.id !== filter.server.id) {
                filted = true;
            }
            if (!filted) {
                result.push(value);
            }
        });
        return result;
    };
});