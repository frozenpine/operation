app.controller('loginStaticsControl', ['$scope', '$systems', '$interval', '$timeout', '$routeParams', '$rootScope', function($scope, $systems, $interval, $timeout, $routeParams, $rootScope) {
    $scope.loginShowDetail = true;
    $scope.loginStaticsShow = false;
    $scope.CheckLoginLog = function(force = false) {
        var started = $systems.LoginStaticsCheck({
            sysID: $routeParams.sysid,
            onSuccess: function(data) {
                angular.forEach(data.records, function(rspValue, rspIndex) {
                    angular.forEach($scope.loginStatics, function(value, index) {
                        if (rspValue.seat_id == value.seat_id) {
                            angular.merge(value, rspValue);
                        }
                    })
                });
                if (data.cached != true) {
                    $scope.checking = false;
                }
            },
            onError: function() {
                $scope.checking = false;
            }
        }, force);
        if (started) {
            $scope.checking = true;
        }
    };
    $rootScope.$watch('GlobalConfig.loginStaticsInterval.current', function(newValue, oldValue) {
        if (newValue != oldValue) {
            if (isNaN(newValue) || newValue < 30) {
                $scope.GlobalConfigs.loginStaticsInterval.current =
                    $scope.GlobalConfigs.loginStaticsInterval.default;
                return;
            } else {
                $interval.cancel($scope.loginStaticInterval);
                $scope.autoRefresh();
            }
        }
    }, true);
    $scope.autoRefresh = function() {
        if ($scope.auto) {
            $scope.loginStaticInterval = $interval(
                function() { $scope.CheckLoginLog(); },
                $rootScope.GlobalConfigs.loginStaticsInterval.current * 1000
            );
            $scope.CheckLoginLog();
        } else {
            $interval.cancel($scope.loginStaticInterval);
        }
    };
    $scope.$on('$destory', function() {
        $interval.cancel($scope.loginStaticInterval);
    })

    $systems.LoginList({
        sysID: $routeParams.sysid,
        onSuccess: function(data) {
            $scope.loginStaticsShow = true;
            $scope.loginStatics = data.records;
            $scope.CheckLoginLog();
        }
    })
}]);