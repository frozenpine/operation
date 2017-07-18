var app = angular.module('myApp', ['ngRoute', 'angular-sortable-view', 'ngStorage'], function($provide) {
    $provide.factory('globalVar', function() {
        return {
            'intervals': []
        };
    });

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

    $provide.factory('$websocket', function($rootScope, $location, $interval, $timeout, $message) {
        var connected = false;
        var reconnect = false;
        var heartbeat_interval;
        var unload = false;
        var ws;
        var topic_callbacks = {}

        var init = function() {
            if ("WebSocket" in window) {
                ws = new WebSocket("ws://" + $location.host() + ":5000/websocket");
                ws.onopen = function() {
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
            console.log('[Client] Closing websocket.')
            ws.close();
        };

        var onMessage = function(msg) {
            if (msg.hasOwnProperty('heartbeat')) {
                console.log('[Server] Heartbeat: ' + msg.heartbeat);
            } else if (msg.hasOwnProperty('topics')) {
                msg.topics.forEach(function(topic_name) {
                    topic_callbacks[topic_name] = new Set();
                    console.log('[Client] Subscribing topic: ' + topic_name);
                    ws.send(JSON.stringify({
                        method: 'subscribe',
                        topic: topic_name
                    }));
                });
            } else if (msg.hasOwnProperty('message')) {
                console.log('[Server] Message from server: ' + msg.message)
                $message.Info(msg.message);
            } else if (msg.hasOwnProperty('topic')) {
                switch (msg.topic) {
                    case "public":
                        $message.Info(msg.data);
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
            Send: function(msg) {
                ws.send(JSON.stringify(msg));
            },
            Close: function() { ws.close(); },
            Subscribe: function(topic_name, callback) {},
            UnSubscribe: function(topic_name, callback) {}
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
                if (response.hasOwnProperty('message')) {
                    $message.Alert(response.message);
                }
            });
    }
    this.InitQueue = function(params) {
        $http.post('api/op_group/id/' + params.groupID)
            .success(function(response) {
                $message.Success(response.message);
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
                $message.Success(response.message);
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
                params.onSuccess(response.data);
            })
            .error(function(response) {
                console.log(response);
                if (response.hasOwnProperty('message')) {
                    $message.Alert(response.message);
                }
            });
    }
});

app.service("$operationBooks", ["$http", function($http) {
    this.operationBookBaseInfoGet = function(params) {
        $http.get('api/operation-book-base-info')
            .success(function(response) {
                if (response.error_code == 0)
                    params.onSuccess(response.data);
            })
            .error(function(response) {
                console.log(response);
            });
    }
    this.oprationbooksGet = function(params) {
        $http.get('api/operation-books')
            .success(function(response) {
                if (response.error_code == 0)
                    params.onSuccess(response.data);
            })
            .error(function(response) {
                console.log(response);
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
            });
    }
    this.operationbookCheck = function(params) {
        $http.post('api/operation-book-check', data = params.data)
            .success(function(response) {
                if (response.error_code == 0) {
                    params.onSuccess(response.data);
                } else {
                    params.onError(response.message)
                }
            }).error(function(response) {
                console.log(response);
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
            });
    }
    this.systemOptionGroupGet = function(params) {
        $http.get('api/systems')
            .success(function(response) {
                if (response.error_code == 0)
                    params.onSuccess(response.data);
                else {
                    params.onError(response.message)
                }
            }).error(function(response) {
                console.log(response);
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
            });
    }
    this.operationRecordsPost = function(params) {
        $http.post('api/operate-records', data = {})
            .success(function(response) {
                params.onSuccess(response.records);
            }).error(function(response) {
                console.log(response);
            });
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
app.run(function($rootScope, $interval, $location, globalVar, $websocket) {
    $rootScope.tab = 1; //default
    $rootScope.user_uuid = '';
    $rootScope.$on('$routeChangeStart', function(evt, next, current) {
        console.log('route begin change');
        angular.forEach(globalVar.intervals, function(value, index) {
            $interval.cancel(value);
        });
        globalVar.intervals = [];
    });
    $rootScope.status = "normal";
    // $rootScope.Messenger = Message;
    if ($rootScope.LoginStatics === undefined) {
        $rootScope.LoginStatics = {};
    }
});
app.controller('dashBoardControl', ['$scope', '$rootScope', function($scope, $rootScope) {
    //$rootScope.Message = Message;
    $rootScope.isShowSideList = false;
}]);
app.filter('paging', function() {
    return function(listsData, start) {
        return listsData.slice(start);
    }
})
app.controller('optionResultControl', ['$scope', '$http', '$operationBooks', function($scope, $http, $operationBooks) {
    $operationBooks.operationRecordsPost({
        onSuccess: function(res) {
            $scope.operationRecordsData = res;
            console.log($scope.operationRecordsData);
            $scope.listsDataNum = $scope.operationRecordsData.length;
            $scope.pages = Math.ceil($scope.listsDataNum / 10);
            console.log($scope.pages);
        }
    });
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
app.controller('EditoptionBookController', ['$scope', '$http', '$operationBooks', function($scope, $http, $operationBooks) {
    $operationBooks.operationBookBaseInfoGet({
        onSuccess: function(res) {
            $scope.optionBookEditBookData = res;
        }
    });
    $operationBooks.oprationbooksGet({
        onSuccess: function(res) {
            $scope.optionBookSystemOptBookData = res.records;
        }
    });
    $scope.optionBookSelectedGet = function() {
        $scope.isEmergency = [{
            "name": "紧急操作",
            "value": true
        }, {
            "name": "非紧急操作",
            "value": false
        }];
        $scope.dataCopy = {
            "sys_id": $scope.optionBookSelected.system.id.toString(),
            "catalog_id": $scope.optionBookSelected.catalog.id.toString(),
            "type": $scope.optionBookSelected.type,
            "description": $scope.optionBookSelected.description,
            "name": $scope.optionBookSelected.name,
            "is_emergency": $scope.optionBookSelected.is_emergency.toString()
        };
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
app.controller('optionBookController', ['$scope', '$http', '$timeout', '$operationBooks', function($scope, $http, $timeout, $operationBooks) {
    $operationBooks.operationBookBaseInfoGet({
        onSuccess: function(res) {
            $scope.optionBookData = res;
        }
    });
    $scope.optionBookEditData = {
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
    $scope.optionBookCheckShell = function(index) {
        $scope.optionBookShellIs = false;
        $scope.checkShow = true;
        $operationBooks.operationbookCheck({
            data: $scope.optionBookCommand[index],
            onSuccess: function(response) {
                if (response == 0) {
                    alert("检查成功");
                    $scope.checkShow = false;
                    $scope.optionBookShellIs = true;
                } else {
                    alert("检查失败,脚本文件不存在");
                    $scope.checkShow = false;
                    if ($scope.optionBookCommand.length != 1)
                        $scope.optionBookCommand.splice(index, 1);
                    else {
                        $scope.optionBookCommand[index].shell = "";
                        $scope.optionBookCommand[index].chdir = "";
                    }
                }
            },
            onError: function(response) {
                console.log(response);
            }
        });
    }
    $scope.optionBookEditPost = function() {
        $scope.optionBookEditDataPost = {
            "name": $scope.optionBookEditData.name,
            "description": $scope.optionBookEditData.description,
            "remote_name": $scope.optionBookEditData.remote_name,
            "type": $scope.optionBookEditData.type.name,
            "catalog_id": $scope.optionBookEditData.catalog.catalog_id,
            "sys_id": $scope.optionBookEditData.sys.sys_id,
            "is_emergency": $scope.optionBookEditData.is_emergency,
            "mod": $scope.optionBookCommand
        };
        console.log($scope.optionBookEditDataPost);
        $operationBooks.operationbookDefinePost({
            data: $scope.optionBookEditDataPost,
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
app.controller('optionGroupController', ['$scope', '$http', '$q', '$operationBooks', '$window', function($scope, $http, $q, $operationBooks, $window) {

    //	$scope.cannotSort = false;
    $operationBooks.systemOptionGroupGet({
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
            if (id == value.book_id) {
                $scope.optionNowSelect = value;
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
            console.log(promises);
        });
    }
    $scope.dbclickFunc = function(index) {
        $scope.optionGroupConfirm.operations.splice(index, 1);
    }
    $scope.tes1 = function(data) {
        console.log(data);
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
                alert("表单提交成功");
                window.location.reload();
                $scope.formComfirm = !$scope.formComfirm;
            },
            onError: function(response) {
                $scope.loadingIcon = !$scope.loadingIcon;
                alert("表单提交失败，错误代码" + response);
                $scope.formComfirm = !$scope.formComfirm;
            }
        })
    }

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
                /*
                $scope.sysStaticInterval = $interval(function() { $scope.checkProc(); }, 30000);
                globalVar.intervals.push($scope.sysStaticInterval);
                */
            }
        })
        .error(function(response) {
            console.log(response);
            $scope.checking = false;
        });
}]);
app.controller('sideBarCtrl', ['$scope', '$http', '$operationBooks', '$rootScope', '$location', function($scope, $http, $operationBooks, $rootScope, $location) {
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
            // console.log($scope.listName);
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

app.controller('opGroupController', ['$scope', '$operationBooks', '$operations', '$routeParams', '$location', '$rootScope', '$timeout', '$message', '$sessionStorage', function($scope, $operationBooks, $operations, $routeParams, $location, $rootScope, $timeout, $message, $sessionStorage) {
    $scope.$on('$routeChangeStart', function(evt, next, current) {
        var last = $scope.opList.details[$scope.opList.details.length - 1];
        if (last.exec_code != -1 && last.checker.isTrue && !last.checker.checked) {
            $location.url('/op_group/' + current.params.grpid);
            alert('还有未确认的操作结果！');
        }
    });

    $scope.triggered_ouside = false;
    $scope.batch_run = false;
    $scope.user_uuid = $('#user_uuid').text();

    $scope.$on('TaskStatusChanged', function(event, data) {
        if (data.hasOwnProperty('details')) {
            $timeout(function() {
                $scope.opList = data;
            }, 0)
            angular.forEach($scope.opList.details, function(value, index) {
                delete $sessionStorage[value.uuid];
            });
            $message.Warning('任务队列被重新初始化');
        } else {
            angular.forEach($scope.opList.details, function(value, index) {
                if (data.uuid == value.uuid) {
                    if (data.user_session != $scope.user_uuid) {
                        $scope.triggered_ouside = true;
                        if (data.exec_code == -2) {
                            $message.Warning('任务 "' + data.op_name + '" 被外部触发执行', 5);
                        }
                    } else {
                        $scope.triggered_ouside = false;
                    }
                    $timeout(function() {
                        $scope.opList.details[index] = data;
                    }, 0);
                    TaskStatus(data, index);
                }
            });
        }
    });

    $operations.Detail({
        groupID: $routeParams.grpid,
        onSuccess: function(data) {
            $scope.opList = data;
            TaskQueueStatus();
        }
    });

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
                return;
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
    }

    function TaskStatus(data, index) {
        if (!$scope.batch_run && !$scope.triggered_ouside) {
            if (data.hasOwnProperty('output_lines') && data.output_lines.length > 0) {
                $scope.check_result(index);
            }
        } else {
            if (data.checker.isTrue && data.exec_code == 0) {
                $sessionStorage[data.uuid] = true;
                $timeout(function() {
                    $scope.opList.details[index].checker.checked = true;
                })
            }
        }
        if (index < $scope.opList.details.length - 1 && (!data.checker.isTrue || data.checker.checked)) {
            $scope.opList.details[index + 1].enabled = data.exec_code === 0;
        }
    }

    function TaskQueueStatus() {
        angular.forEach($scope.opList.details, function(value, index) {
            if (index > 0 && $scope.opList.details[index - 1].checker.isTrue) {
                checked = $sessionStorage[$scope.opList.details[index - 1].uuid];
                $scope.opList.details[index].enabled = value.enabled && checked === true;
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
                if (value.book_id == Id) {
                    data.book_id = value.book_id;
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
                    alert("表单提交成功");
                    window.location.reload();
                },
                onError: function(req) {
                    $scope.optionGroupEditPostShow = !$scope.optionGroupEditPostShow;
                    alert("表单提交失败，错误代码" + req);
                }
            })
            //  	$http({
            //  		method: 'put',
            //  		url: 'http://localhost:5000/api/operation-group/id/' + $scope.optionGroupCopy.operation_group.id,
            //  		data: $scope.optionGroupCopy
            //  	}).success(function(req) {
            //  		if(req.error_code == 0){
            //  			$scope.optionGroupEditPostShow = !$scope.optionGroupEditPostShow;
            //	    		alert("表单提交成功");
            //	    		window.location.reload();
            //  		}else{
            //  			$scope.optionGroupEditPostShow = !$scope.optionGroupEditPostShow;
            //	    		alert("表单提交失败，错误代码"+req.message);
            //  		}
            //  	});
    }
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