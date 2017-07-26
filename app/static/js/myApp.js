var app = angular.module('myApp', ['ngRoute', 'angular-sortable-view', 'ngStorage'], function($provide) {
    $provide.factory('$uuid', function() {
        return {
            uuid4: function() {
                return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
                    (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
                )
            }
        }
    });

    $provide.factory('$message', function($uuid) {
        return {
            ModelSucess: function(msg, moduleID, timeout = 3, id = $uuid.uuid4()) {
                $('#' + moduleID).append('\
<div class="am-alert" style="margin: 1px 5px; display: none" id="' + id + '">\
    <p class="am-text-center">' + msg + '</p>\
</div>\
                ');
                $('#' + id).alert();
                $('#' + id).addClass('am-alert-success').show();
                setTimeout(function() {
                    $('#' + id).alert('close');
                }, timeout * 1000);
            },
            ModelAlert: function(msg, moduleID, timeout = 3, id = $uuid.uuid4()) {
                $('#' + moduleID).append('\
<div class="am-alert" style="margin: 1px 5px; display: none" id="' + id + '">\
    <p class="am-text-center">' + msg + '</p>\
</div>\
                ');
                $('#' + id).alert();
                $('#' + id).addClass('am-alert-danger').show();
                setTimeout(function() {
                    $('#' + id).alert('close');
                }, timeout * 1000);
            },
            Alert: function(msg, timeout = 3, id = $uuid.uuid4()) {
                $('#alertMessage').append('\
<div class="am-alert" style="margin: 1px 5px; display: none" id="' + id + '">\
    <span type="button" class="am-close am-fr">&times;</span>\
    <p class="am-text-center">' + msg + '</p>\
</div>\
                ');
                $('#' + id).alert();
                $('#' + id).addClass('am-alert-danger').show();
                setTimeout(function() {
                    $('#' + id).alert('close');
                }, timeout * 1000);
            },
            Warning: function(msg, timeout = 3, id = $uuid.uuid4()) {
                $('#alertMessage').append('\
<div class="am-alert" style="margin: 1px 5px; display: none" id="' + id + '">\
    <span type="button" class="am-close am-fr">&times;</span>\
    <p class="am-text-center">' + msg + '</p>\
</div>\
                ');
                $('#' + id).alert();
                $('#' + id).addClass('am-alert-warning').show();
                setTimeout(function() {
                    $('#' + id).alert('close');
                }, timeout * 1000);
            },
            Info: function(msg, timeout = 3, id = $uuid.uuid4()) {
                $('#alertMessage').append('\
<div class="am-alert" style="margin: 1px 5px; display: none" id="' + id + '">\
    <span type="button" class="am-close am-fr">&times;</span>\
    <p class="am-text-center">' + msg + '</p>\
</div>\
                ');
                $('#' + id).alert();
                $('#' + id).show();
                setTimeout(function() {
                    $('#' + id).alert('close');
                }, timeout * 1000);
            },
            Success: function(msg, timeout = 3, id = $uuid.uuid4()) {
                $('#alertMessage').html('\
<div class="am-alert" style="margin: 1px 5px; display: none" id="' + id + '">\
    <span type="button" class="am-close am-fr">&times;</span>\
    <p class="am-text-center">' + msg + '</p>\
</div>\
                ');
                $('#' + id).alert();
                $('#' + id).addClass('am-alert-success').show();
                setTimeout(function() {
                    $('#' + id).alert('close');
                }, timeout * 1000);
            }
        }
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
                if (ws) { delete ws; }
                var websocket_protocol = $location.protocol() == "http" ? "ws://" : "wss://";
                var websocket_uri = websocket_protocol + $location.host() + ":" + $location.port() + "/websocket";
                console.log(websocket_uri);
                ws = new WebSocket(websocket_uri);
                ws.onopen = function() {
                    unload = false;
                    console.log("[Client] Websocket connected successfully.");
                    $message.Success('Websocket connected successfully.');
                    connected = true;
                    reconnect = false;
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
                    console.log('[Client] Websocket connection error.');
                    $message.Alert('Websocket connection error.');
                };

                ws.onclose = function() {
                    connected = false;
                    $interval.cancel(heatbeat_interval);
                    if (!unload) {
                        if (!reconnect) {
                            console.log('[Client] Websocket connection lost.');
                            $message.Warning('Websocket connection lost, reconnect in 30s.', 30)
                        } else {
                            console.log('[Client] Websocket re-connect failed, retry...');
                            $message.Warning('Websocket re-connect failed, retry in 30s.', 30)
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
                $message.Info(msg.message);
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
                        $message.Info(msg.data);
                        $timeout(function() {
                            $sessionStorage.messages.push(msg.data);
                        }, 0)
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
                console.log('[Client] Closing websocket.')
                ws.close();
            }
        };
    });
});

app.directive("fileModel", ["$parse", function($parse) {
    return {
        restrict: "A",
        link: function(scope, element, attrs) {
            var model = $parse(attrs.fileModel);
            var modelSetter = model.assign;

            element.bind("change", function() {
                scope.$apply(function() {
                    modelSetter(scope, element[0].files[0]);
                    console.log(model.assign);
                })
            })
        }
    }
}]);

app.service("fileUpload", ["$http", function($http) {
    this.uploadFileToUrl = function(file, uploadUrl) {
        var fd = new FormData();
        fd.append("file", file)
        $http.post(uploadUrl, fd, {
                transformRequest: angular.identity,
                headers: { "Content-Type": undefined }
            })
            .success(function(res) {
                if (res.error_code == 0) {
                    alert("文件上传成功。");
                    window.location.reload();
                } else {
                    alert("数据已存在于数据库中。")
                }
            })
            .error(function(res) {
                alert(res.message);
            })
    }
}]);

app.service('$uidatas', function($http, $message) {
    this.SideBarList = function(params) {
        $http.get('api/UI/sideBarCtrl')
            .success(function(response) {
                if (response.error_code == 0) {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    };
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            })
            .error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            })
    }
})

app.service('$servers', function($http, $websocket, $message, $localStorage, $timeout, $rootScope) {
    this.CheckServerStatics = function(params, force = false) {
        if (params.sysID === undefined) {
            return false;
        }
        var request_timestamp = new Date().getTime();
        if ($localStorage.hasOwnProperty('svrStatics_' + params.sysID)) {
            if ($localStorage['svrStatics_' + params.sysID].hasOwnProperty('last_request')) {
                last_request = parseInt($localStorage['svrStatics_' + params.sysID].last_request);
                if (!force && request_timestamp - last_request <
                    ($rootScope.GlobalConfigs.svrStaticsInterval.current * 1000)) {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(angular.extend(
                            $localStorage['svrStatics_' + params.sysID], { cached: false }
                        ));
                    }
                    return false;
                } else {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(angular.extend(
                            $localStorage['svrStatics_' + params.sysID], { cached: true }
                        ));
                    }
                }
            }
            $timeout(function() {
                angular.extend($localStorage['svrStatics_' + params.sysID], { last_request: request_timestamp });
            }, 0);
        }
        $websocket.Request({
            uri: 'api/system/id/' + params.sysID + '/svr_statics/check',
            method: 'get',
            callback: function(response) {
                if (response.error_code == 0) {
                    if ($localStorage.hasOwnProperty('svrStatics_' + params.sysID)) {
                        $timeout(function() {
                            angular.merge($localStorage['svrStatics_' + params.sysID], response.data);
                        })
                    } else {
                        $timeout(function() {
                            $localStorage['svrStatics_' + params.sysID] = angular.merge(
                                response.data, { last_request: request_timestamp }
                            );
                        });
                    }
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            }
        });
        /* $http.get('api/system/id/' + params.sysID + '/svr_statics/check')
            .success(function(response) {
                if (response.error_code == 0) {
                    if ($localStorage.hasOwnProperty('svrStatics_' + params.sysID)) {
                        $timeout(function() {
                            angular.merge($localStorage['svrStatics_' + params.sysID], response.data);
                        })
                    } else {
                        $timeout(function() {
                            $localStorage['svrStatics_' + params.sysID] = angular.merge(
                                response.data, { last_request: request_timestamp }
                            );
                        });
                    }
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            })
            .error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            }); */
        return true;
    };

    this.ServerList = function(params) {
        if (params.sysID === undefined) {
            return;
        }
        /* $websocket.Request({
            uri: 'api/system/id/' + params.sysID + '/svr_statics',
            method: 'get',
            callback: function(response) {
                if (response.error_code == 0) {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            }
        }); */
        $http.get('api/system/id/' + params.sysID + '/svr_statics')
            .success(function(response) {
                if (response.error_code == 0) {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            })
            .error(function(response) {
                console.log(response);
                if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                } else {
                    $message.Alert(response.message);
                }
            });
    }
});

app.service('$systems', function($http, $websocket, $message, $localStorage, $sessionStorage, $timeout, $rootScope) {
    this.SystemStaticsCheck = function(params, force = false) {
        if (params.sysID === undefined) {
            return false;
        }
        var request_timestamp = new Date().getTime();
        if ($localStorage.hasOwnProperty('sysStatics_' + params.sysID)) {
            if ($localStorage['sysStatics_' + params.sysID].hasOwnProperty('last_request')) {
                last_request = parseInt($localStorage['sysStatics_' + params.sysID].last_request);
                if (!force && request_timestamp - last_request <
                    ($rootScope.GlobalConfigs.sysStaticsInterval.current * 1000)) {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(angular.extend(
                            $localStorage['sysStatics_' + params.sysID], { cached: false }
                        ));
                    }
                    return false;
                } else {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(angular.extend(
                            $localStorage['sysStatics_' + params.sysID], { cached: true }
                        ));
                    }
                }
            }
            $timeout(function() {
                angular.extend($localStorage['sysStatics_' + params.sysID], { last_request: request_timestamp });
            }, 0);
        }
        $websocket.Request({
            uri: 'api/system/id/' + params.sysID + '/sys_statics/check',
            method: 'get',
            callback: function(response) {
                if (response.error_code == 0) {
                    if ($localStorage.hasOwnProperty('sysStatics_' + params.sysID)) {
                        $timeout(function() {
                            angular.merge($localStorage['sysStatics_' + params.sysID], response.data);
                        })
                    } else {
                        $timeout(function() {
                            $localStorage['sysStatics_' + params.sysID] = angular.merge(
                                response.data, { last_request: request_timestamp }
                            );
                        });
                    }
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            }
        });
        /* $http.get('api/system/id/' + params.sysID + '/sys_statics/check')
            .success(function(response) {
                if (response.error_code == 0) {
                    if ($localStorage.hasOwnProperty('sysStatics_' + params.sysID)) {
                        $timeout(function() {
                            angular.merge($localStorage['sysStatics_' + params.sysID], response.data);
                        })
                    } else {
                        $timeout(function() {
                            $localStorage['sysStatics_' + params.sysID] = angular.merge(
                                response.data, { last_request: request_timestamp }
                            );
                        });
                    }
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            })
            .error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            }); */
        return true;
    }

    this.SystemList = function(params) {
        if (params.sysID === undefined) {
            return;
        }
        /* $websocket.Request({
            uri: 'api/system/id/' + params.sysID + '/sys_statics',
            method: 'get',
            callback: function(response) {
                if (response.error_code == 0) {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            }
        }); */
        $http.get('api/system/id/' + params.sysID + '/sys_statics')
            .success(function(response) {
                if (response.error_code == 0) {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            })
            .error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
    }

    this.LoginStaticsCheck = function(params, force = false) {
        if (params.sysID === undefined) {
            return false;
        }
        var request_timestamp = new Date().getTime();
        if ($sessionStorage.hasOwnProperty('loginStatics_' + params.sysID)) {
            if ($sessionStorage['loginStatics_' + params.sysID].hasOwnProperty('last_request')) {
                last_request = parseInt($sessionStorage['loginStatics_' + params.sysID].last_request);
                if (!force && request_timestamp - last_request <
                    ($rootScope.GlobalConfigs.loginStaticsInterval.current * 1000)) {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(angular.extend(
                            $sessionStorage['loginStatics_' + params.sysID], { cached: false }
                        ));
                    }
                    return false;
                } else {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(angular.extend(
                            $sessionStorage['loginStatics_' + params.sysID], { cached: true }
                        ));
                    }
                }
            }
            $timeout(function() {
                angular.extend($sessionStorage['loginStatics_' + params.sysID], { last_request: request_timestamp });
            }, 0);
        }
        $http.get('api/system/id/' + params.sysID + '/login_statics/check')
            .success(function(response) {
                if (response.error_code == 0) {
                    if ($sessionStorage.hasOwnProperty('loginStatics_' + params.sysID)) {
                        $timeout(function() {
                            angular.merge($sessionStorage['loginStatics_' + params.sysID], response.data);
                        })
                    } else {
                        $timeout(function() {
                            $sessionStorage['loginStatics_' + params.sysID] = angular.merge(
                                response.data, { last_request: request_timestamp }
                            );
                        });
                    }
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            })
            .error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
        return true;
    }

    this.LoginList = function(params) {
        if (params.sysID === undefined) {
            return;
        }
        $http.get('api/system/id/' + params.sysID + '/login_statics')
            .success(function(response) {
                if (response.error_code == 0) {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            })
            .error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            })
    }

    this.ClientSessionCheck = function(params, force = false) {
        if (params.sysID === undefined) {
            return false;
        }
        var request_timestamp = new Date().getTime();
        if ($sessionStorage.hasOwnProperty('clientSessions_' + params.sysID)) {
            if ($sessionStorage['clientSessions_' + params.sysID].hasOwnProperty('last_request')) {
                last_request = parseInt($sessionStorage['clientSessions_' + params.sysID].last_request);
                if (!force && request_timestamp - last_request <
                    ($rootScope.GlobalConfigs.sessionStaticsInterval.current * 1000)) {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(angular.extend(
                            $sessionStorage['clientSessions_' + params.sysID], { cached: false }
                        ));
                    }
                    return false;
                } else {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(angular.extend(
                            $sessionStorage['clientSessions_' + params.sysID], { cached: true }
                        ));
                    }
                }
            }
            $timeout(function() {
                angular.extend(
                    $sessionStorage['clientSessions_' + params.sysID], { last_request: request_timestamp }
                );
            }, 0);
        }
        $http.get('api/system/id/' + params.sysID + '/user_sessions')
            .success(function(response) {
                if (response.error_code == 0) {
                    if ($sessionStorage.hasOwnProperty('clientSessions_' + params.sysID)) {
                        $timeout(function() {
                            angular.merge($sessionStorage['clientSessions_' + params.sysID], response.data);
                        })
                    } else {
                        $timeout(function() {
                            $sessionStorage['clientSessions_' + params.sysID] = angular.merge(
                                response.data, { last_request: request_timestamp }
                            );
                        });
                    }
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            })
            .error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
        return true;
    }
})

app.service('$operations', function($websocket, $http, $message, $sessionStorage) {
    this.Detail = function(params) {
        $http.get('api/op_group/id/' + params.groupID)
            .success(function(response) {
                if (response.error_code == 0) {
                    params.onSuccess(response.data);
                } else {
                    $message.Warning(response.message);
                }
            })
            .error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
    }
    this.InitQueue = function(params) {
        $http.post('api/op_group/id/' + params.groupID)
            .success(function(response) {
                if (response.err_code == 0) {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            })
            .error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
    }
    this.SkipCurrent = function(params) {}
    this.ResumeQueue = function(params) {}
    this.Snapshot = function(params) {
        $http.get('api/op_group/id/' + params.groupID + '/snapshot')
            .success(function(response) {
                if (response.err_code == 0) {
                    if (params.hasOwnProperty('onSuccess')) {
                        params.onSuccess(response.data);
                    }
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response);
                }
            })
            .error(function(response) {
                console.log(response);
                if (response.hasOwnProperty('message')) {
                    $message.Alert(response.message);
                }
            });
    }
    this.RunNext = function(params) {
        $http.get(
                'api/operation/id/' + params.operationID,
                headers = {
                    Authorizor: JSON.stringify(params.authorizor)
                }
            )
            .success(function(response) {
                if (response.error_code == 0) {
                    response.data.exec_code = -4;
                    params.onSuccess(response.data);
                } else {
                    console.log(response)
                    if (params.hasOwnProperty('onError')) {
                        params.onError(response.message);
                    } else {
                        $message.Warning(response.message);
                    }
                }
            })
            .error(function(response) {
                console.log(response);
                if (response.hasOwnProperty('message')) {
                    $message.Alert(response.message);
                }
            });
    }
    this.RunAll = function(params) {
        $http.get('api/op_group/id/' + params.groupID + '/all')
            .success(function(response) {
                if (response.error_code == 0) {
                    params.onSuccess(response.data);
                } else if (params.hasOwnProperty('onError')) {
                    params.onError(response.data);
                } else {
                    $message.Warning(response.message);
                }
            })
            .error(function(response) {
                console.log(response);
                if (response.hasOwnProperty('message')) {
                    $message.Alert(response.message);
                }
            });
    }
});

app.service("$operationBooks", ["$http", '$message', function($http, $message) {
    this.operationBookSystemsGet = function(params) {
        $http.get('api/systems')
            .success(function(response) {
                if (response.error_code == 0) {
                    params.onSuccess(response.data);
                }
            })
            .error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
    }

    this.operationBookSystemListGet = function(params) {
        $http.get('api/system/id/' + params.sys_id + '/systems')
            .success(function(response) {
                if (response.error_code == 0)
                    params.onSuccess(response.data);
                else {
                    params.onError(response.message)
                }
            }).error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
    }

    this.operationCatalogs = function(params) {
        $http.get('/api/operation-catalogs')
            .success(function(response) {
                if (response.error_code == 0)
                    params.onSuccess(response.data);
                else {
                    params.onError(response.message)
                }
            }).error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
    }

    this.operationbookGet = function(params) {
        $http.get('api/operation-book/id/' + params.optBook_id)
            .success(function(response) {
                if (response.error_code == 0) {
                    params.onSuccess(response.data);
                } else {
                    params.onError(response.message)
                }
            }).error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
    }

    this.operationbooksPut = function(params) {
        $http.put('api/operation-book/id/' + params.optBook_id, data = params.data)
            .success(function(response) {
                if (response.error_code == 0) {
                    params.onSuccess(response.data);
                } else {
                    params.onError(response.message)
                }
            }).error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
    }

    this.operationbookCheck = function(params) {
        $http.post('api/system/id/' + params.sys_id + '/operation-book/script-check', data = params.data)
            .success(function(response) {
                if (response.error_code == 0) {
                    params.onSuccess(response.data);
                } else {
                    params.onError(response)
                }
            }).error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
    }

    this.operationbookDefinePost = function(params) {
        $http.post('api/operation-books', data = params.data)
            .success(function(response) {
                if (response.error_code == 0) {
                    params.onSuccess(response.data);
                } else {
                    params.onError(response.message)
                }
            }).error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
    }
    this.systemOptionBooksGet = function(params) {
        $http.get('api/system/id/' + params.sys_id + '/operation-books')
            .success(function(response) {
                if (response.error_code == 0) {
                    params.onSuccess(response.data);
                } else {
                    params.onError(response.message)
                }
            }).error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
    }
    this.systemOptionGroupPost = function(params) {
        $http.post('api/operation-groups', data = params.data)
            .success(function(response) {
                if (response.error_code == 0) {
                    params.onSuccess(response.data);
                } else {
                    params.onError(response.message)
                }
            }).error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
    }
    this.optionGroupEditPut = function(params) {
        $http.put('api/operation-group/id/' + params.optionGroup_id, data = params.data)
            .success(function(response) {
                if (response.error_code == 0) {
                    params.onSuccess(response.data);
                } else {
                    params.onError(response.message)
                }
            }).error(function(response) {
                console.log(response);
                $message.Alert(response.message);
            });
    }
    this.operationRecordsPost = function(params) {
        $http.get('api/operate-records')
            .success(function(response) {
                params.onSuccess(response.data);
            }).error(function(response) {
                console.log(response);
            });
    }
    this.operationPriviGet = function(params) {
        $http.get('api/user/privileges')
            .success(function(response) {
                params.onSuccess(response.data);
                console.log(response);
            }).error(function(response) {
                console.log(response);
            });
    }
    this.operationBookEditPut = function(params) {
        $http.put('api/operation-books', data = params.data)
            .success(function(response) {
                if (response.error_code == 0) {
                    params.onSuccess(response.data);
                } else {
                    params.onError(response.message);
                }
            }).error(function(response) {
                console.log(response);
            })
    }
}]);

app.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/dashboard', {
            templateUrl: 'UI/views/dashboard'
        })
        .when('/op_records', {
            templateUrl: 'UI/views/op_records'
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

app.run(function($rootScope, $websocket, $sessionStorage, $localStorage, $operationBooks) {
    $rootScope.tab = 1; //default
    $rootScope.status = "normal";
    $rootScope.GlobalConfigs = {
        svrStaticsInterval: { default: 60, current: 60 },
        sysStaticsInterval: { default: 60, current: 60 },
        loginStaticsInterval: { default: 60, current: 60 },
        sessionStaticsInterval: { default: 60, current: 60 },
        cpuIdleThreshold: { upper: 100, lower: 50 }
    }
    $operationBooks.operationPriviGet({
        onSuccess: function(res) {
            $rootScope.privileges = res.privileges;
            console.log($rootScope.privileges);
        },
        onError: function(res) {
            console.log(res);
        }
    });
});
app.controller('dashBoardControl', ['$scope', '$rootScope', function($scope, $rootScope) {
    $rootScope.isShowSideList = false;
}]);

app.filter('resultFilter', function() {
    return function(ListData, filterLimit, scope) {
        var newArr = new Array();
        angular.forEach(ListData, function(value, index) {
            var filted = false;
            if (value.operation.name.toLowerCase().match(filterLimit.operation) === null) {
                filted = true;
            }
            if (value.operator.name.toLowerCase().match(filterLimit.operator) === null) {
                filted = true;
            }
            if (value.authorizor) {
                if (value.authorizor.name.toLowerCase().match(filterLimit.authorizor) === null) {
                    filted = true;;
                }
            } else if (filterLimit.authorizor && filterLimit.authorizor !== "") {
                filted = true;
            }
            if (value.results[0] && value.results[0].error_code == 0 ? filterLimit.result == 'false' : filterLimit.result == 'true') {
                filted = true;;
            }
            if (filterLimit.executeStartDate) {
                if (filterLimit.executeStartTime) {
                    var startDateTimestampe = filterLimit.executeStartDate.getTime() +
                        filterLimit.executeStartTime.getTime() + 8 * 3600 * 1000;
                    var recordDateTimestampe = Date.parse(value.operated_at);
                    if (recordDateTimestampe < startDateTimestampe) {
                        filted = true;;
                    }
                } else {
                    var startDateTimestampe = filterLimit.executeStartDate.getTime();
                    var recordDateTimestampe = Date.parse(value.operated_at.match(/\d{4}-\d{2}-\d{2}/))
                    if (recordDateTimestampe < startDateTimestampe) {
                        filted = true;;
                    }
                }
            } else if (filterLimit.executeStartTime) {
                var startTimestamp = filterLimit.executeStartTime.getTime();
                var recordTimestamp = Date.parse('The Jan 01 1970 ' + value.operated_at.match(/\d{2}:\d{2}:\d{2}/) + ' GMT+0800');
                if (recordTimestamp < startTimestamp) {
                    filted = true;
                }
            }
            if (filterLimit.executeEndDate) {
                if (filterLimit.executeEndTime) {
                    var endDateTimestampe = filterLimit.executeEndDate.getTime() +
                        filterLimit.executeEndTime.getTime() + 8 * 3600 * 1000;
                    var recordDateTimestampe = Date.parse(value.operated_at);
                    if (recordDateTimestampe > endDateTimestampe) {
                        filted = true;;
                    }
                } else {
                    var endDateTimestampe = filterLimit.executeEndDate.getTime() + 24 * 3600 * 1000 - 1;
                    var recordDateTimestampe = Date.parse(value.operated_at.match(/\d{4}-\d{2}-\d{2}/));
                    if (recordDateTimestampe > endDateTimestampe) {
                        filted = true;;
                    }
                }
            } else if (filterLimit.executeEndTime) {
                var endTimestamp = filterLimit.executeEndTime.getTime();
                var recordTimestamp = Date.parse('The Jan 01 1970 ' + value.operated_at.match(/\d{2}:\d{2}:\d{2}/) + ' GMT+0800');
                if (recordTimestamp > endTimestamp) {
                    filted = true;
                }
            }
            if (!filted) {
                newArr.push(value);
            }
        })
        scope.pages = Math.ceil(newArr.length / scope.listsPerPage);
        return newArr;
    }
});

app.filter('paging', function() {
    return function(listsData, start) {
        if (listsData)
            return listsData.slice(start);
    }
});

app.controller('optionResultControl', ['$scope', '$operationBooks', function($scope, $operationBooks) {
    $scope.executeResult = [];
    $scope.operationName = null;
    $scope.loadingShow = true;
    $scope.filter_keywords = {};
    $scope.currentPage = 0;
    $scope.listsPerPage = 10;
    $operationBooks.operationRecordsPost({
        onSuccess: function(res) {
            $scope.operationRecordsData = res.records;
            $scope.pages = Math.ceil($scope.operationRecordsData.length / $scope.listsPerPage);
            $scope.loadingShow = false;
        }
    });
    $scope.$watch('pages', function() {
        $scope.pagesNum = [];
        for (var i = 0; i < $scope.pages; i++) {
            $scope.pagesNum.push(i);
        }
        $scope.currentPage = 0;
    });
    /* $scope.makePageList = function(length) {
        $scope.pages = Math.ceil(length / $scope.listsPerPage);
        $scope.pagesNum = [];
        for (var i = 0; i < $scope.pages; i++) {
            $scope.pagesNum.push(i);
        }
    } */
    $scope.setPages = function(num) {
        $scope.currentPage = num;
    }
    $scope.prePage = function() {
        if ($scope.currentPage > 0)
            $scope.currentPage--;
    }
    $scope.nextPage = function() {
        if ($scope.currentPage < $scope.pages - 1)
            $scope.currentPage++;
    }
    $scope.firstPage = function() {
        $scope.currentPage = 0;
    }
    $scope.lastPage = function() {
        $scope.currentPage = $scope.pages - 1;
    }
    $scope.show_result = function(index) {
        $('#op_result' + index).modal({ relatedTarget: this });
    };
}]);

app.controller('FileUpdateControl', ['$scope', 'fileUpload', function($scope, fileUpload) {
    $scope.sendFile = function() {
        var url = "api/global-config",
            file = $scope.fileToUpload;
        if (!file)
            alert("请选择需要上传的文件。")
        else
            fileUpload.uploadFileToUrl(file, url);
    }
}]);

app.controller('EditoptionBookController', ['$scope', '$operationBooks', function($scope, $operationBooks) {
    $operationBooks.operationBookSystemsGet({
        onSuccess: function(res) {
            $scope.optionBookData = res.records;
        }
    });
    $scope.selectWhichSystem = function(id) {

        $operationBooks.operationBookSystemListGet({
            sys_id: id,
            onSuccess: function(res) {
                $scope.optionBookSystemData = res.records;
            }
        });

        $operationBooks.systemOptionBooksGet({
            sys_id: id,
            onSuccess: function(res) {
                $scope.operationBooksData = res.records;
            }
        });
    }

    $scope.optionBookSelectedGet = function(id) {
        $operationBooks.operationbookGet({
            optBook_id: id,
            onSuccess: function(res) {

                $operationBooks.operationCatalogs({
                    onSuccess: function(res) {
                        $scope.optionBookEditBookData = res.records;
                    }
                });


                $scope.optionBookSystemOptBookData = res;
                if ($scope.optionBookSystemOptBookData.catalog) {
                    $scope.dataCopy = {
                        "sys_id": $scope.optionBookSystemOptBookData.system.id.toString(),
                        "catalog_id": $scope.optionBookSystemOptBookData.catalog.id.toString(),
                        "type": $scope.optionBookSystemOptBookData.type,
                        "description": $scope.optionBookSystemOptBookData.description,
                        "name": $scope.optionBookSystemOptBookData.name,
                        "is_emergency": $scope.optionBookSystemOptBookData.is_emergency.toString()
                    };
                } else {
                    $scope.dataCopy = {
                        "sys_id": $scope.optionBookSystemOptBookData.system.id.toString(),
                        "catalog_id": "",
                        "type": $scope.optionBookSystemOptBookData.type,
                        "description": $scope.optionBookSystemOptBookData.description,
                        "name": $scope.optionBookSystemOptBookData.name,
                        "is_emergency": $scope.optionBookSystemOptBookData.is_emergency.toString()
                    };
                }
            },
            onError: function(res) {
                console.log(res);
            }
        });
        $scope.isEmergency = [{
            "name": "紧急操作",
            "value": true
        }, {
            "name": "非紧急操作",
            "value": false
        }];
    }
    $scope.EditOptionBookPut = function(id) {
        $operationBooks.operationbooksPut({
            optBook_id: id,
            data: $scope.dataCopy,
            onSuccess: function(response) {
                alert("表单提交成功");
                window.location.reload();
            },
            onError: function(response) {
                alert("表单提交失败，错误代码" + response);
            }
        });
    }
}]);

app.controller('optionBookController', ['$scope', '$timeout', '$operationBooks', '$message', function($scope, $timeout, $operationBooks, $message) {
    $operationBooks.operationBookSystemsGet({
        onSuccess: function(res) {
            $scope.optionBookData = res.records;
        }
    });
    $operationBooks.operationCatalogs({
        onSuccess: function(res) {
            $scope.operationCatalogs = res.records;
        }
    });

    $scope.selectWhichSystem = function(id) {
        $operationBooks.operationBookSystemListGet({
            sys_id: id,
            onSuccess: function(res) {
                $scope.systemListData = res.records;
            }
        });
    }
    $scope.optionBookEditData = {
        "main_sys": "",
        "name": "",
        "description": "",
        "remote_name": "",
        "type": "",
        "catalog": "",
        "sys": "",
        "is_emergency": "",
        "mod": ""
    };
    $scope.optionBookCommand = [{
        "shell": "",
        "chdir": ""
    }];
    $scope.checkDataFull = function(data) {
        if (data.name == "" || data.sys == "" || data.type == "" || !$scope.optionBookShellIs)
            return true;
        else
            return false;
    }
    $scope.optionBookComAdd = function() {
        $scope.optionBookShellIs = false;
        $scope.optionBookNew = {};
        $scope.optionBookCommand.push($scope.optionBookNew);
    }
    $scope.optionBookShellIs = false;
    $scope.optionBookCheckShell = function(index, id) {
        if (id === undefined) {
            $message.ModelAlert("请选择系统", "modalInfoShowDefine");
            return;
        }
        $scope.optionBookShellIs = false;
        $scope.checkShow = true;
        $operationBooks.operationbookCheck({
            sys_id: id,
            data: $scope.optionBookCommand[index],
            onSuccess: function(response) {
                $message.ModelSucess("检查成功", "modalInfoShowDefine");
                // $scope.checkShow = false;
                $scope.optionBookShellIs = true;
            },
            onError: function(response) {
                $message.ModelAlert("检查失败,脚本文件不存在", "modalInfoShowDefine");
                // $scope.checkShow = false;
                if ($scope.optionBookCommand.length != 1) {
                    $scope.optionBookCommand.splice(index, 1);
                } else {
                    $scope.optionBookCommand[index].shell = "";
                    $scope.optionBookCommand[index].chdir = "";
                }
            }
        });
    }
    $scope.optionBookEditPost = function() {
        $scope.optionBookEditDataPost = {
            "name": $scope.optionBookEditData.name,
            "description": $scope.optionBookEditData.description,
            "remote_name": $scope.optionBookEditData.remote_name,
            "type": $scope.optionBookEditData.type,
            "catalog_id": $scope.optionBookEditData.catalog.id,
            "sys_id": $scope.optionBookEditData.sys.id,
            "mod": $scope.optionBookCommand
        };
        console.log($scope.optionBookEditDataPost);
        $operationBooks.operationbookDefinePost({
            data: $scope.optionBookEditDataPost,
            onSuccess: function(response) {
                $message.Success("表单提交成功");
                // window.location.reload();
            },
            onError: function(response) {
                $message.ModelAlert("表单提交失败，错误信息" + response, "modalInfoShowAdd");
            }
        });
    }
}]);

app.controller('Privileges', ['$rootScope', function($rootScope) {
    /*不可删除,用于获取$rootScope*/
}]);

app.controller('optionGroupController', ['$scope', '$q', '$operationBooks', '$rootScope', '$message', function($scope, $q, $operationBooks, $rootScope, $message) {
    $operationBooks.operationBookSystemsGet({
        onSuccess: function(res) {
            $scope.optionGroupSystem = res.records;
        },
        onError: function(res) {
            console.log(res);
        }
    })
    $scope.optionGroupConfirm = {
        "operation_group": {
            "sys_id": null,
            "name": null,
            "description": null
        },
        "operations": []
    };
    $scope.optionGroupDataBackup = [];
    $scope.optionBookInSysId = function(id) {
        $operationBooks.systemOptionBooksGet({
            sys_id: id,
            onSuccess: function(res) {
                $scope.optionGroupDataBackup = res.records;
            },
            onError: function(res) {
                console.log(res);
            }
        });
    }
    $scope.optionGroupName = null;
    $scope.optionGroupDescription = null;
    $scope.optionNowSelect = null;
    $scope.optionShow = false;
    $scope.detailInfo = "";
    $scope.optionGroupConfirmIsNull = false;
    $scope.infOfDetail = function(id) {
        if ($scope.optionGroupConfirm.operations.length != 0) {
            $scope.optionGroupConfirmIsNull = true;
        } else {
            $scope.optionGroupConfirmIsNull = false;
        }
        $scope.optionGroupConfirm.operation_group.name = $scope.optionGroupName;
        $scope.optionGroupConfirm.operation_group.description = $scope.optionGroupDescription;
        $scope.optionShow = true;
        angular.forEach($scope.optionGroupDataBackup, function(value, index) {
            if (id == value.id) {
                $scope.optionNowSelect = {
                    name: value.name,
                    description: value.description,
                    earliest: null,
                    latest: null
                };
                $scope.detailInfo = value.description;
            }
        });

    }
    $scope.optionSelectAdd = function() {
        $scope.optionGroupConfirm.operations.push($scope.optionNowSelect);
    };
    activate();

    function activate() {
        var promises = $scope.optionGroupConfirm.operations;
        return $q.all(promises).then(function() {
            // promise被resolve时的处理
            // console.log(promises);
        });
    }
    $scope.indexRight = null;
    $scope.optionSelectDel = function(index) {
        $scope.indexRight = index;
        console.log($scope.indexRight);
    }
    $scope.dbclickFunc = function() {
        if ($scope.indexRight) {
            $scope.optionGroupConfirm.operations.splice($scope.indexRight, 1);
            $scope.indexRight = null;
        }
    }
    $scope.formComfirm = false;
    $scope.loadingIcon = false;
    $scope.test2 = function() {
        $scope.formComfirm = !$scope.formComfirm;
        $scope.loadingIcon = !$scope.loadingIcon;
        $operationBooks.systemOptionGroupPost({
            data: $scope.optionGroupConfirm,
            onSuccess: function(response) {
                $scope.loadingIcon = !$scope.loadingIcon;
                $message.Success("表单提交成功");
                // window.location.reload();
                $rootScope.$broadcast('OperationGroupRenew')
                $scope.formComfirm = true;
            },
            onError: function(response) {
                $scope.loadingIcon = !$scope.loadingIcon;
                $message.Alert("表单提交失败，错误代码" + response);
                $scope.formComfirm = !$scope.formComfirm;
            }
        })
    }
}]);

app.controller('userController', ['$scope', '$http', '$rootScope', '$operationBooks', function($scope, $http, $rootScope, $operationBooks) {
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

app.controller('svrStaticsControl', ['$scope', '$servers', '$interval', '$routeParams', '$localStorage', '$rootScope', function($scope, $servers, $interval, $routeParams, $localStorage, $rootScope) {
    $scope.svrShowDetail = true;
    var sys_id = $routeParams.sysid;

    $scope.serverList = function() {
        $servers.ServerList({
            sysID: sys_id,
            onSuccess: function(data) {
                $scope.serverStatics = data.details;
                $scope.checkSvrStatics();
            },
            onError: function() {
                $scope.checking = false;
            }
        });
    }

    $scope.serverList();

    $scope.checkSvrStatics = function(force = false) {
        var started = $servers.CheckServerStatics({
            sysID: sys_id,
            onSuccess: function(data) {
                if (data.sys_id == sys_id) {
                    $scope.serverStatics = data.details;
                    $scope.serverStatics.showMountDetail = [];
                    angular.forEach(data.details.disks, function(value, index) {
                        $scope.serverStatics.showMountDetail.push(false);
                    });
                }
                if (data.cached != true) {
                    $scope.checking = false;
                }
            },
            onError: function() {
                $scope.checking = false;
            }
        }, force);
        if (started) {
            angular.forEach($scope.serverStatics, function(value, index) {
                value.uptime = '检查中...';
            });
            $scope.checking = true;
        }
    };

    $scope.autoRefresh = function() {
        if ($scope.auto) {
            $scope.svrStaticInterval = $interval(
                function() { $scope.checkSvrStatics(); },
                $rootScope.GlobalConfigs.svrStaticsInterval.current * 1000
            );
            $scope.checkSvrStatics();
        } else {
            $interval.cancel($scope.svrStaticInterval);
        }
    };

    $scope.$on('$destroy', function() {
        $interval.cancel($scope.svrStaticInterval);
    });
}]);

app.controller('sysStaticsControl', ['$scope', '$systems', '$interval', '$routeParams', '$rootScope', function($scope, $systems, $interval, $routeParams, $rootScope) {
    $scope.sysShowDetail = true;
    var sys_id;
    if ($routeParams.hasOwnProperty('sysid')) {
        sys_id = $routeParams.sysid;
    } else {

    }
    $scope.checkProc = function(force = false) {
        var started = $systems.SystemStaticsCheck({
            sysID: sys_id,
            onSuccess: function(data) {
                $scope.systemStatics = data.records;
                if (data.cached != true) {
                    $scope.checking = false;
                }
            },
            onError: function() {
                $scope.checking = false;
            }
        }, force);
        if (started) {
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
        }
    };
    $scope.autoRefresh = function() {
        if ($scope.auto) {
            $scope.sysStaticInterval = $interval(
                function() { $scope.checkProc(); },
                $rootScope.GlobalConfigs.sysStaticsInterval.current * 1000
            );
            $scope.checkProc();
        } else {
            $interval.cancel($scope.sysStaticInterval);
        }
    };

    $scope.$on('$destory', function() {
        $interval.cancel($scope.sysStaticInterval);
    })

    $systems.SystemList({
        sysID: sys_id,
        onSuccess: function(data) {
            $scope.systemStatics = data.records;
            $scope.checkProc();
        },
        onError: function() {
            $scope.checking = false;
        }
    })
}]);

app.controller('sideBarCtrl', ['$scope', '$uidatas', '$operationBooks', '$rootScope', '$location', '$timeout', function($scope, $uidatas, $operationBooks, $rootScope, $location, $timeout) {
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
        } else {
            // $scope.clearTabList();
            $rootScope.isShowSideList = false;
        }
    });
    $scope.$on('OperationGroupRenew', function() {
        // $timeout(function() {
        $scope.SideBarList();
        // }, 0);
    })
    $scope.SideBarList = function() {
        $uidatas.SideBarList({
            onSuccess: function(data) {
                $scope.listName = data.records;
            }
        });
    };
    $scope.SideBarList();
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
}]);

app.controller('opGroupController', ['$scope', '$operationBooks', '$operations', '$routeParams', '$location', '$rootScope', '$timeout', '$message', '$sessionStorage', function($scope, $operationBooks, $operations, $routeParams, $location, $rootScope, $timeout, $message, $sessionStorage) {
    /* $scope.$on('$routeChangeStart', function(evt, next, current) {
        var last = $scope.opList.details[$scope.opList.details.length - 1];
        if (last.exec_code != -1 && last.checker.isTrue && !last.checker.checked) {
            $location.url('/op_group/' + current.params.grpid);
            $message.Alert('还有未确认的操作结果！');
        }
    }); */

    $scope.triggered_ouside = false;
    $scope.batch_run = false;
    $scope.user_uuid = $('#user_uuid').text();
    $scope.taskQueueRunning = false;

    $scope.$on('TaskStatusChanged', function(event, data) {
        if (data.hasOwnProperty('details')) {
            $timeout(function() {
                $scope.opList = data;
                angular.forEach($scope.opList.details, function(value, index) {
                    delete $sessionStorage[value.uuid];
                });
            }, 0);
            $message.Warning('任务队列被重新初始化');
            $scope.taskQueueRunning = false;
            $scope.batch_run = false;
        } else {
            angular.forEach($scope.opList.details, function(value, index) {
                if (data.uuid == value.uuid) {
                    if (data.operator.operator_uuid != $scope.user_uuid) {
                        $scope.triggered_ouside = true;
                        if (data.exec_code == -2) {
                            $message.Warning('任务 "' + data.op_name + '" 被外部触发执行', 5);
                        }
                    } else {
                        $scope.triggered_ouside = false;
                    }
                    TaskStatus(data, index);
                }
            });
        }
    });

    $scope.GetOperationList = function() {
        $operations.Detail({
            groupID: $routeParams.grpid,
            onSuccess: function(data) {
                $scope.opList = data;
                TaskQueueStatus();
            }
        });
    }

    $scope.InitQueue = function() {
        $operations.InitQueue({
            groupID: $routeParams.grpid
        });
    }

    $scope.GetOperationList();

    $scope.check_result = function(index) {
        $('#result' + index).modal({
            relatedTarget: this,
            onConfirm: function() {
                $scope.$apply(function() {
                    if (index < $scope.opList.details.length - 1) {
                        $scope.opList.details[index + 1].enabled = true;
                    }
                    $scope.opList.details[index].checker.checked = true;
                    $sessionStorage[$scope.opList.details[index].uuid] = true;
                });
            }
        });
    };

    $scope.runAll = function() {
        var authorizor;
        $scope.batch_run = true;
        var terminate = false;
        var need_authorization = false;
        $scope.opList.details.forEach(function(value, index) {
            if (value.interactivator.isTrue) {
                $message.Alert('操作列表内包含交互式执行操作，无法批量运行');
                terminate = true;
                value.enabled = false;
            }
        });
        if (!terminate) {
            $operations.RunAll({
                groupID: $routeParams.grpid,
                onSuccess: function(data) {
                    $message.Info('批量任务执行开始');
                }
            });
        }
    };

    function TaskStatus(data, index) {
        $timeout(function() {
            $scope.opList.details[index] = data;
        }, 0);
        if (!$scope.batch_run) {
            if (!$scope.triggered_ouside && data.hasOwnProperty('output_lines') && data.output_lines.length > 0) {
                $scope.check_result(index);
            }
            if (index < $scope.opList.details.length - 1 && (!data.checker.isTrue || data.checker.checked)) {
                $scope.opList.details[index + 1].enabled = data.exec_code === 0;
            }
        } else {
            $timeout(function() {
                $scope.opList.details[index].enabled = false;
                if (data.checker.isTrue && data.exec_code == 0) {
                    $sessionStorage[data.uuid] = true;
                    $scope.opList.details[index].checker.checked = true;
                }
            }, 0);
        }
        if (index < $scope.opList.details.length - 1) {
            $scope.taskQueueRunning = true;
        } else if (data.exec_code == 0) {
            $scope.taskQueueRunning = false;
            $message.Success('任务全部完成', 10);
        }
    }

    function TaskQueueStatus() {
        angular.forEach($scope.opList.details, function(value, index) {
            if (index > 0 && $scope.opList.details[index - 1].checker.isTrue) {
                checked = $sessionStorage[$scope.opList.details[index - 1].uuid];
                $scope.opList.details[index].enabled = value.enabled && checked === true;
            }
            if (index < $scope.opList.details.length - 1) {
                $scope.taskQueueRunning = value.exec_code >= 0;
                if (value.checker.isTrue && $scope.opList.details[index + 1].exec_code == 0) {
                    $sessionStorage[value.uuid] = true;
                }
            } else if (value.exec_code == 0) {
                $scope.taskQueueRunning = false;
            }
            if (value.checker.isTrue) {
                $scope.opList.details[index].checker.checked = $sessionStorage[value.uuid] === true;
            }
        })
    }

    $scope.execute = function(index, id) {
        $scope.batch_run = false;
        if ($scope.opList.details[index].interactivator.isTrue) {
            $http.get('api/operation/id/' + id + '/ui')
                .success(function(response) {
                    $scope.opList.details[index].interactivator.template = response;
                    $('#interactive' + id).bind('results.quantdo', function(event, data) {
                        $scope.$apply(function() {
                            if ($routeParams.hasOwnProperty('grpid')) {
                                $scope.opList.details[index] = data;
                                TaskStatus(data);
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
                    $operations.RunNext({
                        operationID: id,
                        groupID: $routeParams.grpid,
                        authorizor: data,
                        onSuccess: function(data) {
                            $scope.opList.details[index] = data;
                        }
                    });
                });
                $('#authorizor').modal({
                    relatedTarget: this,
                    onCancel: function() {
                        $('#authorizeUser').val('');
                        $('#authorizePassword').val('');
                    }
                });
            } else {
                $operations.RunNext({
                    groupID: $routeParams.grpid,
                    operationID: id,
                    onSuccess: function(data) {
                        $scope.opList.details[index] = data;
                    }
                });
            }
        }
    };
    $scope.optionGroupEditShow = true;
    $scope.optionGroupSelect = 0;
    $scope.optionGroupEdit = function(data) {
        if ($rootScope.privileges.edit_group == false) {
            $message.Warning('该用户无编辑权限，无法编辑队列内容');
            return;
        }
        if ($scope.taskQueueRunning) {
            $message.Warning('任务队列未完成，无法编辑队列内容');
            return;
        }
        $operationBooks.systemOptionBooksGet({
            sys_id: data.sys_id,
            onSuccess: function(res) {
                $scope.optionBooks = res.records;
            },
            onError: function(res) {
                console.log(response);
            }
        })

        $scope.optionGroupCopy = {
            "operation_group": {
                "id": data.grp_id,
                "name": data.name,
                "description": null,
                "is_emergency": null
            },
            "operations": []
        };
        $scope.need_authorization = [{
            "name": "是",
            "value": true
        }, {
            "name": "否",
            "value": false
        }];
        $scope.optionOldData = angular.copy($scope.opList.details);
        angular.forEach($scope.optionOldData, function(value, index) {
            var data = new Object;
            data.operation_name = value.op_name;
            data.description = value.op_desc;
            data.earliest = value.time_range.lower;
            data.latest = value.time_range.upper;
            data.need_authorized = value.need_authorized;
            data.operation_id = value.id;
            $scope.optionGroupCopy.operations.push(data);
        })

        $scope.optionGroupSelectWhich = function(Id, data, index_id) {
            angular.forEach($scope.optionBooks, function(value, index) {
                if (value.id == Id) {
                    data.book_id = value.id;
                    data.description = value.description;
                    data.operation_name = value.name;
                    data.operation_id = "";
                }
            });
            var stringId = "#resetSelect" + index_id;
            $(stringId).val("0");
        }

        $scope.optionGroupEditShow = !$scope.optionGroupEditShow;
    }
    $scope.optionGroupEditAdd = function() {
        $scope.optionGroupNew = {};
        $scope.optionGroupCopy.operations.push($scope.optionGroupNew);
    }
    $scope.optionGroupEditCancel = function() {
        $scope.optionGroupEditShow = !$scope.optionGroupEditShow
    }
    $scope.optionGroupEditDelete = function(index_del) {
        //  	console.log($scope.optionGroupCopy.operations,index_del);
        $scope.optionGroupCopy.operations.splice(index_del, 1);
    }
    $scope.optionGroupEditPostShow = true;
    $scope.optionGroupEditFinish = function() {
        $operationBooks.optionGroupEditPut({
            optionGroup_id: $scope.optionGroupCopy.operation_group.id,
            data: $scope.optionGroupCopy,
            onSuccess: function(req) {
                $scope.optionGroupEditPostShow = !$scope.optionGroupEditPostShow;
                $scope.optionGroupEditShow = true;
                $message.Success("表单提交成功");
                $scope.GetOperationList();
            },
            onError: function(req) {
                $scope.optionGroupEditPostShow = !$scope.optionGroupEditPostShow;
                $message.Alert("表单提交失败，错误代码" + req);
            }
        })
    }
}]);

app.controller('emergeOpsController', ['$scope', '$http', '$routeParams', '$operationBooks', '$message', function($scope, $http, $routeParams, $operationBooks, $message) {
    $scope.optionBookEditDataList = new Array();
    $scope.optionBookEditShow = new Array();
    $http.get('api/system/id/' + $routeParams.sysid + '/catalogs/operation-books')
        .success(function(response) {
            $scope.emergeopList = response.data.records;
            for (var i = 0; i < $scope.emergeopList.length; i++) {
                $scope.optionBookEditDataList.push(null);
                $scope.optionBookEditShow.push(true);
            }
        })
        .error(function(response) {
            console.log(response);
        });

    $scope.optionBookEdit = function(data, index) {
        $scope.optionBookCatalog_id = data[0].catalog_id.toString();
        $scope.isEmergency = [{
            "name": "紧急操作",
            "value": true
        }, {
            "name": "非紧急操作",
            "value": false
        }];
        $scope.optionBookEditShow[index] = false;
        console.log($scope.optionGroupEditShow);
        $operationBooks.systemOptionBooksGet({
            sys_id: $routeParams.sysid,
            onSuccess: function(res) {
                $scope.optionBookData = res.records;
            }
        });
        $operationBooks.operationCatalogs({
            onSuccess: function(res) {
                $scope.operationCatalogs = res.records;
            }
        });
        $operationBooks.operationBookSystemListGet({
            sys_id: $routeParams.sysid,
            onSuccess: function(res) {
                $scope.systemListData = res.records;
            }
        });

        $scope.optionBookEditDataList[index] = new Array();
        $scope.optionOldData = angular.copy(data);
        angular.forEach($scope.optionOldData, function(value) {
            var data = new Object;
            data.op_name = value.op_name.toString();
            data.op_desc = value.op_desc.toString();
            data.type = value.type.toString();
            data.catalog_id = value.catalog_id.toString();
            // data.is_emergency = value.is_emergency.toString();
            data.disabled = value.disabled.toString();
            data.id = value.id;
            data.sys_id = value.sys_id.toString();
            data.connection = value.connection;
            $scope.optionBookEditDataList[index].push(data);
        })
        $scope.optionBookEditCancel = function(index) {
            $scope.optionBookEditShow[index] = true;
        }
        $scope.optionBookEditDelete = function(index_del) {
            $scope.optionBookEditDataList[index][index_del].disabled = "true";
        }
        $scope.optionBookEditPut = function() {
            $scope.optionBookEditDataListNew = {
                "data": $scope.optionBookEditDataList[index],
                "catalog_id": $scope.optionBookCatalog_id
            }
            $operationBooks.operationBookEditPut({
                data: $scope.optionBookEditDataListNew,
                onSuccess: function(res) {
                    $message.Success("提交成功");
                    $http.get('api/system/id/' + $routeParams.sysid + '/operation-books')
                        .success(function(response) {
                            $scope.emergeopList = response.data.records;
                            $scope.optionBookEditShow[index] = true;
                            console.log(response);
                        })
                        .error(function(response) {
                            console.log(response);
                        });

                },
                onError: function(res) {
                    console.log(res);
                }
            })

        }
    }

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

app.controller('loginStaticsControl', ['$scope', '$systems', '$interval', '$timeout', '$routeParams', '$rootScope', function($scope, $systems, $interval, $timeout, $routeParams, $rootScope) {
    $scope.loginShowDetail = true;
    $scope.loginStaticsShow = false;
    $scope.CheckLoginLog = function(force = false) {
        var started = $systems.LoginStaticsCheck({
            sysID: $routeParams.sysid,
            onSuccess: function(data) {
                angular.forEach(data.records, function(rspValue, rspIndex) {
                    angular.forEach($scope.loginStatics, function(value, index) {
                        if (rspValue.seat_id == value.seat_id) {
                            angular.merge(value, rspValue);
                        }
                    })
                });
                if (data.cached != true) {
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
    $rootScope.$watch('GlobalConfig.loginStaticsInterval.current', function(newValue, oldValue) {
        if (newValue != oldValue) {
            if (isNaN(newValue) || newValue < 30) {
                $scope.GlobalConfigs.loginStaticsInterval.current =
                    $scope.GlobalConfigs.loginStaticsInterval.default;
                return;
            } else {
                $interval.cancel($scope.loginStaticInterval);
                $scope.autoRefresh();
            }
        }
    }, true);
    $scope.autoRefresh = function() {
        if ($scope.auto) {
            $scope.loginStaticInterval = $interval(
                function() { $scope.CheckLoginLog(); },
                $rootScope.GlobalConfigs.loginStaticsInterval.current * 1000
            );
            $scope.CheckLoginLog();
        } else {
            $interval.cancel($scope.loginStaticInterval);
        }
    };
    $scope.$on('$destory', function() {
        $interval.cancel($scope.loginStaticInterval);
    })

    $systems.LoginList({
        sysID: $routeParams.sysid,
        onSuccess: function(data) {
            $scope.loginStaticsShow = true;
            $scope.loginStatics = data.records;
            $scope.CheckLoginLog();
        }
    })
}]);

app.controller('clientStaticsControl', ['$scope', '$systems', '$routeParams', '$interval', '$message', '$rootScope', function($scope, $systems, $routeParams, $interval, $message, $rootScope) {
    $scope.clientShowDetail = true;
    $scope.userSessionShow = false;
    $scope.CheckClientSessions = function(force = false) {
        var started = $systems.ClientSessionCheck({
            sysID: $routeParams.sysid,
            onSuccess: function(data) {
                $scope.userSessionShow = true;
                $scope.statusList = data.records;
                if (data.cached != true) {
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
                function() { $scope.CheckClientSessions(); },
                $rootScope.sessionStaticsInterval.current * 1000
            );
            $scope.CheckClientSessions();
        } else {
            $interval.cancel($scope.clientSessionInterval);
        }
    }
    $scope.$on('$destory', function() {
        $interval.cancel($scope.clientSessionInterval);
    })
    $scope.CheckClientSessions();
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

app.controller('messageControl', ['$scope', '$sessionStorage', function($scope, $sessionStorage) {
    $scope.messages = $sessionStorage.messages;
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
    }
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
                return "执行成功";
            case -2:
                return "执行中...";
            case -3:
                return "跳过执行";
            case -4:
                return "任务已调度";
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
            myChart.setOption(option.data);
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
                        data: idcs.data.records
                    }]
                });
            });
        }
    }
}]);