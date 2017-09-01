app.controller('sysStaticsControl', ['$scope', '$systems', '$interval', '$routeParams', '$rootScope', function($scope, $systems, $interval, $routeParams, $rootScope) {
    $scope.sysShowDetail = true;
    var sys_id;
    if ($routeParams.hasOwnProperty('sysid')) {
        sys_id = $routeParams.sysid;
    } else {

    }
    $scope.checkProc = function(force) {
        if (force === undefined) {
            force = false;
        }
        var started = $systems.SystemStaticsCheck({
            sysID: sys_id,
            onSuccess: function(data) {
                $scope.systemStatics = data.records;
                if (data.cached !== true) {
                    $scope.checking = false;
                }
            },
            onError: function() {
                $scope.checking = false;
            }
        }, force);
        if (started) {
            $scope.checking = true;
            angular.forEach($scope.systemStatics, function(value1, index1) {
                angular.forEach(value1.detail, function(value2, index2) {
                    value2.status.stat = 'checking';
                    angular.forEach(value2.sockets, function(value3, index3) {
                        value3.status.stat = '检查中...';
                    });
                    angular.forEach(value2.connections, function(value4, index4) {
                        value4.status.stat = '检查中...';
                    });
                });
            });
        }
    };

    $scope.checkRefreshInterval = function() {
        var interval = $scope.GlobalConfigs.sysStaticsInterval.current;
        if (isNaN(interval) || interval < 30) {
            $scope.GlobalConfigs.sysStaticsInterval.current =
                $scope.GlobalConfigs.sysStaticsInterval.default;
            return;
        } else {
            $interval.cancel($scope.sysStaticInterval);
            $scope.autoRefresh();
        }
    };
    $scope.autoRefresh = function() {
        if ($scope.auto) {
            $scope.sysStaticInterval = $interval(
                $scope.checkProc,
                $rootScope.GlobalConfigs.sysStaticsInterval.current * 1000
            );
            $scope.checkProc();
        } else {
            $interval.cancel($scope.sysStaticInterval);
        }
    };

    $scope.$on('$destory', function() {
        $interval.cancel($scope.sysStaticInterval);
    });

    $systems.SystemList({
        sysID: sys_id,
        onSuccess: function(data) {
            $scope.systemStatics = data.records;
            $scope.checkProc();
        },
        onError: function() {
            $scope.checking = false;
        }
    });
}]);