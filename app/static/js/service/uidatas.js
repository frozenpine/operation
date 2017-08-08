var app = angular.module('myApp');
app.service('$uidatas', function ($http, $message) {
    this.SideBarList = function (params) {
        $http.get('api/UI/sideBarCtrl')
            .success(function (response) {
                if (response.error_code === 0) {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            })
            .error(function (response) {
                console.log(response);
                $message.Alert(response.message);
            });
    };
});