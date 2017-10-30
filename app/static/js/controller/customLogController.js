app.controller('customLogController', ['$scope', '$http', function($scope, $http){
    $scope.servers = [];
    $http.get('api/system/id/3/customlogs')
        .success(function(response){
            if (response.error_code === 0) {
                $scope.servers = response.data.records;
            }
        })
        .error(function(response){

        });
}]);
