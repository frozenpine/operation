app.service('$ds', ['$scope', '$http', function($scope, $http){
    this.getDsDefault = function(){
        return {
            name: undefined,
            description: undefined,
            sys_id: undefined,
            src_type: undefined,
            src_model: undefined,
            connector: {
                ip: undefined,
                port: undefined,
                login_user: undefined,
                login_pwd: undefined,
                database: undefined,
                charset: 'utf8',
                login_file: undefined,
                module: undefined
            }
        };
    };
}]);
