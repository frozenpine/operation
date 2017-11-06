app.service('$datasources', function($http, $message) {
    this.getCustomLogs = function() {

    };

    this.getDsType = function() {
        return {
            SQL: {id: 1, name: 'SQL数据库'},
            FILE: {id: 2, name: '日志文件'}
        };
    };

    this.getDsModel = function(type_id) {
        switch(type_id) {
            case undefined:
                return {};
            case 2:
                return {
                    Custom: {id: 0, name: '自定义'},
                    Seat: {id: 1, name: '席位信息'}
                };
            default:
                return {
                    Custom: {id: 0, name: '自定义'},
                    Seat: {id: 1, name: '席位信息'},
                    Session: {id: 2, name: '登录会话'}
                };
        }
    };

    this.AddDataSource = function(params) {
        $http.post('api/datasources', data=params.data)
            .success(function(response){
                if (response.error_code === 0) {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            })
            .error(function(response){
                console.log(response);
                $message.Alert(response.message);
            });
    };
});
