var app = angular.module('myApp', ['ngRoute'], function($provide) {
    $provide.factory('globalVar', function() {
        return {
            'intervals': []
        };
    });

    $provide.factory('$message', function() {
        return {
            Alert: function(msg, timeout = 5) {

            },
            Warning: function(msg, timeout = 5) {

            },
            Info: function(msg, timeout = 5) {

            }
        }
    })

    $provide.factory('Message', function($rootScope, $location, $interval, $timeout) {
        if ($rootScope.Messages === undefined) {
            $rootScope.Messages = {
                public: []
            };
        }

        var connected = false;
        var heartbeat_interval;
        var unload = false;
        var ws;

        var init = function() {
            if ("WebSocket" in window) {
                ws = new WebSocket("ws://" + $location.host() + ":5000/websocket");
                ws.onopen = function() {
                    console.log("conn success");
                    connected = true;
                    ws.send(JSON.stringify({
                        method: 'topics'
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
                    console.log('Websocket error.');
                };

                ws.onclose = function() {
                    connected = false;
                    $interval.cancel(heatbeat_interval);
                    console.log('Websocket closed');
                    if (!unload) {
                        console.log('Connection lost.')
                        $timeout(init, 30000);
                    }
                };
            } else {
                console.log("WebSocket not supported");
            }
        };

        init();

        window.onbeforeunload = function() {
            unload = true;
            ws.close();
        };

        var onMessage = function(msg) {
            if (msg.hasOwnProperty('heartbeat')) {
                console.log(msg.heartbeat);
            } else if (msg.hasOwnProperty('topics')) {
                console.log(msg.topics);
                msg.topics.forEach(function(topic_name) {
                    ws.send(JSON.stringify({
                        method: 'subscribe',
                        topic: topic_name
                    }));
                });
            } else {
                switch (msg.topic) {
                    case "public":
                        $rootScope.$apply(function() {
                            $rootScope.Messages.public.push(msg.data);
                            $rootScope.AlertMessage = msg.data;
                            $rootScope.triggered = true;
                        });
                        if (window.localStorage.public === undefined) {
                            window.localStorage.public = [];
                        }
                        window.localStorage.public.push(msg.data);
                        break;
                    case "tasks":
                        console.log(JSON.parse(msg.data));
                        break;
                    default:
                        console.log(JSON.stringify(msg));
                }
            }
        };

        return {
            Send: function(msg) {
                ws.send(JSON.stringify(msg));
            },
            Close: function() { ws.close(); },
            Subscribe: function(topic_name, callback) {
                ws.send(JSON.stringify({
                    method: 'subscribe',
                    topic: topic_name
                }));
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
            templateUrl: 'UI/views/statics'
        })
        .when('/op_group/:grpid', {
            templateUrl: 'UI/views/op_group'
        })
        .when('/emerge_ops/system/:sysid', {
            templateUrl: 'UI/views/emerge_ops'
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
    if ($rootScope.LoginStatics === undefined) {
        $rootScope.LoginStatics = {};
    }
});
app.controller('dashBoardControl', ['$scope', 'Message', '$rootScope', '$http', function($scope, Message, $rootScope, $http) {
    //$rootScope.Message = Message;
    $rootScope.isShowSideList = false;
}]);
app.controller('userController', ['$scope', '$http', function($scope, $http) {
    $scope.ModifyPassword = function(usr_id) {
        $('#modifyPassword').modal({
            relatedTarget: this,
            onConfirm: function() {
                $http.put('api/user/id/' + usr_id, data = {
                    old_password: $('#oldPwd').val(),
                    password: $('#newPwd').val()
                }).success(function(response) {
                    console.log(response);
                }).error(function(response) {
                    console.log(response);
                });
                $('#oldPwd').val('');
                $('#newPwd').val('');
            }
        });
    };
}]);
app.controller('svrStaticsControl', ['$scope', '$http', 'globalVar', '$interval', '$routeParams', function($scope, $http, globalVar, $interval, $routeParams) {
    $scope.svrShowDetail = true;
    $scope.checkSvrStatics = function() {
        angular.forEach($scope.serverStatics, function(value, index) {
            value.uptime = '检查中...';
        });
        $scope.checking = true;
        $http.get('api/system/id/' + $routeParams.sysid + '/svr_statics/check')
            .success(function(response) {
                if (response.sys_id == $routeParams.sysid) {
                    $scope.serverStatics = response.details;
                    $scope.serverStatics.showMountDetail = [];
                    angular.forEach(response.details.disks, function(value, index) {
                        $scope.serverStatics.showMountDetail.push(false);
                    });
                }
                $scope.checking = false;
            })
            .error(function(response) {
                console.log(response);
                $scope.checking = false;
            });
    };
    $scope.autoRefresh = function(auto) {
        if (auto) {
            $scope.svrStaticInterval = $interval(function() { $scope.checkSvrStatics(); }, 60000);
            $scope.checkSvrStatics();
            globalVar.intervals.push($scope.svrStaticInterval);
        } else {
            $interval.cancel($scope.svrStaticInterval);
        }
    };

    $http.get('api/system/id/' + $routeParams.sysid + '/svr_statics')
        .success(function(response) {
            if ($routeParams.hasOwnProperty('sysid') && response.sys_id == $routeParams.sysid) {
                $scope.serverStatics = response.details;
                $scope.checkSvrStatics();
            }
        })
        .error(function(response) {
            console.log(response);
            $scope.checking = false;
        });
}]);
app.controller('sysStaticsControl', ['$scope', '$http', 'globalVar', '$interval', '$routeParams', function($scope, $http, globalVar, $interval, $routeParams) {
    $scope.sysShowDetail = true;
    $scope.checkProc = function() {
        $scope.checking = true;
        angular.forEach($scope.systemStatics, function(value1, index1) {
            angular.forEach(value1.detail, function(value2, index2) {
                value2.status.stat = 'checking';
                angular.forEach(value2.sockets, function(value3, index3) {
                    value3.status.stat = '检查中...';
                });
                angular.forEach(value2.connections, function(value4, index4) {
                    value4.status.stat = '检查中...';
                });
            });
        });
        $http.get('api/system/id/' + $routeParams.sysid + '/sys_statics/check')
            .success(function(response) {
                $scope.systemStatics = response;
                $scope.checking = false;
            })
            .error(function(response) {
                console.log(response);
                $scope.checking = false;
            });
    };
    $scope.autoRefresh = function(auto) {
        if (auto) {
            $scope.sysStaticInterval = $interval(function() { $scope.checkProc(); }, 30000);
            $scope.checkProc();
            globalVar.intervals.push($scope.sysStaticInterval);
        } else {
            $interval.cancel($scope.sysStaticInterval);
        }
    };

    $http.get('api/system/id/' + $routeParams.sysid + '/sys_statics')
        .success(function(response) {
            if ($routeParams.hasOwnProperty('sysid')) {
                $scope.systemStatics = response;
                $scope.checkProc();
            }
        })
        .error(function(response) {
            console.log(response);
            $scope.checking = false;
        });
}]);
app.controller('sideBarCtrl', ['$scope', '$http', '$timeout', '$rootScope', '$location', function($scope, $http, $timeout, $rootScope, $location) {
    $scope.tabList = [];
    var idList = [];
    $scope.$on('$routeChangeStart', function(evt, next, current) {
        if (next.params.hasOwnProperty('sysid')) {
            if ($scope.listName === undefined) {
                var watch_onece = $scope.$watch('listName', function() {
                    if ($scope.listName !== undefined) {
                        $scope.showListChange(next.params.sysid);
                        watch_onece(); //取消监听
                    }
                });
            } else {
                $scope.showListChange(next.params.sysid);
            }
        }
    });
    $http.get('api/UI/sideBarCtrl')
        .success(function(response) {
            $scope.listName = response;
        })
        .error(function(response) {
            console.log(response);
        });
    $scope.showListChild = function(id) {
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
        angular.forEach($scope.tabList, function(value, index) {
            value.active = "";
            if (idList.indexOf(value.id) == -1) {
                idList.push(value.id);
            }
        });
        angular.forEach($scope.listName, function(value, index) {
            if (value.id == id) {
                $scope.listName[index].isShow = true;
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
            var LocationUrl = $scope.tabList[length - 1].Url;
            LocationUrl = LocationUrl.substring(1, LocationUrl.length);
            LocationUrl = '/' + LocationUrl;
            $location.url(LocationUrl);
        } else {
            $rootScope.isShowSideList = false;
            $location.url('/dashboard');
        }
    };
    $scope.clearTabList = function() {
        if ($rootScope.isShowSideList === false) {
            idList.splice(0, idList.length);
            $scope.tabList.splice(0, $scope.tabList.length);
            return false;
        } else {
            return true;
        }
    };
    $scope.operateChange = function(id) {
        $rootScope.isShowSideList = false;
    };
}]);

app.controller('opGroupController', ['$scope', '$http', '$timeout', '$routeParams', '$location', 'Message', function($scope, $http, $timeout, $routeParams, $location, Message) {
    $scope.$on('$routeChangeStart', function(evt, next, current) {
        var last = $scope.opList.details[$scope.opList.details.length - 1];
        if (last.err_code != -1 && last.checker.isTrue && !last.checker.checked) {
            $location.url('/op_group/' + current.params.grpid);
            alert('还有未确认的操作结果！');
        }
    });

    $http.get('api/op_group/id/' + $routeParams.grpid)
        .success(function(response) {
            $scope.opList = response;
        })
        .error(function(response) {
            console.log(response);
        });
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
    $scope.check_his_result = function(index) {
        $('#his_result' + index).modal({ relatedTarget: this });
    };
    $scope.skip = function(index) {
        if ($scope.opList.details[index].err_code == -1) {
            $scope.opList.details[index].err_code = -3;
        }
        if (index < $scope.opList.details.length - 1) {
            $scope.opList.details[index + 1].enabled = true;
        }
        for (var i = 0; i <= index; i++) {
            $scope.opList.details[i].skip = false;
            $scope.opList.details[i].enabled = true;
        }
    };
    $scope.execute = function(index, id) {
        if ($scope.opList.details[index].interactivator.isTrue) {
            $http.get('api/operation/id/' + id + '/ui')
                .success(function(response) {
                    $scope.opList.details[index].interactivator.template = response;
                    $('#interactive' + id).bind('results.quantdo', function(event, data) {
                        $scope.$apply(function() {
                            if ($routeParams.hasOwnProperty('grpid')) {
                                $scope.opList.details[index] = data;
                                if (data.output_lines.length > 0) {
                                    if (data.checker.isTrue) {
                                        $scope.confirm(index);
                                    } else {
                                        $scope.check_result(index);
                                    }
                                }
                                if (index < $scope.opList.details.length - 1 && ($scope.opList.details[index].checker === undefined || !$scope.opList.details[index].checker.isTrue)) {
                                    $scope.opList.details[index + 1].enabled = data.err_code === 0;
                                }
                            }
                        });
                    });
                    $('#interactive' + id).on('opened.modal.amui', function() {
                        var imgElement = $('#interactive' + id).find('img')[0];
                        if (imgElement !== null && imgElement !== undefined) {
                            imgElement.click();
                        }
                    });
                    $('#interactive' + id).modal({
                        relatedTarget: this,
                        onCancel: function() {
                            $scope.$apply(function() {
                                $scope.opList.details[index].err_code = -1;
                            });
                        }
                    });
                });
        } else {
            if ($scope.opList.details[index].need_authorized) {
                $('#authorizor').bind('authorize.quantdo', function(event, data) {
                    $scope.opList.details[index].err_code = -2;
                    $scope.opList.details[index].skip = false;
                    $http.post('api/operation/id/' + id, data = data)
                        .success(function(response) {
                            if ($routeParams.hasOwnProperty('grpid')) {
                                $scope.opList.details[index] = response;
                                if (response.output_lines.length > 0) {
                                    if (response.checker.isTrue) {
                                        $scope.confirm(index);
                                    } else {
                                        $scope.check_result(index);
                                    }
                                }
                                if (index < $scope.opList.details.length - 1 && ($scope.opList.details[index].checker === undefined || !$scope.opList.details[index].checker.isTrue)) {
                                    $scope.opList.details[index + 1].enabled = response.err_code === 0;
                                }
                            }
                            $('#authorizor').unbind('authorize.quantdo');
                        })
                        .error(function(response) {
                            console.log(response);
                            if ($routeParams.hasOwnProperty('grpid')) {
                                $scope.opList.details[index] = response;
                            }
                            $('#authorizor').unbind('authorize.quantdo');
                        });
                });
                var err_code = $scope.opList.details[index].err_code;
                $('#authorizor').modal({
                    relatedTarget: this,
                    onCancel: function() {
                        $('#authorizeUser').val('');
                        $('#authorizePassword').val('');
                    }
                });
            } else {
                $scope.opList.details[index].err_code = -2;
                $scope.opList.details[index].skip = false;
                $http.post('api/operation/id/' + id)
                    .success(function(response) {
                        if ($routeParams.hasOwnProperty('grpid')) {
                            $scope.opList.details[index] = response;
                            if (response.output_lines.length > 0) {
                                if (response.checker.isTrue) {
                                    $scope.confirm(index);
                                } else {
                                    $scope.check_result(index);
                                }
                            }
                            if (index < $scope.opList.details.length - 1 && ($scope.opList.details[index].checker === undefined || !$scope.opList.details[index].checker.isTrue)) {
                                $scope.opList.details[index + 1].enabled = response.err_code === 0;
                            }
                        }
                    })
                    .error(function(response) {
                        console.log(response);
                        if ($routeParams.hasOwnProperty('grpid')) {
                            $scope.opList.details[index] = response;
                        }
                    });
            }
        }
    };
}]);
app.controller('emergeOpsController', ['$scope', '$http', '$routeParams', function($scope, $http, $routeParams) {
    $http.get('api/emerge_ops/system/id/' + $routeParams.sysid)
        .success(function(response) {
            $scope.emergeopList = response;
        })
        .error(function(response) {
            console.log(response);
        });

    $scope.openshell = function(sys_id) {
        $http.get('api/webshell/system/id/' + sys_id)
            .success(function(response) {
                $scope.emergeopList.webshell = response;
                $('#webshell').modal({
                    relatedTarget: this
                });
            });
    };

    $scope.check_result = function(id) {
        $('#result' + id).modal({ relatedTarget: this });
    };
    $scope.check_his_result = function(id) {
        $('#his_result' + id).modal({ relatedTarget: this });
    };

    $scope.execute = function(grp_name, op_idx, id) {
        var group = null;
        angular.forEach($scope.emergeopList, function(value, index) {
            if (grp_name == value.name) {
                group = value;
            }
        });
        if (group === null || group === undefined) {
            console.log('Operation group found with name ' + grp_name);
            return;
        }
        if (group.details[op_idx].interactivator.isTrue) {
            $http.get('api/emerge_ops/id/' + id + '/ui')
                .success(function(response) {
                    group.details[op_idx].interactivator.template = response;
                    $('#interactive' + id).bind('results.quantdo', function(event, data) {
                        $scope.$apply(function() {
                            if ($routeParams.hasOwnProperty('grpid')) {
                                group.details[op_idx] = data;
                            }
                        });
                    });
                    $('#interactive' + id).on('opened.modal.amui', function() {
                        var imgElement = $('#interactive' + id).find('img')[0];
                        if (imgElement !== null && imgElement !== undefined) {
                            imgElement.click();
                        }
                    });
                    $('#interactive' + id).modal({
                        relatedTarget: this,
                        onCancel: function() {
                            $scope.$apply(function() {
                                group.details[op_idx].err_code = -1;
                            });
                        }
                    });
                })
                .error(function(response) {
                    console.log(response);
                });
        } else {
            group.details[op_idx].err_code = -2;
            $http.post('api/emerge_ops/id/' + id)
                .success(function(response) {
                    if ($routeParams.hasOwnProperty('sysid')) {
                        group.details[op_idx] = response;
                    }
                })
                .error(function(response) {
                    console.log(response);
                });
        }
    };
}]);
app.controller('loginStaticsControl', ['$scope', '$http', 'globalVar', '$rootScope', '$interval', '$timeout', '$routeParams', function($scope, $http, globalVar, $rootScope, $interval, $timeout, $routeParams) {
    $scope.loginShowDetail = true;
    $scope.loginStaticsShow = false;
    $scope.$watch('$rootScope.LoginStatics', function(newValue, oldValue) {
        $timeout(function() {
            $scope.loginStatics = $rootScope.LoginStatics[$routeParams.sysid];
        }, 0);
    }, true);
    $scope.CheckLoginLog = function() {
        $scope.checking = true;
        $http.get('api/system/id/' + $routeParams.sysid + '/login_statics/check')
            .success(function(response) {
                if ($routeParams.hasOwnProperty('sysid')) {
                    angular.forEach(response, function(value1, index1) {
                        angular.forEach($rootScope.LoginStatics[$routeParams.sysid], function(value2, index2) {
                            if (value1.seat_id == value2.seat_id) {
                                $rootScope.LoginStatics[$routeParams.sysid][index2].seat_status = value1.seat_status;
                                $rootScope.LoginStatics[$routeParams.sysid][index2].conn_count = value1.conn_count;
                                $rootScope.LoginStatics[$routeParams.sysid][index2].disconn_count = value1.disconn_count;
                                $rootScope.LoginStatics[$routeParams.sysid][index2].login_fail = value1.login_fail;
                                $rootScope.LoginStatics[$routeParams.sysid][index2].login_success = value1.login_success;
                                $rootScope.LoginStatics[$routeParams.sysid][index2].updated_time = value1.updated_time;
                                if (value1.hasOwnProperty('trading_day')) {
                                    $rootScope.LoginStatics[$routeParams.sysid][index2].trading_day = value1.trading_day;
                                }
                                if (value1.hasOwnProperty('login_time')) {
                                    $rootScope.LoginStatics[$routeParams.sysid][index2].login_time = value1.login_time;
                                }
                            }
                        });
                    });
                    $scope.checking = false;
                }
            })
            .error(function(response) {
                console.log(response);
                $scope.checking = false;
            });
    };
    $scope.$watch('refresh_interval', function(newValue, oldValue) {
        $interval.cancel($scope.loginStaticInterval);
        $scope.autoRefresh();
    })
    $scope.autoRefresh = function() {
        if ($scope.auto) {
            if (isNaN($scope.refresh_interval)) {
                var interval = 60000;
            } else {
                var interval = parseInt($scope.refresh_interval)
                if (interval <= 30) {
                    $scope.refresh_interval = 30;
                    interval = 30;
                }
                interval = interval * 1000;
            }
            $scope.loginStaticInterval = $interval(function() { $scope.CheckLoginLog(); }, interval);
            $scope.CheckLoginLog();
            globalVar.intervals.push($scope.loginStaticInterval);
        } else {
            $interval.cancel($scope.loginStaticInterval);
        }
    };

    $http.get('api/system/id/' + $routeParams.sysid + '/login_statics')
        .success(function(response) {
            $scope.loginStaticsShow = true;
            $rootScope.LoginStatics[$routeParams.sysid] = response;
            $scope.loginStatics = $rootScope.LoginStatics[$routeParams.sysid];
            $scope.CheckLoginLog();
        })
        .error(function(response) {
            console.log(response);
        });
}]);
app.controller('clientStaticsControl', ['$scope', 'globalVar', '$http', '$routeParams', '$interval', function($scope, globalVar, $http, $routeParams, $interval) {
    $scope.clientShowDetail = true;
    $scope.userSessionShow = false;
    $scope.CheckClientSessions = function() {
        $scope.checking = true;
        $http.get('api/system/id/' + $routeParams.sysid + '/user_sessions')
            .success(function(response) {
                $scope.userSessionShow = true;
                $scope.checking = false;
                $scope.statusList = response;
            })
            .error(function(response) {
                console.log(response);
                $scope.checking = false;
            });
    };
    $scope.autoRefresh = function(auto) {
        if (auto) {
            $scope.clientSessionInterval = $interval(function() { $scope.CheckClientSessions(); }, 300000);
            $scope.CheckClientSessions();
            globalVar.intervals.push($scope.clientSessionInterval);
        } else {
            $interval.cancel($scope.clientSessionInterval);
        }
    }
    $scope.CheckClientSessions();
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

}]);
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
            default:
                return "执行失败";
        }
    };
});
app.directive('relamap', [function() {
    return {
        restrict: 'A',
        link: link
    };

    function link(scope, element, attr) {
        var myChart = echarts.init(element[0]);
        myChart.showLoading();
        $.get('api/UI/relation', function(option) {
            myChart.hideLoading();
            myChart.setOption(option);
        });

        $(element[0]).resize(function() {
            myChart.resize();
        });
    }
}]);
app.directive('idcmap', [function() {
    return {
        restrict: 'A',
        link: link
    };

    function link(scope, element, attr) {
        $.get('api/UI/map?name=china', function(chinaJson) {
            echarts.registerMap('china', chinaJson);
            myChart = echarts.init(element[0]);
            myChart.showLoading();
            myChart.setOption({
                backgroundColor: '#fff',
                title: {
                    text: '数据中心分布',
                    left: '10px',
                    top: '10px'
                },
                tooltip: {
                    trigger: 'item',
                },
                toolbox: {
                    show: true,
                    feature: {
                        dataView: { show: true, readOnly: true },
                        restore: { show: true }
                    }
                },
                legend: {
                    orient: 'vertical',
                    y: 'bottom',
                    x: 'left',
                    data: ['数据中心'],
                    textStyle: {
                        color: '#111'
                    }
                },
                geo: {
                    map: 'china',
                    itemStyle: {
                        normal: {
                            borderColor: '#111'
                        }
                    }
                }
            });
            myChart.hideLoading();

            $(element[0]).resize(function() {
                //chartResize();
                myChart.resize();
            });

            getIDC();
        });

        function getIDC() {
            $.get('api/UI/idc', function(idcs) {
                myChart.setOption({
                    series: [{
                        name: '数据中心',
                        type: 'effectScatter',
                        coordinateSystem: 'geo',
                        showEffectOn: 'emphasis',
                        rippleEffect: {
                            period: 4,
                            scale: 3,
                            brushType: 'fill'
                        },
                        label: {
                            normal: {
                                show: true,
                                position: 'right',
                                formatter: '{b}'
                            }
                        },
                        symbolSize: function(val) {
                            return val[2];
                        },
                        itemStyle: {
                            normal: {
                                color: '#ddb926'
                            }
                        },
                        data: idcs
                    }]
                });
            });
        }
    }
}]);