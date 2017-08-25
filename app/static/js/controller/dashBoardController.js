app.controller('dashBoardController', ['$scope', '$rootScope', '$uidatas', '$timeout', function($scope, $rootScope, $uidatas, $timeout) {
    $rootScope.isShowSideList = false;
    $scope.checking = false;
    $scope.getInventory = function() {
        $scope.checking = true;
        $uidatas.Inventory({
            onSuccess: function(data) {
                $timeout(function() {
                    $scope.inventory = data.records;
                }, 0);
                $scope.checking = false;
            }
        });
    };
    $scope.getInventory();

    $scope.CheckProcVersionCallback = function(data) {
        $scope.getInventory();
    };

    $scope.bindPopup = function(proc) {
        $('#' + proc.proc_uuid).popover({
            content: proc.proc_name + '<br/>' + proc.proc_ver,
            trigger: "hover focus"
        });
    };
}]);