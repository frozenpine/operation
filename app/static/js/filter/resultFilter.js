app.filter('resultFilter', function() {
    return function(ListData, filterLimit, scope) {
        var newArr = [];
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
                    filted = true;
                }
            } else if (filterLimit.authorizor && filterLimit.authorizor !== "") {
                filted = true;
            }
            if (value.results[0] && value.results[0].error_code === 0 ? filterLimit.result == 'false' : filterLimit.result === 'true') {
                filted = true;
            }
            var startDateTimestampe;
            var recordDateTimestampe;
            var endDateTimestampe;
            var endTimestamp;
            var recordTimestamp;
            if (filterLimit.executeStartDate) {
                if (filterLimit.executeStartTime) {
                    startDateTimestampe = filterLimit.executeStartDate.getTime() +
                        filterLimit.executeStartTime.getTime() + 8 * 3600 * 1000;
                    recordDateTimestampe = Date.parse(value.operated_at);
                    if (recordDateTimestampe < startDateTimestampe) {
                        filted = true;
                    }
                } else {
                    startDateTimestampe = filterLimit.executeStartDate.getTime();
                    recordDateTimestampe = Date.parse(value.operated_at.match(/\d{4}-\d{2}-\d{2}/));
                    if (recordDateTimestampe < startDateTimestampe) {
                        filted = true;
                    }
                }
            } else if (filterLimit.executeStartTime) {
                startTimestamp = filterLimit.executeStartTime.getTime();
                recordTimestamp = Date.parse('The Jan 01 1970 ' + value.operated_at.match(/\d{2}:\d{2}:\d{2}/) + ' GMT+0800');
                if (recordTimestamp < startTimestamp) {
                    filted = true;
                }
            }
            if (filterLimit.executeEndDate) {
                if (filterLimit.executeEndTime) {
                    endDateTimestampe = filterLimit.executeEndDate.getTime() +
                        filterLimit.executeEndTime.getTime() + 8 * 3600 * 1000;
                    recordDateTimestampe = Date.parse(value.operated_at);
                    if (recordDateTimestampe > endDateTimestampe) {
                        filted = true;
                    }
                } else {
                    endDateTimestampe = filterLimit.executeEndDate.getTime() + 24 * 3600 * 1000 - 1;
                    recordDateTimestampe = Date.parse(value.operated_at.match(/\d{4}-\d{2}-\d{2}/));
                    if (recordDateTimestampe > endDateTimestampe) {
                        filted = true;
                    }
                }
            } else if (filterLimit.executeEndTime) {
                endTimestamp = filterLimit.executeEndTime.getTime();
                recordTimestamp = Date.parse('The Jan 01 1970 ' + value.operated_at.match(/\d{2}:\d{2}:\d{2}/) + ' GMT+0800');
                if (recordTimestamp > endTimestamp) {
                    filted = true;
                }
            }
            if (!filted) {
                newArr.push(value);
            }
        });
        scope.pages = Math.ceil(newArr.length / scope.listsPerPage);
        return newArr;
    };
});