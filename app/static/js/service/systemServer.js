var app = angular.module('myApp');
app.service("$systemServer", ["$http", "$message", function($http, $message) {
    this.addServer = function(params) {
        $http.post('api/servers/', data = params.data)
            .success(function(response) {
                if (response.error_code === 0) {
                    params.onSuccess(response.data);
                } else {
                    params.onError(response.message);
                }
            }).error(function(response) {
                console.log(response);
                $message.ModelAlert(response.message, "modalInfoShowAddSer");
            });
    };
    this.serversGet = function(params) {
        $http.get('api/servers')
            .success(function(response) {
                if (response.error_code === 0) {
                    params.onSuccess(response.data);
                }
            })
            .error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
    };
    this.systemTypesGet = function(params) {
        $http.get('api/system-types')
            .success(function(response) {
                if (response.error_code === 0) {
                    params.onSuccess(response.data);
                }
            })
            .error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
    };
    this.systemVendorGet = function(params) {
        $http.get('api/vendors')
            .success(function(response) {
                if (response.error_code === 0) {
                    params.onSuccess(response.data);
                }
            })
            .error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
    };
    this.addSystem = function(params) {
        $http.post('api/systems', data = params.data)
            .success(function(response) {
                if (response.error_code === 0) {
                    params.onSuccess(response.data);
                } else {
                    params.onError(response.message);
                }
            }).error(function(response) {
                console.log(response);
                $message.ModelAlert(response.message, "modalInfoShowAddSer");
            });
    };
    this.getProcess = function(params) {
        $http.get('api/processes')
            .success(function(response) {
                if (response.error_code === 0) {
                    params.onSuccess(response.data);
                }
            })
            .error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
    };
    this.addProcess = function(params) {
        $http.post('api/processes', data = params.data)
            .success(function(response) {
                if (response.error_code === 0) {
                    params.onSuccess(response.data);
                } else {
                    params.onError(response.message);
                }
            }).error(function(response) {
                console.log(response);
            });
    };
    this.editServer = function(params) {
        $http.put('api/server/id/' + params.id, data = params.data)
            .success(function(response) {
                if (response.error_code === 0) {
                    params.onSuccess(response.data);
                } else {
                    params.onError(response.message);
                }
            }).error(function(response) {
                console.log(response);
            });
    };
    this.editSystem = function(params) {
        $http.put('api/system/id/' + params.id, data = params.data)
            .success(function(response) {
                if (response.error_code === 0) {
                    params.onSuccess(response.data);
                } else {
                    params.onError(response.message);
                }
            }).error(function(response) {
                console.log(response);
            });
    };
    this.getSystem = function(params) {
        $http.get('api/system/id/' + params.id)
            .success(function(response) {
                if (response.error_code === 0) {
                    params.onSuccess(response.data);
                } else {
                    params.onError(response.message);
                }
            }).error(function(response) {
                console.log(response);
            });
    };
    this.getSystemTree = function(params) {
        $http.get('api/system/tree-structure')
            .success(function(response) {
                params.onSuccess(response);
            })
            .error(function(response) {
                console.log(response);
            });
    };
}]);