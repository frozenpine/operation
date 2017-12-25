var app = angular.module('myApp', ['ngRoute', 'angular-sortable-view', 'ngStorage', 'ngScroll', 'tree.dropdown'], function($provide) {
    $provide.factory('$uuid', function() {
        return {
            uuid4: function() {
                return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, function(c) {
                    return (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16);
                });
            }
        };
    });

    $provide.factory('$message', function($uuid) {
        return {
            ModelSucess: function(msg, moduleID, timeout, id) {
                if (timeout === undefined) {
                    timeout = 3;
                }
                if (id === undefined) {
                    id = $uuid.uuid4();
                }
                $('#' + moduleID).append(
                    '<div class="am-alert" style="margin: 1px 5px; display: none" id="' + id + '">' +
                    '    <p class="am-text-center">' + msg + '</p>' +
                    '</div>'
                );
                $('#' + id).alert();
                $('#' + id).addClass('am-alert-success').show();
                setTimeout(function() {
                    $('#' + id).alert('close');
                }, timeout * 1000);
            },
            ModelAlert: function(msg, moduleID, timeout, id) {
                if (timeout === undefined) {
                    timeout = 3;
                }
                if (id === undefined) {
                    id = $uuid.uuid4();
                }
                $('#' + moduleID).append(
                    '<div class="am-alert" style="margin: 1px 5px; display: none" id="' + id + '">' +
                    '    <p class="am-text-center">' + msg + '</p>' +
                    '</div>'
                );
                $('#' + id).alert();
                $('#' + id).addClass('am-alert-danger').show();
                setTimeout(function() {
                    $('#' + id).alert('close');
                }, timeout * 1000);
            },
            Alert: function(msg, timeout, id) {
                if (timeout === undefined) {
                    timeout = 3;
                }
                if (id === undefined) {
                    id = $uuid.uuid4();
                }
                $('#alertMessage').append(
                    '<div class="am-alert" style="margin: 1px 5px; display: none" id="' + id + '">' +
                    '    <span type="button" class="am-close am-fr">&times;</span>' +
                    '    <p class="am-text-center">' + msg + '</p>' +
                    '</div>'
                );
                $('#' + id).alert();
                $('#' + id).addClass('am-alert-danger').show();
                setTimeout(function() {
                    $('#' + id).alert('close');
                }, timeout * 1000);
            },
            Warning: function(msg, timeout, id) {
                if (timeout === undefined) {
                    timeout = 3;
                }
                if (id === undefined) {
                    id = $uuid.uuid4();
                }
                $('#alertMessage').append(
                    '<div class="am-alert" style="margin: 1px 5px; display: none" id="' + id + '">' +
                    '    <span type="button" class="am-close am-fr">&times;</span>' +
                    '    <p class="am-text-center">' + msg + '</p>' +
                    '</div>'
                );
                $('#' + id).alert();
                $('#' + id).addClass('am-alert-warning').show();
                setTimeout(function() {
                    $('#' + id).alert('close');
                }, timeout * 1000);
            },
            Info: function(msg, timeout, id) {
                if (timeout === undefined) {
                    timeout = 3;
                }
                if (id === undefined) {
                    id = $uuid.uuid4();
                }
                $('#alertMessage').append(
                    '<div class="am-alert" style="margin: 1px 5px; display: none" id="' + id + '">' +
                    '    <span type="button" class="am-close am-fr">&times;</span>' +
                    '    <p class="am-text-center">' + msg + '</p>' +
                    '</div>'
                );
                $('#' + id).alert();
                $('#' + id).show();
                setTimeout(function() {
                    $('#' + id).alert('close');
                }, timeout * 1000);
            },
            Success: function(msg, timeout, id) {
                if (timeout === undefined) {
                    timeout = 3;
                }
                if (id === undefined) {
                    id = $uuid.uuid4();
                }
                $('#alertMessage').html(
                    '<div class="am-alert" style="margin: 1px 5px; display: none" id="' + id + '">' +
                    '    <span type="button" class="am-close am-fr">&times;</span>' +
                    '    <p class="am-text-center">' + msg + '</p>' +
                    '</div>'
                );
                $('#' + id).alert();
                $('#' + id).addClass('am-alert-success').show();
                setTimeout(function() {
                    $('#' + id).alert('close');
                }, timeout * 1000);
            }
        };
    });

    $provide.factory('$dialog', function() {
        return {
            Confirm: function() {

            }
        };
    });

    $provide.factory('$websocket', function($rootScope, $location, $interval, $timeout, $message, $sessionStorage, $uuid) {
        if (!$sessionStorage.hasOwnProperty('messages')) {
            $sessionStorage.messages = [];
        }
        var connected = false;
        var reconnect = false;
        var heartbeat_interval;
        var unload = false;
        var ws;
        var request_list = {};

        var init = function() {
            if ("WebSocket" in window) {
                // if (ws) { delete ws; }
                var websocket_protocol = $location.protocol() == "http" ? "ws://" : "wss://";
                var websocket_uri = websocket_protocol + $location.host() + ":" + $location.port() + "/websocket";
                console.log(websocket_uri);
                ws = new WebSocket(websocket_uri);
                ws.onopen = function() {
                    unload = false;
                    console.log("[Client] Websocket connected successfully.");
                    $message.Success('Websocket连接成功.');
                    connected = true;
                    reconnect = false;
                    ws.send(JSON.stringify({
                        method: 'topics'
                    }));
                    ws.send(JSON.stringify({
                        method: 'heartbeat'
                    }));
                    heatbeat_interval = $interval(function() {
                        ws.send(JSON.stringify({
                            method: 'heartbeat'
                        }));
                    }, 60000);
                };

                ws.onmessage = function(event) {
                    onMessage(JSON.parse(event.data));
                };

                ws.onerror = function() {
                    connected = false;
                    $interval.cancel(heatbeat_interval);
                    console.log('[Client] Websocket connection error.');
                    // $message.Alert('Websocket连接错误.', 30);
                };

                ws.onclose = function() {
                    connected = false;
                    $interval.cancel(heatbeat_interval);
                    if (!unload) {
                        if (!reconnect) {
                            console.log('[Client] Websocket connection lost.');
                            $message.Warning('Websocket连接中断, 将在30s后重连.', 30);
                            $rootScope.$broadcast('heartbeat-lost');
                        } else {
                            console.log('[Client] Websocket re-connect failed, retry...');
                            $message.Warning('Websocket连接失败, 将在30s后重连.', 30);
                        }
                        $timeout(init, 30000);
                        reconnect = true;
                    }
                };
            } else {
                console.log("[Client] WebSocket not supported.");
            }
        };

        init();

        window.onbeforeunload = function() {
            unload = true;
            ws.close();
        };

        var onMessage = function(msg) {
            if (msg.hasOwnProperty('heartbeat')) {
                console.log('[Server] Heartbeat: ' + msg.heartbeat);
                $rootScope.$broadcast('heartbeat', msg.heartbeat);
            } else if (msg.hasOwnProperty('topics')) {
                msg.topics.forEach(function(topic_name) {
                    console.log('[Client] Subscribing topic: ' + topic_name);
                    ws.send(JSON.stringify({
                        method: 'subscribe',
                        topic: topic_name
                    }));
                });
            } else if (msg.hasOwnProperty('message')) {
                console.log('[Server] Message from server: ' + msg.message);
                // $message.Info(msg.message);
            } else if (msg.hasOwnProperty('error')) {
                console.log('[Server] Message from server: ' + msg.error);
                $message.Alert(msg.error);
            } else if (msg.hasOwnProperty('response')) {
                response = JSON.parse(msg.response);
                request_list[msg.session](response);
                delete request_list[msg.session];
            } else if (msg.hasOwnProperty('topic')) {
                switch (msg.topic) {
                    case "public":
                        // $message.Info(msg.data);
                        $timeout(function() {
                            $sessionStorage.messages.push(msg.data);
                        }, 0);
                        break;
                    case "tasks":
                        task_result = JSON.parse(msg.data);
                        console.log(task_result);
                        $rootScope.$broadcast('TaskStatusChanged', task_result);
                        break;
                    default:
                        console.log(JSON.stringify(msg));
                }
            }
        };

        return {
            Request: function(params) {
                var session = $uuid.uuid4();
                request_list[session] = params.callback;
                ws.send(JSON.stringify({
                    request: params.uri,
                    method: params.method,
                    session: session
                }));
            },
            Close: function() {
                unload = true;
                console.log('[Client] Closing websocket.');
                ws.close();
            }
        };
    });
});

app.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/dashboard', {
            templateUrl: 'UI/views/dashboard'
        })
        .when('/op_records', {
            templateUrl: 'UI/views/op_records'
        })
        .when('/inventory', {
            templateUrl: 'UI/views/inventory'
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

app.run(function($rootScope, $websocket, $sessionStorage, $localStorage, $location, $message) {
    $rootScope.tab = 1; //default
    $rootScope.status = "normal";
    $rootScope.currentId = null;
    $rootScope.GlobalConfigs = {
        svrStaticsInterval: { default: 60, current: 60 },
        sysStaticsInterval: { default: 60, current: 60 },
        loginStaticsInterval: { default: 60, current: 60 },
        sessionStaticsInterval: { default: 60, current: 60 },
        cpuIdleThreshold: { upper: 100, lower: 50 }
    };
    $rootScope.$on('$routeChangeStart', function(evt, next, current) {
        if ($rootScope.privileges === undefined) {
            $location.url('/dashboard');
        } else {
            angular.forEach($rootScope.privileges, function(value, key) {
                var ui_view = next.$$route.templateUrl.split('/').pop();
                if ('#' + ui_view === key && !value) {
                    evt.defaultPrevented = true;
                    $message.Warning('用户无权限访问该URI!');
                }
            });
        }
    });
});

app.filter('paging', function() {
    return function(listsData, start) {
        if (listsData)
            return listsData.slice(start);
    };
});

app.controller('FileUpdateControl', ['$scope', 'fileUpload', function($scope, fileUpload) {
    $scope.sendFile = function() {
        var url = "api/global-config",
            file = $scope.fileToUpload;
        if (!file)
            alert("请选择需要上传的文件。");
        else
            fileUpload.uploadFileToUrl(file, url);
    };
}]);

/* app.controller('warningCtrl', ['$scope', '$http', function($scope, $http) {
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
}]); */

// app.controller('taskControl', ['$scope', '$rootScope', function($scope, $rootScope) {}]);
app.filter('paging', function() {
    return function(listsData, start) {
        if (listsData)
            return listsData.slice(start);
    };
});

app.filter('KB2', function() {
    return function(value, dst) {
        var num = parseFloat(value);
        if (isNaN(num)) {
            return "无数据";
        }
        switch (dst) {
            case "M":
                return (num / 1024).toFixed(2).toString() + " MB";
            case "G":
                return (num / (1024 * 1024)).toFixed(2).toString() + " GB";
            case "T":
                return (num / (1024 * 1024 * 1024)).toFixed(2).toString() + " TB";
            default:
                if (num >= 1024) {
                    if (num >= 1048576) {
                        if (num >= 1073741824) {
                            return (num / (1024 * 1024 * 1024)).toFixed(2).toString() + " TB";
                        } else {
                            return (num / (1024 * 1024)).toFixed(2).toString() + " GB";
                        }
                    } else {
                        return (num / 1024).toFixed(2).toString() + " MB";
                    }
                } else {
                    return num.toFixed(2).toString() + " KB";
                }
        }
    };
});

app.filter('html_trust', ['$sce', function($sce) {
    return function(template) {
        return $sce.trustAsHtml(template);
    };
}]);

app.filter('percent', function() {
    return function(value, len, multi) {
        var num = parseFloat(value);
        if (isNaN(num)) {
            return "无数据";
        }
        var fix = 2;
        if (len !== undefined) {
            fix = len;
        }
        var multiplier = 1;
        if (multi !== undefined && multi !== null) {
            multiplier = multi;
        }
        return (num * multiplier).toFixed(fix).toString() + " %";
    };
});

app.filter('percentStatus', ['$rootScope', function($rootScope) {
    return function(value, range) {
        var num = parseFloat(value);
        if (isNaN(num)) {
            return false;
        }
        if (range !== undefined) {
            if (num > range.upper) {
                $rootScope.status = 'warning';
                return true;
            }
            if (num < range.lower) {
                $rootScope.status = 'warning';
                return true;
            }
            return false;
        }
        $rootScope.status = 'warning';
        return true;
    };
}]);

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
            if (stat.indexOf("check") >= 0) {
                return '检查中...';
            }
            switch (stat[0]) {
                case 'D':
                    return '不可中断 ';
                case 'R':
                    return '运行中';
                case 'S':
                    return '运行中';
                case 'T':
                    return '已停止';
                case 'Z':
                    return '僵尸进程';
                default:
                    return '运行中';
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
                return "执行成功";
            case -2:
                return "执行中...";
            case -3:
                return "跳过执行";
            case -4:
                return "任务已调度";
            case -5:
                return "等待触发条件";
            case -6:
                return "执行超时";
            case -7:
                return "超出时间范围";
            case -8:
                return "任务已下发";
            default:
                return "执行失败";
        }
    };
});
