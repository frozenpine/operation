app.controller('opGroupController', ['$scope', '$operationBooks', '$operations', '$routeParams', '$location', '$rootScope', '$timeout', '$message', '$sessionStorage', '$systems', function($scope, $operationBooks, $operations, $routeParams, $location, $rootScope, $timeout, $message, $sessionStorage, $systems) {
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
    // $scope.queue_blocked = false;
    $scope.optionGroupEditShow = true;
    $scope.optionGroupSelect = [];
    $scope.optionEarliest = [];
    $scope.optionLatiest = [];
    $scope.configChecked = false;

    $scope.$on('TaskStatusChanged', function(event, data) {
        if (data.hasOwnProperty('details')) {
            $timeout(function() {
                $scope.opList = data;
                angular.forEach($scope.opList.details, function(value, index) {
                    delete $sessionStorage[value.uuid];
                });
                $scope.taskQueueRunning = false;
                $scope.batch_run = false;
            }, 0);
            TaskQueueStatus();
            $message.Warning('任务队列被重新初始化');
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

    function formatTime(time_string) {
        var match = time_string.match(/\d{2}:\d{2}:\d{2}/);
        if (match !== null) {
            var datetime = new Date('The Jan 01 1970 ' + match[0] + ' GMT+0800');
            return datetime;
        } else {
            return '';
        }
    }

    $scope.GetOperationList = function() {
        $operations.Detail({
            groupID: $routeParams.grpid,
            onSuccess: function(data) {
                $scope.opList = data;
                $scope.optionGroupSelect = new Array(data.details.length);
                $scope.optionEarliest = new Array(data.details.length);
                $scope.optionLatiest = new Array(data.details.length);
                angular.forEach($scope.opList.details, function(value, index) {
                    $scope.optionEarliest[index] = formatTime(value.time_range.lower);
                    $scope.optionLatiest[index] = formatTime(value.time_range.upper);
                });
                TaskQueueStatus();
            }
        });
    };

    $scope.InitQueue = function() {
        // $scope.queue_blocked = false;
        $operations.InitQueue({
            groupID: $routeParams.grpid
        });
    };

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

    $scope.resumeQueue = function() {
        $operations.ResumeQueue({
            groupID: $routeParams.grpid,
            onSuccess: function() {
                $timeout(function() {
                    // $scope.queue_blocked = false;
                    $scope.opList.status_code = 0;
                }, 0);
                $message.Success('队列已恢复');
                $scope.GetOperationList();
            },
            onError: function(data) {
                $message.Warning(data.message);
            }
        });
    };

    $scope.runAll = function() {
        if ( /* $scope.queue_blocked */ $scope.opList.status_code === 14) {
            $message.Warning('队列执行失败已阻塞，请先恢复队列。');
            return;
        }
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
            // $scope.queue_blocked = data.exec_code > 0;
            if (data.exec_code === 1) {
                $scope.opList.status_code = 14;
            }
        }, 0);
        if (!$scope.batch_run) {
            $timeout(function() {
                if (!$scope.triggered_ouside && data.hasOwnProperty('output_lines') && data.output_lines.length > 0) {
                    $scope.check_result(index);
                }
                if (index < $scope.opList.details.length - 1 && (!data.checker.isTrue || data.checker.checked)) {
                    $scope.opList.details[index + 1].enabled = data.exec_code === 0;
                }
            });
        } else {
            $timeout(function() {
                $scope.opList.details[index].enabled = false;
                if (data.checker.isTrue && data.exec_code === 0) {
                    $sessionStorage[data.uuid] = true;
                    $scope.opList.details[index].checker.checked = true;
                }
            }, 0);
        }
        if (index < $scope.opList.details.length - 1) {
            $scope.taskQueueRunning = true;
        } else if (data.exec_code === 0) {
            $scope.taskQueueRunning = false;
            $message.Success('任务全部完成', 10);
        }
    }

    function TaskQueueStatus() {
        $timeout(function() {
            angular.forEach($scope.opList.details, function(value, index) {
                /* if (value.exec_code > 0) {
                    // $scope.queue_blocked = true;
                    $scope.opList.status_code = 14;
                } */
                if (index > 0 && $scope.opList.details[index - 1].checker.isTrue) {
                    checked = $sessionStorage[$scope.opList.details[index - 1].uuid];
                    $scope.opList.details[index].enabled = value.enabled && checked === true;
                }
                if (index < $scope.opList.details.length - 1) {
                    $scope.taskQueueRunning = value.exec_code >= 0;
                    if (value.checker.isTrue && $scope.opList.details[index + 1].exec_code === 0) {
                        $sessionStorage[value.uuid] = true;
                    }
                } else if (value.exec_code === 0) {
                    $scope.taskQueueRunning = false;
                }
                if (value.checker.isTrue) {
                    $scope.opList.details[index].checker.checked = $sessionStorage[value.uuid] === true;
                }
            });
        });
    }

    $scope.execute = function(index, id) {
        if ( /* $scope.queue_blocked */ $scope.opList.status_code === 14) {
            $message.Warning('队列执行失败已阻塞，请先恢复队列。');
            return;
        }
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

    $scope.optionGroupEdit = function(data) {
        if ($rootScope.privileges.edit_group === false) {
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
        });

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
            var data = {
                operation_name: value.op_name,
                description: value.op_desc,
                earliest: null,
                latest: null,
                need_authorized: value.need_authorized,
                operation_id: value.id,
                book_id: value.book_id
            };
            $scope.optionGroupCopy.operations.push(data);
        });

        $scope.optionGroupSelectWhich = function(option, data) {
            angular.forEach($scope.optionBooks, function(value, index) {
                if (value.id == option.id) {
                    data.book_id = value.id;
                    data.description = value.description;
                    data.operation_name = value.name;
                }
            });
        };

        $scope.$watch('optionBooks', function() {
            angular.forEach($scope.opList.details, function(value, index) {
                angular.forEach($scope.optionBooks, function(v, i) {
                    if (value.book_id === v.id) {
                        $scope.optionGroupSelect[index] = v;
                    }
                });
            });
        });

        $scope.optionGroupEditShow = !$scope.optionGroupEditShow;
    };
    $scope.optionGroupEditAdd = function() {
        $scope.optionGroupNew = {};
        $scope.optionGroupCopy.operations.push($scope.optionGroupNew);
    };
    $scope.optionGroupEditCancel = function() {
        $scope.optionGroupEditShow = !$scope.optionGroupEditShow;
    };
    $scope.optionGroupEditDelete = function(index_del) {
        //  	console.log($scope.optionGroupCopy.operations,index_del);
        $scope.optionGroupCopy.operations.splice(index_del, 1);
    };
    $scope.optionGroupEditPostShow = true;
    $scope.optionGroupEditFinish = function() {
        angular.forEach($scope.optionGroupCopy.operations, function(value, index) {
            value.earliest = ($scope.optionEarliest[index] !== undefined &&
                    $scope.optionEarliest[index] !== null && $scope.optionEarliest[index] !== '') ?
                $scope.optionEarliest[index].getHours() + ':' + $scope.optionEarliest[index].getMinutes() : null;
            value.latest = ($scope.optionLatiest[index] !== undefined &&
                    $scope.optionLatiest[index] !== null && $scope.optionLatiest[index] !== '') ?
                $scope.optionLatiest[index].getHours() + ':' + $scope.optionLatiest[index].getMinutes() : null;
        });
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
        });
    };

    $systems.QuantdoConfigList({
        sysID: $routeParams.sysid,
        onSuccess: function(data) {
            $scope.configFileList = data.records;
            $scope.CheckSystemConfig();
        }
    });

    $scope.CheckSystemConfig = function() {
        $scope.checkingSystemConfig = true;
        $scope.configChecked = false;
        $systems.QuantdoConfigCheck({
            sysID: $routeParams.sysid,
            onSuccess: function(data) {
                var check_failed = false;
                angular.forEach(data.records, function(value, index) {
                    angular.forEach(value.detail, function(conf, idx) {
                        if (conf.hash_changed) {
                            check_failed = true;
                        }
                    });
                });
                if (check_failed) {
                    $message.Warning('配置文件被修改，确认配置前无法进行操作！', 10);
                }
                $timeout(function() {
                    $scope.configFileList = data.records;
                    $scope.checkingSystemConfig = false;
                    $scope.configChecked = !check_failed;
                    // console.log($scope.configChecked);
                }, 0);
            }
        });
    };

    $scope.confirmConfig = function(config) {
        if (config.hash_changed) {
            if (confirm('确认更新配置文件的HASH值？')) {
                config.updating = true;
                $systems.QuantdoConfigRenew({
                    configID: config.id,
                    onSuccess: function(data) {
                        $timeout(function() {
                            angular.forEach($scope.configFileList, function(value, index) {
                                angular.forEach(value.detail, function(conf, idx) {
                                    if (conf.uuid === data.uuid) {
                                        angular.merge(conf, data);
                                    }
                                });
                            });
                            config.updating = false;
                        }, 0);
                        $scope.CheckSystemConfig();
                        $message.Success('配置文件HASH值更新成功。');
                    }
                });
            }
        }
    };
}]);