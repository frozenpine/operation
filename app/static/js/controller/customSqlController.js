app.controller('customSqlController', ['$scope', '$http', function($scope, $http){
    $scope.checking = true;
    $http.get('api/system/id/3/customsqls')
        .success(function(response){
            console.log(response);
            if (response.error_code === 0) {
                $scope.dbs = response.data.records;
                $scope.checking = false;
            }
        })
        .error(function(response) {
            $scope.checking = false;
            $scope.dbs = [];
        });

    $scope.getCustomSqlDs = function () {

    };
}]);
