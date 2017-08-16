app.controller('mainController', ['$scope', '$rootScope', '$location', '$timeout', '$uidatas', '$operationBooks', '$users', '$message', function($scope, $rootScope, $location, $timeout, $uidatas, $operationBooks, $users, $message) {
    $rootScope.staticsShow = true;
    $scope.messagePosition = {};
    $scope.opGroupTriggerTime = {};
    $scope.opGroupEditList = {};
    $scope.grpOrderEdit = {};

    $('body').on('scroll', function(event) {
        if (event.offsetY >= 86) {
            $timeout(function() {
                $scope.messagePosition = {
                    position: "fixed",
                    top: "3px",
                    left: 0,
                    right: "15px",
                    zIndex: "999"
                };
            });
        } else {
            $timeout(function() {
                $scope.messagePosition = {};
            });
        }
    });

    /* Code 4 SideBar Start */
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
            $rootScope.isShowSideList = false;
        }
    });

    $scope.$on('OperationGroupRenew', function() {
        $timeout($scope.SideBarList(), 0);
    });

    function formatTime(time_string) {
        var match = time_string.match(/\d{1,2}:\d{1,2}(:\d{1,2})?/);
        if (match !== null) {
            var datetime = new Date('The Jan 01 1970 ' + match[0] + ' GMT+0800');
            return datetime;
        } else {
            return '';
        }
    }

    $scope.checkingSideBarList = false;
    $scope.SideBarList = function() {
        $scope.checkingSideBarList = true;
        $uidatas.SideBarList({
            onSuccess: function(data) {
                angular.forEach(data.records, function(value, index) {
                    $scope.grpOrderEdit[value.id] = false;
                    // $scope.opGroupEditList[value.id] = new Array(value.secondName.length);
                });
                $scope.listName = data.records;
                $scope.checkingSideBarList = false;
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

    /**
     * 改变左边侧边栏的排序和内容
     */

    $scope.groupEdit = function(data) {
        $scope.grpOrderEdit[data.id] = true;
        $scope.opGroupEditList[data.id] = [];
        angular.forEach(data.secondName, function(value, index) {
            $scope.opGroupEditList[data.id].push({
                id: value.id,
                name: value.name,
                trigger_time: formatTime(value.trigger_time),
                disabled: false
            });
        });
    };

    $scope.groupItemDelete = function(item) {
        item.disabled = true;
    };

    $scope.groupCheckData = function(id) {
        var flag = false;
        angular.forEach($scope.opGroupEditList[id], function(value, index) {
            if (value !== undefined && (value.name === undefined || value.trigger_time === undefined)) {
                flag = true;
            }
            return;
        });
        return flag;
    };

    $scope.changeSidebar = function(id) {
        var flag = false;
        angular.forEach($scope.opGroupEditList[id], function(value, index) {
            if (value !== undefined && (value.name === undefined || value.trigger_time === undefined)) {
                flag = true;
            }
            return;
        });
        if (flag) { $message.Warning('操作组数据不完整'); return; }
        var tempListData = angular.copy($scope.opGroupEditList[id]);
        for (var i = 0; i < tempListData.length; i++) {
            tempListData[i].trigger_time = $scope.opGroupEditList[id][i].trigger_time.getHours() + ':' +
                $scope.opGroupEditList[id][i].trigger_time.getMinutes();
        }
        // console.log($scope.listName);
        /* for (var i = 0; i < $scope.listName.length; i++) {
            for (var j = 0; j < $scope.listName[i].secondName.length; j++) {
                var listObj = {};
                listObj.id = $scope.listName[i].secondName[j].id.toString();
                listObj.name = $scope.listName[i].secondName[j].name;
                if (flag == $scope.listName[i].secondName[j].id) {
                    listObj.disabled = true;
                } else {
                    listObj.disabled = false;
                }
                if ($scope.listName[i].secondName[j].trigger_time instanceof Date) {
                    listObj.trigger_time =
                        $scope.listName[i].secondName[j].trigger_time.getHours() + ":" +
                        $scope.listName[i].secondName[j].trigger_time.getMinutes();
                } else {
                    listObj.trigger_time =
                        $scope.listName[i].secondName[j].trigger_time.substr(0, 5);
                }
                $scope.tempListData.push(listObj);
            }
        } */
        console.log($scope.tempListData);
        $uidatas.updateSideBar({
            data: tempListData,
            onSuccess: function(data) {
                $scope.SideBarList();
                $scope.grpOrderEdit[id] = false;
                $message.Success('修改操作组成功');
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
    /* Code 4 SideBar End */

    /* Code 4 User Start */
    $scope.ModifyPassword = function(usr_id) {
        $('#modifyPassword').modal({
            relatedTarget: this,
            onConfirm: function() {
                /* $http.put('api/user/id/' + usr_id, data = {
                    old_password: $('#oldPwd').val(),
                    password: $('#newPwd').val()
                }).success(function(response) {
                    console.log(response);
                }).error(function(response) {
                    console.log(response);
                }); */
                $users.ModifyPassword({
                    userID: usr_id,
                    data: {
                        old_password: $('#oldPwd').val(),
                        password: $('#newPwd').val()
                    },
                    onSuccess: function(data) {
                        $('#oldPwd').val('');
                        $('#newPwd').val('');
                    },
                    onError: function(data) {
                        // console.log(data);
                    }
                });
            }
        });
    };

    $scope.$watch('currentId', function() {
        if ($scope.currentId) {
            $users.GetPrivileges({
                userID: $scope.currentId,
                onSuccess: function(data) {
                    $rootScope.privileges = data.privileges;
                },
                onError: function(data) {
                    console.log(data);
                }
            });
        }
    });
    /* Code 4 User End */
}]);