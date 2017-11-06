app.controller('customLogController', ['$scope', '$http', function($scope, $http){
    $scope.checking = true;
    $http.get('api/system/id/3/customlogs')
        .success(function(response){
            console.log(response);
            if (response.error_code === 0) {
                $scope.servers = response.data.records;
                $scope.checking = false;
            }
        })
        .error(function(response){
            $scope.checking = false;
            $scope.servers = [];
        });
}]);
