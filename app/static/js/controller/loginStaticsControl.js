app.controller('loginStaticsControl', ['$scope', '$systems', '$interval', '$timeout', '$routeParams', '$rootScope', function($scope, $systems, $interval, $timeout, $routeParams, $rootScope) {
    $scope.loginShowDetail = true;
    $scope.loginStaticsShow = false;
    $scope.CheckLoginLog = function(force) {
        if (force === undefined) {
            force = false;
        }
        var started = $systems.LoginStaticsCheck({
            sysID: $routeParams.sysid,
            onSuccess: function(data) {
                if (data.records.length > 0) {
                    angular.forEach(data.records, function(rspValue, rspIndex) {
                        angular.forEach($scope.loginStatics, function(value, index) {
                            if (rspValue.seat_id == value.seat_id) {
                                angular.merge(value, rspValue);
                            }
                        });
                    });
                } else {
                    var request_time;
                    if (data.hasOwnProperty('last_request')) {
                        request_time = new Date(parseInt(data.last_request));
                    }
                    var merge_data = {
                        conn_count: 0,
                        disconn_count: 0,
                        login_fail: 0,
                        login_success: 0,
                        seat_status: '未连接',
                    };
                    if (request_time !== undefined) {
                        data.updated_time = request_time.getHours() + ':' + request_time.getMinutes() + ':' + request_time.getSeconds();
                    }
                    angular.forEach($scope.loginStatics, function(value, index) {
                        angular.merge(value, merge_data);
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
            $scope.checking = true;
        }
    };

    $scope.checkRefreshInterval = function() {
        var interval = $scope.GlobalConfigs.loginStaticsInterval.current;
        if (isNaN(interval) || interval < 30) {
            $scope.GlobalConfigs.loginStaticsInterval.current =
                $scope.GlobalConfigs.loginStaticsInterval.default;

        } else {
            $interval.cancel($scope.loginStaticInterval);
            $scope.autoRefresh();
        }
    };
    $scope.autoRefresh = function() {
        if ($scope.auto) {
            $scope.loginStaticInterval = $interval(
                $scope.CheckLoginLog,
                $rootScope.GlobalConfigs.loginStaticsInterval.current * 1000
            );
            $scope.CheckLoginLog();
        } else {
            $interval.cancel($scope.loginStaticInterval);
        }
    };
    $scope.$on('$destory', function() {
        $interval.cancel($scope.loginStaticInterval);
    });

    $systems.LoginList({
        sysID: $routeParams.sysid,
        onSuccess: function(data) {
            $scope.loginStaticsShow = true;
            $scope.loginStatics = data.records;
            $scope.CheckLoginLog();
        }
    });
}]);