app.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/dashboard', {
            templateUrl: 'UI/views/dashboard'
        })
        .when('/op_records', {
            templateUrl: 'UI/views/op_records'
        })
        .when('/sys_ser', {
            templateUrl: 'UI/views/sys_ser_pro'
        })
        .when('/statics/:sysid', {
            templateUrl: 'UI/views/statics'
        })
        .when('/system/:sysid/op_group/:grpid', {
            templateUrl: 'UI/views/op_group'
        })
        .when('/system/:sysid/operate-books', {
            templateUrl: 'UI/views/operate-books'
        })
        .otherwise({
            redirectTo: '/dashboard'
        });
}]);