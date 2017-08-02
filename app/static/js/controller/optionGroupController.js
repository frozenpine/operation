var app = angular.module('myApp');
app.controller('optionGroupController', ['$scope', '$q', '$operationBooks', '$rootScope', '$message', '$timeout', function($scope, $q, $operationBooks, $rootScope, $message, $timeout) {
    $operationBooks.operationBookSystemsGet({
        onSuccess: function(res) {
            $scope.optionGroupSystem = res.records;
        },
        onError: function(res) {
            console.log(res);
        }
    });
    $scope.optionGroupConfirm = {
        operation_group: {
            sys_id: null,
            name: null,
            description: null,
            trigger_time: null,
            is_emergency: false
        },
        operations: []
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
        $scope.optionGroupConfirm.operation_group.name = $scope.optionGroupName;
        $scope.optionGroupConfirm.operation_group.description = $scope.optionGroupDescription;
        $scope.optionGroupConfirm.operation_group.trigger_time =
            $scope.optionGroupInittime !== undefined ? $scope.optionGroupInittime.getHours() + ':' + $scope.optionGroupInittime.getMinutes() : '';
        $scope.optionGroupConfirm.operation_group.is_emergency = $scope.optionGroupEmerge;
        $scope.optionShow = true;
        angular.forEach($scope.optionGroupDataBackup, function(value, index) {
            if (id == value.id) {
                $scope.optionNowSelect = {
                    name: value.name,
                    description: value.description,
                    book_id: value.id,
                    earliest: null,
                    latest: null
                };
                $scope.detailInfo = value.description;
            }
        });

    }
    $scope.optionSelectAdd = function() {
        $scope.optionGroupConfirm.operations.push($scope.optionNowSelect);
        /* $scope.optionGroupConfirm.operation_group.name = $scope.optionGroupName;
        $scope.optionGroupConfirm.operation_group.description = $scope.optionGroupDescription;
        $scope.optionGroupConfirm.operation_group.trigger_time =
            $scope.optionGroupInittime !== undefined ? $scope.optionGroupInittime.getHours() + ':' + $scope.optionGroupInittime.getMinutes() : '';
        $scope.optionGroupConfirm.operation_group.is_emergency = $scope.optionGroupEmerge; */
        if ($scope.optionGroupConfirm.operations.length > 0) {
            $scope.optionGroupConfirmIsNull = true;
        } else {
            $scope.optionGroupConfirmIsNull = false;
        }
    };
    activate();

    function activate() {
        var promises = $scope.optionGroupConfirm.operations;
        return $q.all(promises).then(function() {
            // promise被resolve时的处理
            // console.log(promises);
        });
    }
    $scope.dbclickFunc = function(index) {
        $scope.optionGroupConfirm.operations.splice(index, 1);
        if ($scope.optionGroupConfirm.operations.length > 0) {
            $scope.optionGroupConfirmIsNull = true;
        } else {
            $scope.optionGroupConfirmIsNull = false;
        }
    }
    $scope.formComfirm = false;
    $scope.loadingIcon = false;
    $scope.addNewGroup = function() {
        // $scope.formComfirm = !$scope.formComfirm;
        $scope.loadingIcon = !$scope.loadingIcon;
        $operationBooks.systemOptionGroupPost({
            data: $scope.optionGroupConfirm,
            onSuccess: function(response) {
                $timeout(function() {
                    $scope.loadingIcon = !$scope.loadingIcon;
                    $scope.optionGroupConfirm = {
                        operation_group: {
                            sys_id: null,
                            name: null,
                            description: null,
                            trigger_time: null,
                            is_emergency: false
                        },
                        operations: []
                    };
                    $scope.optionGroupName = null;
                    $scope.optionGroupDescription = null;
                    $scope.optionGroupInittime = null;
                    $scope.optionGroupEmerge = false;
                    $scope.optionGroupName = null;
                    $scope.optionNowSelect = null;
                    $scope.optionShow = false;
                    $scope.detailInfo = "";
                    $scope.optionGroupConfirmIsNull = false;
                    $scope.formComfirm = false;
                }, 0);

                $rootScope.$broadcast('OperationGroupRenew');
                $('#addNewGroups').modal('close');
                $message.Success("表单提交成功");
            },
            onError: function(response) {
                $scope.loadingIcon = !$scope.loadingIcon;
                $message.ModelAlert("表单提交失败，错误代码" + response, 'modalInfoShowAdd');
                $scope.formComfirm = true;
            }
        })
    }
}]);