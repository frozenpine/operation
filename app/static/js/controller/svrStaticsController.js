app.controller('svrStaticsControl', ['$scope', '$servers', '$interval', '$routeParams', '$localStorage', '$rootScope', function($scope, $servers, $interval, $routeParams, $localStorage, $rootScope) {
    $scope.svrShowDetail = true;
    var sys_id = $routeParams.sysid;

    $scope.serverList = function() {
        $servers.ServerList({
            sysID: sys_id,
            onSuccess: function(data) {
                $scope.serverStatics = data.details;
                $scope.checkSvrStatics();
            },
            onError: function() {
                $scope.checking = false;
            }
        });
    };

    $scope.serverList();

    $scope.checkSvrStatics = function(force) {
        if (force === undefined) {
            force = false;
        }
        var started = $servers.CheckServerStatics({
            sysID: sys_id,
            onSuccess: function(data) {
                if (data.sys_id == sys_id) {
                    $scope.serverStatics = data.details;
                    $scope.serverStatics.showMountDetail = [];
                    angular.forEach(data.details.disks, function(value, index) {
                        $scope.serverStatics.showMountDetail.push(false);
                    });
                }
                if (data.cached !== true) {
                    $scope.checking = false;
                }
            },
            onError: function() {
                $scope.checking = false;
            }
        }, force);
        if (started) {
            angular.forEach($scope.serverStatics, function(value, index) {
                value.uptime = '检查中...';
            });
            $scope.checking = true;
        }
    };

    $scope.checkRefreshInterval = function() {
        var interval = $scope.GlobalConfigs.svrStaticsInterval.current;
        if (isNaN(interval) || interval < 30) {
            $scope.GlobalConfigs.svrStaticsInterval.current =
                $scope.GlobalConfigs.svrStaticsInterval.default;

        } else {
            $interval.cancel($scope.svrStaticInterval);
            $scope.autoRefresh();
        }
    };
    $scope.autoRefresh = function() {
        if ($scope.auto) {
            $scope.svrStaticInterval = $interval(
                $scope.checkSvrStatics,
                $rootScope.GlobalConfigs.svrStaticsInterval.current * 1000
            );
            $scope.checkSvrStatics();
        } else {
            $interval.cancel($scope.svrStaticInterval);
        }
    };

    $scope.$on('$destroy', function() {
        $interval.cancel($scope.svrStaticInterval);
    });
}]);