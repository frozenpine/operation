var app = angular.module('myApp');
app.controller('userController', ['$scope', '$http', '$rootScope', '$operationBooks', function($scope, $http, $rootScope, $operationBooks) {
    $scope.ModifyPassword = function(usr_id) {
        $('#modifyPassword').modal({
            relatedTarget: this,
            onConfirm: function() {
                $http.put('api/user/id/' + usr_id, data = {
                    old_password: $('#oldPwd').val(),
                    password: $('#newPwd').val()
                }).success(function(response) {
                    console.log(response);
                }).error(function(response) {
                    console.log(response);
                });
                $('#oldPwd').val('');
                $('#newPwd').val('');
            }
        });
    };
}]);