app.controller('mainController', ['$scope', '$rootScope', '$location', '$timeout', '$uidatas', '$operationBooks', '$users', function($scope, $rootScope, $location, $timeout, $uidatas, $operationBooks, $users) {
    $scope.messagePosition = {};
    $("body").scroll(function() {
        $timeout(function() {
            var topDistance = document.documentElement.scrollHeight || document.body.scrollHeight;
            if (topDistance > 200) {
                $scope.messagePosition = {
                    position: "fixed",
                    top: 0,
                    left: 0,
                    right: "15px",
                    zIndex: "999"
                };
            } else {
                $scope.messagePosition = {};
            }
        });
    });

    /* Code 4 SideBar Start */
    $scope.tabList = [];
    $scope.grpOrderEdit = {};
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
    $scope.SideBarList = function() {
        $uidatas.SideBarList({
            onSuccess: function(data) {
                $scope.listName = data.records;
                $scope.grpOrderEdit = [];
                angular.forEach($scope.listName, function(value, index) {
                    $scope.grpOrderEdit[value.id] = false;
                });
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
                $users({
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