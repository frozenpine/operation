var app = angular.module('myApp');
app.service('$systems', function($http, $message, $localStorage, $sessionStorage, $timeout, $rootScope) {
    this.SystemStaticsCheck = function(params, force = false) {
        if (params.sysID === undefined) {
            return false;
        }
        var request_timestamp = new Date().getTime();
        if ($localStorage.hasOwnProperty('sysStatics_' + params.sysID)) {
            if ($localStorage['sysStatics_' + params.sysID].hasOwnProperty('last_request')) {
                last_request = parseInt($localStorage['sysStatics_' + params.sysID].last_request);
                if (!force && request_timestamp - last_request <
                    ($rootScope.GlobalConfigs.sysStaticsInterval.current * 1000)) {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(angular.extend(
                            $localStorage['sysStatics_' + params.sysID], { cached: false }
                        ));
                    }
                    return false;
                } else {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(angular.extend(
                            $localStorage['sysStatics_' + params.sysID], { cached: true }
                        ));
                    }
                }
            }
            $timeout(function() {
                angular.extend($localStorage['sysStatics_' + params.sysID], { last_request: request_timestamp });
            }, 0);
        }
        /* $websocket.Request({
            uri: 'api/system/id/' + params.sysID + '/sys_statics/check',
            method: 'get',
            callback: function(response) {
                if (response.error_code == 0) {
                    if ($localStorage.hasOwnProperty('sysStatics_' + params.sysID)) {
                        $timeout(function() {
                            angular.merge($localStorage['sysStatics_' + params.sysID], response.data);
                        })
                    } else {
                        $timeout(function() {
                            $localStorage['sysStatics_' + params.sysID] = angular.merge(
                                response.data, { last_request: request_timestamp }
                            );
                        });
                    }
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            }
        }); */
        $http.get('api/system/id/' + params.sysID + '/sys_statics/check')
            .success(function(response) {
                if (response.error_code == 0) {
                    if ($localStorage.hasOwnProperty('sysStatics_' + params.sysID)) {
                        $timeout(function() {
                            angular.merge($localStorage['sysStatics_' + params.sysID], response.data);
                        })
                    } else {
                        $timeout(function() {
                            $localStorage['sysStatics_' + params.sysID] = angular.merge(
                                response.data, { last_request: request_timestamp }
                            );
                        });
                    }
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            })
            .error(function(response) {
                console.log(response);
                if (response.hasOwnProperty('message')) {
                    $message.Alert(response.message);
                }
            });
        return true;
    }

    this.SystemList = function(params) {
        if (params.sysID === undefined) {
            return;
        }
        /* $websocket.Request({
            uri: 'api/system/id/' + params.sysID + '/sys_statics',
            method: 'get',
            callback: function(response) {
                if (response.error_code == 0) {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            }
        }); */
        $http.get('api/system/id/' + params.sysID + '/sys_statics')
            .success(function(response) {
                if (response.error_code == 0) {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            })
            .error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
    }

    this.LoginStaticsCheck = function(params, force = false) {
        if (params.sysID === undefined) {
            return false;
        }
        var request_timestamp = new Date().getTime();
        if ($sessionStorage.hasOwnProperty('loginStatics_' + params.sysID)) {
            if ($sessionStorage['loginStatics_' + params.sysID].hasOwnProperty('last_request')) {
                last_request = parseInt($sessionStorage['loginStatics_' + params.sysID].last_request);
                if (!force && request_timestamp - last_request <
                    ($rootScope.GlobalConfigs.loginStaticsInterval.current * 1000)) {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(angular.extend(
                            $sessionStorage['loginStatics_' + params.sysID], { cached: false }
                        ));
                    }
                    return false;
                } else {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(angular.extend(
                            $sessionStorage['loginStatics_' + params.sysID], { cached: true }
                        ));
                    }
                }
            }
            $timeout(function() {
                angular.extend($sessionStorage['loginStatics_' + params.sysID], { last_request: request_timestamp });
            }, 0);
        }
        $http.get('api/system/id/' + params.sysID + '/login_statics/check')
            .success(function(response) {
                if (response.error_code == 0) {
                    if ($sessionStorage.hasOwnProperty('loginStatics_' + params.sysID)) {
                        $timeout(function() {
                            angular.merge($sessionStorage['loginStatics_' + params.sysID], response.data);
                        })
                    } else {
                        $timeout(function() {
                            $sessionStorage['loginStatics_' + params.sysID] = angular.merge(
                                response.data, { last_request: request_timestamp }
                            );
                        });
                    }
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            })
            .error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
        return true;
    }

    this.LoginList = function(params) {
        if (params.sysID === undefined) {
            return;
        }
        $http.get('api/system/id/' + params.sysID + '/login_statics')
            .success(function(response) {
                if (response.error_code == 0) {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            })
            .error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            })
    }

    this.ClientSessionCheck = function(params, force = false) {
        if (params.sysID === undefined) {
            return false;
        }
        var request_timestamp = new Date().getTime();
        if ($sessionStorage.hasOwnProperty('clientSessions_' + params.sysID)) {
            if ($sessionStorage['clientSessions_' + params.sysID].hasOwnProperty('last_request')) {
                last_request = parseInt($sessionStorage['clientSessions_' + params.sysID].last_request);
                if (!force && request_timestamp - last_request <
                    ($rootScope.GlobalConfigs.sessionStaticsInterval.current * 1000)) {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(angular.extend(
                            $sessionStorage['clientSessions_' + params.sysID], { cached: false }
                        ));
                    }
                    return false;
                } else {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(angular.extend(
                            $sessionStorage['clientSessions_' + params.sysID], { cached: true }
                        ));
                    }
                }
            }
            $timeout(function() {
                angular.extend(
                    $sessionStorage['clientSessions_' + params.sysID], { last_request: request_timestamp }
                );
            }, 0);
        }
        $http.get('api/system/id/' + params.sysID + '/user_sessions')
            .success(function(response) {
                if (response.error_code == 0) {
                    if ($sessionStorage.hasOwnProperty('clientSessions_' + params.sysID)) {
                        $timeout(function() {
                            angular.merge($sessionStorage['clientSessions_' + params.sysID], response.data);
                        })
                    } else {
                        $timeout(function() {
                            $sessionStorage['clientSessions_' + params.sysID] = angular.merge(
                                response.data, { last_request: request_timestamp }
                            );
                        });
                    }
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            })
            .error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
        return true;
    }
})