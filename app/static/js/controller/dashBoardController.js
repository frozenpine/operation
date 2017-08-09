app.controller('dashBoardController', ['$scope', '$rootScope', '$uidatas', '$timeout', function($scope, $rootScope, $uidatas, $timeout) {
    $uidatas.Inventory({
        onSuccess: function(data) {
            $timeout(function() {
                $scope.inventory = data.records;
            }, 0);
        }
    });

    $scope.bindPopup = function(proc) {
        $('#' + proc.proc_uuid).popover({
            content: proc.proc_name + '<br/>' + proc.proc_ver,
            trigger: "hover focus"
        });
    };
}]);