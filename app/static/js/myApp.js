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
                //$rootScope.$apply();
                //$rootScope.$digest();
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
                    $rootScope.$apply(function() {
                        $rootScope.Messages.public.push(msg.data);
                    })
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
        public: []
    };
});
app.controller('dashBoardControl', ['$scope', '$rootScope', function($scope, $rootScope) {
    $rootScope.isShowSideList = false;
}]);
app.controller('svrStaticsControl', ['$scope', '$http', 'globalVar', '$interval', function($scope, $http, globalVar, $interval) {
    $scope.checking = true;
    $scope.checkSvrStatics = function() {
        $scope.checking = true;
        $http.get('api/system/id/' + globalVar.sysid + '/svr_statics/check')
            .success(function(response) {
                if (response.sys_id == globalVar.sysid) {
                    $scope.serverStatics = response.details;
                    $scope.serverStatics.showMountDetail = [];
                    angular.forEach(response.details.disks, function(value, index) {
                        $scope.serverStatics.showMountDetail.push(false);
                    });
                }
                $scope.checking = false;
            });
    };
    $http.get('api/system/id/' + globalVar.sysid + '/svr_statics')
        .success(function(data) {
            console.log(data);
            if (globalVar.current_type == 'sysid') {
                if (data.sys_id == globalVar.sysid) {
                    $scope.serverStatics = data.details;
                    $scope.checkSvrStatics();
                    var svrStaticInterval = $interval(function() { $scope.checkSvrStatics(); }, 60000);
                    globalVar.intervals.push(svrStaticInterval);
                }
                $scope.checking = false;
            }
        });
}]);
app.controller('sysStaticsControl', ['$scope', '$http', 'globalVar', '$interval', function($scope, $http, globalVar, $interval) {
    $scope.checking = true;
    $scope.checkProc = function() {
        $scope.checking = true;
        $http.get('api/system/id/' + globalVar.sysid + '/sys_statics/check')
            .success(function(response) {
                $scope.systemStatics = response;
                $scope.checking = false;
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
app.controller('sideBarCtrl', ['$scope', '$http', '$timeout', 'globalVar', '$rootScope', '$location', function($scope, $http, $timeout, globalVar, $rootScope, $location) {
    $scope.tabList = [];
    var idList = [];
    $http.get('api/UI/sideBarCtrl').success(function(data) {
        $scope.listName = data;
    });
    $scope.showListChild = function(id) {
        $rootScope.isShowSideList = true;
        globalVar.current_type = 'sysid';
        globalVar.sysid = id;
        angular.forEach($scope.listName, function(value, index) {
            if (value.id == id) {
                $scope.listName[index].isShow = !$scope.listName[index].isShow;
            } else {
                $scope.listName[index].isShow = false;
            }
        });
    };
    $scope.showListChange = function(id) {
        $rootScope.isShowSideList = true;
        globalVar.current_type = 'sysid';
        globalVar.sysid = id;
        angular.forEach($scope.tabList, function(value, index) {
            value.active = "";
            if (idList.indexOf(value.id) == -1) {
                idList.push(value.id);
            }
        });
        angular.forEach($scope.listName, function(value, index) {
            if (value.id == id) {
                $scope.listName[index].isShow = !$scope.listName[index].isShow;
                if (idList.indexOf($scope.listName[index].id) == -1) {
                    $scope.tabList.push({
                        "id": $scope.listName[index].id,
                        "name": $scope.listName[index].name,
                        "active": "am-active",
                        "Url": $scope.listName[index].Url
                    });
                } else {
                    angular.forEach($scope.tabList, function(tab) {
                        if (tab.id == id) {
                            tab.active = "am-active";
                        }
                    });
                }
            } else {
                $scope.listName[index].isShow = false;
            }
        });
    };
    $scope.tabChangeActive = function(id) {
        $rootScope.isShowSideList = true;
        globalVar.sysid = id;
        angular.forEach($scope.tabList, function(value) {
            value.active = "";
            if (value.id == id) {
                value.active = "am-active";
            }
        });
    };
    $scope.tabDelete = function(id) {
        $rootScope.isShowSideList = true;
        angular.forEach($scope.tabList, function(data, index) {
            if (data.id == id) {
                $scope.tabList.splice(index, 1);
                idList.splice(index, 1);
            }
        });
        var length = $scope.tabList.length;
        if (length > 0) {
            var set = true;
            angular.forEach($scope.tabList, function(value, index) {
                if (value.active == "am-active") set = false;
            });
            if (set)
                $scope.tabList[length - 1].active = "am-active";
            globalVar.sysid = $scope.tabList[length - 1].id;
            var LocationUrl = $scope.tabList[length - 1].Url;
            LocationUrl = LocationUrl.substring(1, LocationUrl.length);
            LocationUrl = '/' + LocationUrl;
            $location.url(LocationUrl);
        } else {
            $location.url('/dashboard');
        }
    };
    $scope.clearTabList = function() {
        if ($rootScope.isShowSideList === false) {
            idList.splice(0, idList.length);
            $scope.tabList.splice(0, $scope.tabList.length);
            return false;
        } else {
            $rootScope.isShowSideList = true;
            return true;
        }
    };
    $scope.operateChange = function(id) {
        globalVar.grpid = id;
        globalVar.current_type = 'grpid';
        $rootScope.isShowSideList = false;
    };
}]);
app.controller('opGroupController', ['$scope', '$http', '$timeout', 'globalVar', function($scope, $http, $timeout, globalVar) {
    $http.get('api/op_group/id/' + globalVar.grpid).success(function(list) {
        $scope.opList = list;
    });
    /*
    $scope.confirm = function(index) {
        if (index < $scope.opList.details.length - 1) {
            $scope.opList.details[index + 1].enabled = true;
        }
    }*/
    $scope.confirm = function(index) {
        $('#result' + index).modal({
            relatedTarget: this,
            onConfirm: function() {
                $scope.$apply(function() {
                    if (index < $scope.opList.details.length - 1) {
                        $scope.opList.details[index + 1].enabled = true;
                    }
                    $scope.opList.details[index].checker.checked = true;
                });
            }
        });
    };
    $scope.check_result = function(index) {
        $('#result' + index).modal({ relatedTarget: this });
    };
    $scope.skip = function(index) {
        if (index < $scope.opList.details.length - 1) {
            $scope.opList.details[index + 1].enabled = true;
        }
        for (var i = 0; i <= index; i++) {
            $scope.opList.details[i].skip = false;
        }
    };
    $scope.execute = function(index, id) {
        $http.get('api/operation/id/' + id).success(function(data) {
            if (globalVar.current_type == 'grpid') {
                $scope.opList.details[index] = data;
                if (index < $scope.opList.details.length - 1 && !$scope.opList.details[index].checker.isTrue) {
                    $scope.opList.details[index + 1].enabled = data.succeed;
                }
                console.log(data);
            }
        });
    };
}]);
app.controller('loginStaticsControl', ['$scope', '$http', 'globalVar', '$rootScope', '$interval', function($scope, $http, globalVar, $rootScope, $interval) {
    if ($rootScope.LoginStatics === undefined) {
        $rootScope.LoginStatics = {};
    }
    $scope.$watch('$rootScope.LoginStatics', function(newValue, oldValue) {
        $scope.$apply(function() {
            $scope.loginStatics = $rootScope.LoginStatics[globalVar.sysid];
        });
    }, true);
    $scope.CheckLoginLog = function() {
        $scope.checking = true;
        $http.get('api/system/id/' + globalVar.sysid + '/login_statics/check').success(function(data) {
            if (globalVar.current_type == 'sysid') {
                angular.forEach(data, function(value1, index1) {
                    angular.forEach($rootScope.LoginStatics[globalVar.sysid], function(value2, index2) {
                        if (value1.seat_id == value2.seat_id) {
                            $rootScope.LoginStatics[globalVar.sysid][index2].seat_status = value1.seat_status;
                            $rootScope.LoginStatics[globalVar.sysid][index2].conn_count = value1.conn_count;
                            $rootScope.LoginStatics[globalVar.sysid][index2].disconn_count = value1.disconn_count;
                            $rootScope.LoginStatics[globalVar.sysid][index2].login_fail = value1.login_fail;
                            $rootScope.LoginStatics[globalVar.sysid][index2].login_success = value1.login_success;
                        }
                    });
                });
                $scope.checking = false;
            }
        });
    };
    $http.get('api/system/id/' + globalVar.sysid + '/login_statics').success(function(data) {
        $rootScope.LoginStatics[globalVar.sysid] = data;
        $scope.loginStatics = $rootScope.LoginStatics[globalVar.sysid];
        $scope.CheckLoginLog();
        var loginStaticInterval = $interval(function() { $scope.CheckLoginLog(); }, 30000);
        globalVar.intervals.push(loginStaticInterval);
    });
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

}]);
app.controller('messageControl', ['$scope', '$rootScope', function($scope, $rootScope) {
    $scope.$watchCollection('$rootScope.Messages', function() {
        if ($rootScope.Messages.public === undefined) {
            $rootScope.Messages.public = [];
        }
        $scope.$apply(function() {
            $scope.messages = $rootScope.Messages.public;
        });
    });
}]);
app.filter('KB2', function() {
    return function(value, dst) {
        var num = parseInt(value);
        switch (dst) {
            case "M":
                return (num / 1024).toFixed(2).toString() + " MB";
            case "G":
                return (num / (1024 * 1024)).toFixed(2).toString() + " GB";
            default:
                return (num / 1024).toFixed(2).toString() + " MB";
        }
    };
});
app.filter('percent', function() {
    return function(value, len) {
        var num = parseFloat(value);
        var fix = 2;
        if (len !== undefined) {
            fix = len;
        }
        return num.toFixed(fix).toString() + " %";
    };
});
app.filter('mask', function() {
    return function(str) {
        var len = str.length;
        if (len > 3) {
            return str.substring(0, len - 3) + '***';
        } else {
            var mask = '';
            for (var i = 0; i < len - 1; i++) { mask += '*'; }
            return str[0] + mask;
        }
    };
});
app.filter('status', function() {
    return function(stat) {
        if (stat != "stopped") {
            switch (stat[0]) {
                case 'D':
                    return '不可中断 ';
                case 'R':
                    return '运行中';
                case 'S':
                    return '休眠';
                case 'T':
                    return '已停止';
                case 'Z':
                    return '僵尸进程';
                default:
                    return '未知';
            }
        } else {
            return '未启动';
        }
    };
});
app.filter('exe_result', function() {
    return function(value) {
        switch (value) {
            case -1:
                return "未执行";
            case 0:
                return "执行完毕";
            case -2:
                return "执行中...";
            case -3:
                return "跳过执行";
            case 1:
                return "执行失败";
            default:
                return "状态未知";
        }
    };
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