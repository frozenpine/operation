var app = angular.module('myApp', ['ngRoute'], function($provide) {
    $provide.factory('globalVar', function() {
        return {
            'sysid': 0,
            'grpid': 0,
            'current_type': 'sysid',
            'intervals': []
        };
    });
    $provide.factory('Message', function($rootScope) {
        $rootScope.Messages = {};
        if ("WebSocket" in window) {
            var ws = new WebSocket("ws://10.9.101.39:5000/websocket");
            ws.onopen = function() {
                console.log("conn success");
                ws.send(JSON.stringify({
                    method: 'subscribe',
                    topic: 'public'
                }));
            };

            ws.onmessage = function(event) {
                onMessage(JSON.parse(event.data));
                $rootScope.$apply();
            };
        } else {
            console.log("WebSocket not supported");
        }

        window.onbeforeunload = function() {
            ws.onclose = function() {
                console.log('unlodad');
            };
            ws.close();
        };

        var onMessage = function(msg) {
            switch (msg.topic) {
                case "public":
                    if ($rootScope.Messages.public === undefined) {
                        $rootScope.Messages.public = [];
                    }
                    $rootScope.Messages.public.push(msg.data);
                    break;
                default:
                    console.log(JSON.stringify(msg));
            }
        };

        return {
            Send: function(msg) {
                ws.send(JSON.stringify(msg));
            }
        };
    });
});
app.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/dashboard', {
            templateUrl: 'UI/views/dashboard',
            controller: 'dashBoardControl'
        })
        .when('/statics/:sysid', {
            templateUrl: 'UI/views/statics',
        })
        .when('/op_group/:grpid', {
            templateUrl: 'UI/views/op_group'
        })
        .otherwise({
            redirectTo: '/dashboard'
        });
}]);
app.run(function($rootScope, $interval, $location, globalVar, Message) {
    $rootScope.tab = 1; //default
    $rootScope.$on('$routeChangeStart', function(evt, next, current) {
        console.log('route begin change');
        angular.forEach(globalVar.intervals, function(value, index) {
            $interval.cancel(value);
        });
        globalVar.intervals = [];
    });
    $rootScope.status = "normal";
    $rootScope.Messenger = Message;
    $rootScope.Messages = {
        'public': []
    };
});
app.controller('dashBoardControl', ['$scope', function($scope) {

}]);
app.controller('svrStaticsControl', ['$scope', '$http', 'globalVar', '$interval', function($scope, $http, globalVar, $interval) {
    $scope.checking = true;
    $scope.checkSvrStatics = function() {
        $scope.checking = true;
        angular.forEach($scope.serverStatics, function(value, index) {
            $http.get('api/server/id/' + value.id + '/statics')
                .success(function(data) {
                    $scope.serverStatics[index] = data;
                    console.log(data);
                    $scope.checking = false;
                });
        });
    };
    $http.get('api/system/id/' + globalVar.sysid + '/svr_statics')
        .success(function(data) {
            if (globalVar.current_type == 'sysid') {
                $scope.serverStatics = data;
                $scope.checkSvrStatics();
                var svrStaticInterval = $interval(function() { $scope.checkSvrStatics(); }, 60000);
                globalVar.intervals.push(svrStaticInterval);
                $scope.checking = false;
            }
        });
}]);
app.controller('sysStaticsControl', ['$scope', '$http', 'globalVar', '$interval', function($scope, $http, globalVar, $interval) {
    $scope.checking = true;
    $scope.checkProc = function() {
        $scope.checking = true;
        angular.forEach($scope.systemStatics, function(value1, index1) {
            angular.forEach(value1.detail, function(value2, index2) {
                $scope.systemStatics[index1].detail[index2].status.stat = "checking...";
                $http.get('api/process/id/' + value2.id + '/statics')
                    .success(function(data) {
                        $scope.systemStatics[index1].detail[index2] = data;
                        $scope.checking = false;
                    });
            });
        });
    };
    $http.get('api/system/id/' + globalVar.sysid + '/sys_statics')
        .success(function(data) {
            if (globalVar.current_type == 'sysid') {
                $scope.systemStatics = data;
                $scope.checkProc();
                var sysStaticInterval = $interval(function() { $scope.checkProc(); }, 30000);
                globalVar.intervals.push(sysStaticInterval);
                $scope.checking = false;
            }
        });
}]);
app.controller('sideBarCtrl', ['$scope', '$http', '$timeout', 'globalVar', function($scope, $http, $timeout, globalVar) {
    $http.get('api/UI/sideBarCtrl').success(function(data) {
        $scope.listName = data;
    });
    $scope.showListChange = function(id) {
        globalVar.sysid = id;
        globalVar.current_type = 'sysid';
        angular.forEach($scope.listName, function(value, index) {
            if (value.id == id)
                $scope.listName[index].isShow = true;
            else
                $scope.listName[index].isShow = false;
        });
    };
    $scope.operateChange = function(id) {
        globalVar.grpid = id;
        globalVar.current_type = 'grpid';
    };
}]);
app.controller('opGroupController', ['$scope', '$http', '$timeout', 'globalVar', function($scope, $http, $timeout, globalVar) {
    $http.get('api/op_group/id/' + globalVar.grpid).success(function(data) {
        $scope.opList = data;
    });
    $scope.execute = function(index, id) {
        $http.get('api/operation/id/' + id).success(function(data) {
            if (globalVar.current_type == 'grpid') {
                $scope.opList.details[index] = data;
                if (index < $scope.opList.details.length - 1)
                    $scope.opList.details[index + 1].enabled = data.succeed;
                if ($scope.results === null || $scope.results === undefined) {
                    $scope.results = data.output_lines;
                } else {
                    angular.forEach(data.output_lines, function(value, index) {
                        $scope.results.push(value);
                    });
                }
                console.log(data);
            }
        });
    };
}]);
app.controller('loginStaticsControl', ['$scope', '$http', 'globalVar', '$interval', function($scope, $http, globalVar, $interval) {
    $scope.checking = true;
    /*
    $scope.CheckLoginLog = function() {
        $scope.checking = true;
        $scope.loginLogs = [{
            'detail': {
                'success': 'checking...'
            }
        }];
        $http.get('api/system/id/' + globalVar.sysid + '/login_logs').success(function(data) {
            if (globalVar.current_type == 'sysid') {
                $scope.loginLogs = data;
                $scope.checking = false;
            }
        });
    };
    $scope.CheckLoginLog();
    var loginLogInterval = $interval(function() { $scope.CheckLoginLog(); }, 60000);
    globalVar.intervals.push(loginLogInterval);
    */
    $http.get('api/system/id/' + globalVar.sysid + '/login_statics').success(function(data) {
        $scope.logins = data;
        $scope.checking = false;
    })
}]);
app.controller('warningCtrl', ['$scope', '$http', function($scope, $http) {
    $scope.isRadioClick = false;
    $scope.tagSele = {
        statusNum: '',
        handleNum: ''
    };
    $http.get('json/warningStatus.json').success(function(data) {
        $scope.warningData = data;
    });
    $scope.outData = [];
    $scope.ischeck = function() {
        $scope.isRadioClick = true;
        $scope.outData = [];
        angular.forEach($scope.warningData, function(o, index, array) {
            if (($scope.tagSele.statusNum == o.statusNum && $scope.tagSele.handleNum == o.handleNum)) {
                $scope.outData.push(o);
                $scope.outData.push(array[index + 1]);
            } else if ($scope.tagSele.statusNum == o.statusNum && $scope.tagSele.handleNum === '') {
                $scope.outData.push(o);
                $scope.outData.push(array[index + 1]);
            } else if ($scope.tagSele.statusNum === '' && $scope.tagSele.handleNum == o.handleNum) {
                $scope.outData.push(o);
                $scope.outData.push(array[index + 1]);
            }
        });
        console.log($scope.outData);
    };
    $scope.clearRadio = function() {
        $scope.isRadioClick = false;
        $scope.tagSele.statusNum = '';
        $scope.tagSele.handleNum = '';
    };
    $scope.showDetail = function(data) {
        angular.forEach($scope.warningData, function(o) {
            if (data.id == o.secId && data.name) {
                o.isDetailShow = !o.isDetailShow;
            }
        });
    };
}]);
app.controller('taskControl', ['$scope', '$rootScope', function($scope, $rootScope) {
    var watcher = $scope.$watchCollection('$rootScope.Messages.public', function() {
        $scope.messages = $rootScope.Messages.public;
        $scope.$apply();
    });
}]);
app.filter('filterStatus', function() {
    //return function (obj) {
    //	var newObj = [];
    //	angular.forEach(obj,function(o){
    //		if(o.id == 7){
    //			newObj.push(o);
    //		}
    //	});
    //	return newObj;
    //}
});
app.directive('echart', [function() {
    return {
        restrict: 'AE',
        scope: {
            echart: '='
        },
        link: link
    };

    function link(scope, element, attr) {
        var myChart = echarts.init(element[0]);
        // 指定图表的配置项和数据
        var defaultOption = {
            title: {
                text: '内存使用率',
                x: 'center'
            },
            tooltip: {
                trigger: 'item',
                formatter: "{a} <br/>{b} : {c} ({d}%)"
            },
            series: [{
                name: '内存使用',
                type: 'pie',
                radius: '55%',
                center: ['50%', '60%'],
                data: [{
                    value: 1000,
                    name: '已使用内存(MB)'
                }, {
                    value: 3100,
                    name: '剩余内存(MB)'
                }],
                itemStyle: {
                    emphasis: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }]
        };
        // 使用刚指定的配置项和数据显示图表。
        myChart.setOption(defaultOption);

        // 双向传值
        // scope.$watch('echart', function(n, o) {
        //  if (n === o || !n) return;
        //  myChart.setOption(n);
        // });

        //当浏览器窗口发生变化的时候调用div的resize方法
        window.addEventListener('resize', chartResize);

        scope.$on('$destory', function() {
            window.removeEventListener('resize', chartResize);
        });

        function chartResize() {
            myChart.resize();
        }
    }
}]);
app.directive('echart2', [function() {
    return {
        restrict: 'AE',
        scope: {
            echart: '='
        },
        link: link
    };

    function link(scope, element, attr) {
        var myChart = echarts.init(element[0]);
        // 指定图表的配置项和数据
        var defaultOption = {
            title: {
                text: '内存使用率',
                x: 'center'
            },
            tooltip: {
                trigger: 'item',
                formatter: "{a} <br/>{b} : {c} ({d}%)"
            },
            series: [{
                name: '内存使用',
                type: 'pie',
                radius: '55%',
                center: ['50%', '60%'],
                data: [{
                    value: 2000,
                    name: '已使用内存(MB)'
                }, {
                    value: 3100,
                    name: '剩余内存(MB)'
                }],
                itemStyle: {
                    emphasis: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }]
        };
        // 使用刚指定的配置项和数据显示图表。
        myChart.setOption(defaultOption);

        // 双向传值
        // scope.$watch('echart', function(n, o) {
        //  if (n === o || !n) return;
        //  myChart.setOption(n);
        // });

        //当浏览器窗口发生变化的时候调用div的resize方法
        window.addEventListener('resize', chartResize);

        scope.$on('$destory', function() {
            window.removeEventListener('resize', chartResize);
        });

        function chartResize() {
            myChart.resize();
        }
    }
}]);