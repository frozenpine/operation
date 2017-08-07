app.filter('resultFilter', function() {
    return function(ListData, filterLimit, scope) {
        var newArr = new Array();
        angular.forEach(ListData, function(value, index) {
            var filted = false;
            if (value.operation.name.toLowerCase().match(filterLimit.operation) === null) {
                filted = true;
            }
            if (value.operator.name.toLowerCase().match(filterLimit.operator) === null) {
                filted = true;
            }
            if (value.authorizor) {
                if (value.authorizor.name.toLowerCase().match(filterLimit.authorizor) === null) {
                    filted = true;;
                }
            } else if (filterLimit.authorizor && filterLimit.authorizor !== "") {
                filted = true;
            }
            if (value.results[0] && value.results[0].error_code == 0 ? filterLimit.result == 'false' : filterLimit.result == 'true') {
                filted = true;;
            }
            if (filterLimit.executeStartDate) {
                if (filterLimit.executeStartTime) {
                    var startDateTimestampe = filterLimit.executeStartDate.getTime() +
                        filterLimit.executeStartTime.getTime() + 8 * 3600 * 1000;
                    var recordDateTimestampe = Date.parse(value.operated_at);
                    if (recordDateTimestampe < startDateTimestampe) {
                        filted = true;;
                    }
                } else {
                    var startDateTimestampe = filterLimit.executeStartDate.getTime();
                    var recordDateTimestampe = Date.parse(value.operated_at.match(/\d{4}-\d{2}-\d{2}/))
                    if (recordDateTimestampe < startDateTimestampe) {
                        filted = true;;
                    }
                }
            } else if (filterLimit.executeStartTime) {
                var startTimestamp = filterLimit.executeStartTime.getTime();
                var recordTimestamp = Date.parse('The Jan 01 1970 ' + value.operated_at.match(/\d{2}:\d{2}:\d{2}/) + ' GMT+0800');
                if (recordTimestamp < startTimestamp) {
                    filted = true;
                }
            }
            if (filterLimit.executeEndDate) {
                if (filterLimit.executeEndTime) {
                    var endDateTimestampe = filterLimit.executeEndDate.getTime() +
                        filterLimit.executeEndTime.getTime() + 8 * 3600 * 1000;
                    var recordDateTimestampe = Date.parse(value.operated_at);
                    if (recordDateTimestampe > endDateTimestampe) {
                        filted = true;;
                    }
                } else {
                    var endDateTimestampe = filterLimit.executeEndDate.getTime() + 24 * 3600 * 1000 - 1;
                    var recordDateTimestampe = Date.parse(value.operated_at.match(/\d{4}-\d{2}-\d{2}/));
                    if (recordDateTimestampe > endDateTimestampe) {
                        filted = true;;
                    }
                }
            } else if (filterLimit.executeEndTime) {
                var endTimestamp = filterLimit.executeEndTime.getTime();
                var recordTimestamp = Date.parse('The Jan 01 1970 ' + value.operated_at.match(/\d{2}:\d{2}:\d{2}/) + ' GMT+0800');
                if (recordTimestamp > endTimestamp) {
                    filted = true;
                }
            }
            if (!filted) {
                newArr.push(value);
            }
        })
        scope.pages = Math.ceil(newArr.length / scope.listsPerPage);
        return newArr;
    }
});