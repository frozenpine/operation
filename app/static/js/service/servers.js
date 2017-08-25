var app = angular.module('myApp');
app.service('$servers', function($http, $message, $localStorage, $timeout, $rootScope) {
    this.CheckServerStatics = function(params, force) {
        if (force === undefined) {
            force = false;
        }
        if (params.sysID === undefined) {
            return false;
        }
        var request_timestamp = new Date().getTime();
        if ($localStorage.hasOwnProperty('svrStatics_' + params.sysID)) {
            if ($localStorage['svrStatics_' + params.sysID].hasOwnProperty('last_request')) {
                last_request = parseInt($localStorage['svrStatics_' + params.sysID].last_request);
                if (!force && request_timestamp - last_request <
                    ($rootScope.GlobalConfigs.svrStaticsInterval.current * 1000)) {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(angular.extend(
                            $localStorage['svrStatics_' + params.sysID], { cached: false }
                        ));
                    }
                    return false;
                } else {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(angular.extend(
                            $localStorage['svrStatics_' + params.sysID], { cached: true }
                        ));
                    }
                }
            }
            $timeout(function() {
                angular.extend($localStorage['svrStatics_' + params.sysID], { last_request: request_timestamp });
            }, 0);
        }
        $http.get('api/system/id/' + params.sysID + '/svr_statics/check')
            .success(function(response) {
                if (response.error_code === 0) {
                    /* if ($localStorage.hasOwnProperty('svrStatics_' + params.sysID)) {
                        $timeout(function() {
                            $localStorage['svrStatics_' + params.sysID] = response.data;
                        });
                    } else {
                        $timeout(function() {
                            $localStorage['svrStatics_' + params.sysID] = angular.merge(
                                response.data, { last_request: request_timestamp }
                            );
                        });
                    } */
                    $timeout(function() {
                        $localStorage['svrStatics_' + params.sysID] = angular.merge(
                            response.data, { last_request: request_timestamp }
                        );
                    });
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            })
            .error(function(response) {
                console.log(response);
                /* if (response.hasOwnProperty('message')) {
                    $message.Alert(response.message);
                } */
            });
        return true;
    };

    this.ServerList = function(params) {
        if (params.sysID === undefined) {
            return;
        }
        $http.get('api/system/id/' + params.sysID + '/svr_statics')
            .success(function(response) {
                if (response.error_code === 0) {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            })
            .error(function(response) {
                console.log(response);
                /* if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                } else {
                    $message.Alert(response.message);
                } */
            });
    };
});