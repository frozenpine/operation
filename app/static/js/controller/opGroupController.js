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
    $scope.taskQueueInitial = false;
    $scope.optionGroupEditShow = true;
    $scope.configChecked = false;
    $scope.optionGroupEditList = {
        operation_group: {},
        operations: []
    };

    $scope.$on('TaskStatusChanged', function(event, data) {
        if (data.hasOwnProperty('details')) {
            $timeout(function() {
                $scope.opList = data;
                angular.forEach($scope.opList.details, function(value, index) {
                    delete $sessionStorage[value.uuid];
                });
                delete $sessionStorage['configStatics_' + $routeParams.sysid]; // 删除缓存，强制配置文件检查刷新
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
            if (value.need_authorized) {
                need_authorization = true;
            }
        });
        if (!terminate && !need_authorization) {
            $operations.RunAll({
                groupID: $routeParams.grpid,
                onSuccess: function(data) {
                    $message.Info('批量任务执行开始');
                }
            });
        } else if (need_authorization) {
            $('#authorizor').bind('authorize.quantdo', function(event, data) {
                $('#authorizor').unbind('authorize.quantdo');
                $operations.RunAll({
                    groupID: $routeParams.grpid,
                    authorizor: data,
                    onSuccess: function(data) {
                        $message.Info('批量任务执行开始');
                    },
                    onError: function(response) {
                        console.log(response);
                        $message.Warning(response.message);
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
        }
    };

    function TaskStatus(data, index) {
        $timeout(function() {
            $scope.opList.details[index] = data;
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
        if ($scope.opList !== undefined) {
            angular.forEach($scope.opList.details, function(value, index) {
                $timeout(function() {
                    if (index === 0 && value.exec_code === -1) {
                        $scope.taskQueueInitial = true;
                    } else {
                        $scope.taskQueueInitial = false;
                    }
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
    }

    $scope.execute = function(index, id) {
        if ($scope.opList.status_code === 14) {
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
                                TaskStatus(data, index);
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
                    $('#authorizor').unbind('authorize.quantdo');
                    $operations.RunNext({
                        operationID: id,
                        groupID: $routeParams.grpid,
                        authorizor: data,
                        /* onSuccess: function(data) {
                            // $scope.opList.details[index] = data;
                            $scope.opList.details[index].enabled = false;
                        } */
                        onError: function(response) {
                            console.log(response);
                            $message.Warning(response.message);
                            angular.forEach($scope.opList.details, function(value, index) {
                                if (value.id === id) {
                                    value.enabled = true;
                                }
                            });
                        }
                    });
                    $scope.opList.details[index].enabled = false;
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
                    /* onSuccess: function(data) {
                        // $scope.opList.details[index] = data;
                        $scope.opList.details[index].enabled = false;
                    } */
                    onError: function(response) {
                        console.log(response);
                        $message.Warning(response.message);
                        angular.forEach($scope.opList.details, function(value, index) {
                            if (value.id === id) {
                                value.enabled = true;
                            }
                        });
                    }
                });
                $scope.opList.details[index].enabled = false;
            }
        }
    };

    $scope.optionGroupEdit = function() {
        $operationBooks.systemOptionBooksGet({
            sys_id: $routeParams.sysid,
            onSuccess: function(res) {
                $scope.optionBooks = res.records;
            },
            onError: function(res) {
                console.log(response);
            }
        });

        if ($rootScope.privileges.edit_group === false) {
            $message.Warning('该用户无编辑权限，无法编辑队列内容');
            return;
        }
        if ($scope.taskQueueRunning) {
            $message.Warning('任务队列未完成，无法编辑队列内容');
            return;
        }

        $scope.optionGroupEditList.operation_group.id = $scope.opList.grp_id;
        $scope.optionGroupEditList.operation_group.name = $scope.opList.name;
        $scope.optionGroupEditList.operation_group.description = null;
        $scope.optionGroupEditList.operation_group.is_emergency = null;
        $scope.optionGroupEditList.operations = [];
        angular.forEach($scope.opList.details, function(value, index) {
            $scope.optionGroupEditList.operations.push({
                operation_name: value.op_name,
                description: value.op_desc,
                earliest: formatTime(value.time_range.lower),
                latest: formatTime(value.time_range.upper),
                need_authorized: value.need_authorized,
                operation_id: value.id,
                book_id: value.book_id
            });
        });

        $scope.need_authorization = [{
            "name": "是",
            "value": true
        }, {
            "name": "否",
            "value": false
        }];

        $scope.optionGroupEditShow = !$scope.optionGroupEditShow;
    };
    $scope.optionGroupEditAdd = function() {
        $scope.optionGroupEditList.operations.push({});
    };
    $scope.obChange = function(op_item) {
        var selected_ob;
        angular.forEach($scope.optionBooks, function(value, index) {
            if (value.id == op_item.book_id) {
                selected_ob = value;
            }
        });
        op_item.operation_name = angular.copy(selected_ob.name);
        op_item.description = angular.copy(selected_ob.description);
    };
    $scope.optionGroupEditCancel = function() {
        $scope.optionGroupEditShow = !$scope.optionGroupEditShow;
    };
    $scope.optionGroupEditDelete = function(index_del) {
        $scope.optionGroupEditList.operations.splice(index_del, 1);
    };
    $scope.optionGroupEditPostShow = true;
    $scope.optionGroupEditFinish = function() {
        $operationBooks.optionGroupEditPut({
            optionGroup_id: $scope.optionGroupEditList.operation_group.id,
            data: $scope.optionGroupEditList,
            onSuccess: function(req) {
                $scope.optionGroupEditPostShow = !$scope.optionGroupEditPostShow;
                $scope.optionGroupEditShow = true;
                $message.Success("队列属性更新成功!");
                $scope.GetOperationList();
                if (!$scope.taskQueueRunning && $scope.taskQueueInitial && confirm('队列属性已更新,是否重新初始化队列?')) {
                    $scope.InitQueue();
                }
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
        }
    });

    $scope.$watch('taskQueueInitial', function(newValue, oldValue) {
        if (newValue !== oldValue && newValue) {
            $scope.CheckSystemConfig();
        }
    });

    $scope.$watch('taskQueueRunning', function(newValue, oldValue) {
        if (newValue) {
            $scope.checkingSystemConfig = false;
            $scope.configChecked = true;
        } else if (!$scope.taskQueueInitial) {
            $scope.checkingSystemConfig = false;
            $scope.configChecked = true;
        }
    });

    $scope.CheckSystemConfig = function(force) {
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
                    $scope.configCheckDate = data.last_request;
                    // console.log($scope.configChecked);
                }, 0);
            }
        }, force);
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
                        $scope.CheckSystemConfig(true);
                        $message.Success('配置文件HASH值更新成功。');
                    }
                });
            }
        }
    };
}]);