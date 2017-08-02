var app = angular.module('myApp');
app.service('$operations', function($websocket, $http, $message, $sessionStorage) {
    this.Detail = function(params) {
        $http.get('api/op_group/id/' + params.groupID)
            .success(function(response) {
                if (response.error_code == 0) {
                    params.onSuccess(response.data);
                } else {
                    $message.Warning(response.message);
                }
            })
            .error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
    }
    this.InitQueue = function(params) {
        $http.post('api/op_group/id/' + params.groupID)
            .success(function(response) {
                if (response.err_code == 0) {
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
    this.ResumeQueue = function(params) {
        $http.get('api/op_group/id/' + params.groupID + '/restoration')
            .success(function(response) {
                if (response.error_code == 0) {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response);
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
            })
    }
    this.SkipCurrent = function(params) {}
    this.Snapshot = function(params) {
        $http.get('api/op_group/id/' + params.groupID + '/snapshot')
            .success(function(response) {
                if (response.err_code == 0) {
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
    }
    this.RunNext = function(params) {
        $http.get(
                'api/operation/id/' + params.operationID,
                headers = {
                    Authorizor: JSON.stringify(params.authorizor)
                }
            )
            .success(function(response) {
                if (response.error_code == 0) {
                    response.data.exec_code = -4;
                    params.onSuccess(response.data);
                } else {
                    console.log(response)
                    if (params.hasOwnProperty('onError')) {
                        params.onError(response.message);
                    } else {
                        $message.Warning(response.message);
                    }
                }
            })
            .error(function(response) {
                console.log(response);
                if (response.hasOwnProperty('message')) {
                    $message.Alert(response.message);
                }
            });
    }
    this.RunAll = function(params) {
        $http.get('api/op_group/id/' + params.groupID + '/all')
            .success(function(response) {
                if (response.error_code == 0) {
                    params.onSuccess(response.data);
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response.data);
                } else {
                    $message.Warning(response.message);
                }
            })
            .error(function(response) {
                console.log(response);
                if (response.hasOwnProperty('message')) {
                    $message.Alert(response.message);
                }
            });
    }
});