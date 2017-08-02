var app = angular.module('myApp');
app.controller('Privileges', ['$rootScope', '$operationBooks', '$scope', function($rootScope, $operationBooks, $scope) {
    //    $scope.currentId = null;
    $scope.$watch('currentId', function(scope) {
        if ($scope.currentId) {
            $operationBooks.operationPriviGet({
                currentId: $scope.currentId,
                onSuccess: function(res) {
                    $rootScope.privileges = res.privileges;
                    console.log($rootScope.privileges);
                },
                onError: function(res) {
                    console.log(res);
                }
            });
        }
    });
}]);