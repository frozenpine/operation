app.controller('clientStaticsControl', ['$scope', '$systems', '$routeParams', '$interval', '$message', '$rootScope', function($scope, $systems, $routeParams, $interval, $message, $rootScope) {
    $scope.clientShowDetail = true;
    $scope.userSessionShow = false;
    $scope.CheckClientSessions = function(force) {
        if (force === undefined) {
            force = false;
        }
        var started = $systems.ClientSessionCheck({
            sysID: $routeParams.sysid,
            onSuccess: function(data) {
                $scope.userSessionShow = true;
                $scope.statusList = data.records;
                if (data.cached !== true) {
                    $scope.checking = false;
                }
            },
            onError: function(data) {
                if (data.hasOwnProperty('message')) {
                    $message.Alert(data.message);
                }
                $scope.checking = false;
            }
        }, force);
        if (started) {
            $scope.checking = true;
        }
    };
    $scope.autoRefresh = function() {
        if ($scope.auto) {
            $scope.clientSessionInterval = $interval(
                function() {
                    $scope.CheckClientSessions();
                }, parseInt($rootScope.sessionStaticsInterval) * 1000
            );
            $scope.CheckClientSessions();
        } else {
            $interval.cancel($scope.clientSessionInterval);
        }
    };
    $scope.$on('$destory', function() {
        $interval.cancel($scope.clientSessionInterval);
    });
    $scope.CheckClientSessions();
}]);