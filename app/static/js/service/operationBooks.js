app.service("$operationBooks", ["$http", '$message', function($http, $message) {
    this.operationBookSystemsGet = function(params) {
        $http.get('api/systems')
            .success(function(response) {
                if (response.error_code === 0) {
                    params.onSuccess(response.data);
                }
            })
            .error(function(response) {
                console.log(response);
                // $message.Alert(response.message);
            });
    };

    this.operationBookSystemListGet = function(params) {
        $http.get('api/system/id/' + params.sys_id + '/systems')
            .success(function(response) {
                if (response.error_code === 0)
                    params.onSuccess(response.data);
            }).error(function(response) {
                console.log(response);
                // $message.Alert(response.message);
            });
    };

    this.operationCatalogs = function(params) {
        $http.get('/api/operation-catalogs')
            .success(function(response) {
                if (response.error_code === 0)
                    params.onSuccess(response.data);
                else {
                    params.onError(response.message);
                }
            }).error(function(response) {
                console.log(response);
                // $message.Alert(response.message);
            });
    };

    this.operationbookGet = function(params) {
        $http.get('api/operation-book/id/' + params.optBook_id)
            .success(function(response) {
                if (response.error_code === 0) {
                    params.onSuccess(response.data);
                } else {
                    params.onError(response.message);
                }
            }).error(function(response) {
                console.log(response);
                // $message.Alert(response.message);
            });
    };

    this.operationbooksPut = function(params) {
        $http.put('api/operation-book/id/' + params.optBook_id, data = params.data)
            .success(function(response) {
                if (response.error_code === 0) {
                    params.onSuccess(response.data);
                } else {
                    params.onError(response.message);
                }
            }).error(function(response) {
                console.log(response);
                // $message.Alert(response.message);
            });
    };

    this.operationbookCheck = function(params) {
        $http.post('api/system/id/' + params.sys_id + '/operation-book/script-check', data = params.data)
            .success(function(response) {
                if (response.error_code === 0) {
                    params.onSuccess(response.data);
                } else {
                    params.onError(response);
                }
            }).error(function(response) {
                console.log(response);
                // $message.Alert(response.message);
            });
    };

    this.operationbookDefinePost = function(params) {
        $http.post('api/operation-books', data = params.data)
            .success(function(response) {
                if (response.error_code === 0) {
                    params.onSuccess(response.data);
                } else {
                    params.onError(response.message);
                }
            }).error(function(response) {
                console.log(response);
                // $message.Alert(response.message);
            });
    };
    this.systemOptionBooksGet = function(params) {
        $http.get('api/system/id/' + params.sys_id + '/operation-books')
            .success(function(response) {
                if (response.error_code === 0) {
                    params.onSuccess(response.data);
                } else {
                    params.onError(response.message);
                }
            }).error(function(response) {
                console.log(response);
                // $message.Alert(response.message);
            });
    };
    this.systemOptionGroupPost = function(params) {
        $http.post('api/operation-groups', data = params.data)
            .success(function(response) {
                if (response.error_code === 0) {
                    params.onSuccess(response.data);
                } else {
                    params.onError(response.message);
                }
            }).error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
    };
    this.optionGroupEditPut = function(params) {
        $http.put('api/operation-group/id/' + params.optionGroup_id, data = params.data)
            .success(function(response) {
                if (response.error_code === 0) {
                    params.onSuccess(response.data);
                } else {
                    params.onError(response.message);
                }
            }).error(function(response) {
                console.log(response);
                // $message.Alert(response.message);
            });
    };
    this.operationRecordsPost = function(params) {
        $http.get('api/operate-records')
            .success(function(response) {
                params.onSuccess(response.data);
            }).error(function(response) {
                console.log(response);
            });
    };
    this.operationBookEditPut = function(params) {
        $http.put('api/operation-books', data = params.data)
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
}]);