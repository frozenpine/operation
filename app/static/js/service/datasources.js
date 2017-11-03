app.service('$datasources', function($http) {
    this.getDsDefault = function(){
        return angular.copy({
            name: undefined,
            description: undefined,
            sys_id: undefined,
            src_type: undefined,
            src_model: undefined,
            charset: 'utf8'
        });
    };

    this.getDsType = function(){
        return angular.copy({
            SQL: {id: 1, name: 'SQL数据库'},
            FILE: {id: 2, name: '日志文件'}
        });
    };

    this.getDsModel = function(type_id){
        switch(type_id) {
            case undefined:
                return angular.copy({});
            case 2:
                return angular.copy({
                    Custom: {id: 0, name: '自定义'},
                    Seat: {id: 1, name: '席位信息'}
                });
            default:
                return angular.copy({
                    Custom: {id: 0, name: '自定义'},
                    Seat: {id: 1, name: '席位信息'},
                    Session: {id: 2, name: '登录会话'}
                });
        }
    };
});
