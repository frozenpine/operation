app.controller('dsController', ['$scope', '$ds', function($scope, $ds){
    $scope.systemList = [];
    $scope.dataSourceDefine = $ds.getDsDefault();
}]);
