app.service('$users', function ($http, $message) {
    this.ModifyPassword = function (params) {
        if (params.hasOwnProperty('userID')) {
            $http.put('api/user/id/' + params.userID, data = params.data)
                .success(function (response) {
                    if (response.error_code === 0) {
                        if (params.hasOwnProperty('onSuccess')) {
                            params.onSuccess(response);
                        }
                    } else if (params.hasOwnProperty('onError')) {
                        params.onError(response);
                    }
                })
                .error(function (response) {
                    console.log(response);
                    if (response.hasOwnProperty('message')) {
                        $message.Alert(response.message);
                    }
                });
        } else {
            $message.Alert('用户ID未定义！');
        }
    };

    this.GetPrivileges = function (params) {
        if (params.hasOwnProperty('userID')) {
            $http.get('api/user/id/' + params.userID)
                .success(function (response) {
                    if (response.error_code === 0) {
                        if (params.hasOwnProperty('onSuccess')) {
                            params.onSuccess(response.data);
                        }
                    } else if (params.hasOwnProperty('onError')) {
                        params.onError(response.data);
                    }
                })
                .error(function (response) {
                    console.log(response);
                    if (response.hasOwnProperty('message')) {
                        $message.Alert(response.message);
                    }
                });
        } else {
            $message.Alert('用户ID未定义！');
        }
    };
});