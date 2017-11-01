app.controller('customSqlController', ['$scope', '$http', function($scope, $http){
    $scope.dbs = [];
    $http.get('api/system/id/3/customsqls')
        .success(function(response){
            console.log(response);
            if (response.error_code === 0) {
                $scope.dbs = response.data.records;
            }
        })
        .error(function(response){

        });
}]);
