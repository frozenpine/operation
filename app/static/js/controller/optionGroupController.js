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
    $scope.optionBookInSysId = function() {
        var id = optionGroupConfirm.operation_group.sys_id;
        if (id === null || id === undefined) {
            return;
        }
        $operationBooks.systemOptionBooksGet({
            sys_id: id,
            onSuccess: function(res) {
                // $timeout(function() {
                $scope.optionGroupDataBackup = res.records;
                // });
            },
            onError: function(res) {
                console.log(res);
            }
        });
    };
    $scope.optionGroupName = null;
    $scope.optionGroupDescription = null;
    $scope.optionNowSelect = null;
    $scope.optionShow = false;
    $scope.detailInfo = "";
    $scope.optionGroupConfirmIsNull = true;
    $scope.infOfDetail = function(id) {
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
    };
    $scope.optionSelectAdd = function() {
        $scope.optionGroupConfirm.operations.push($scope.optionNowSelect);
        if ($scope.optionGroupConfirm.operations.length > 0) {
            $scope.optionGroupConfirmIsNull = false;
        } else {
            $scope.optionGroupConfirmIsNull = true;
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
            $scope.optionGroupConfirmIsNull = false;
        } else {
            $scope.optionGroupConfirmIsNull = true;
        }
    };
    // $scope.formComfirm = false;
    $scope.loadingIcon = false;
    $scope.addNewGroup = function() {
        // $scope.formComfirm = !$scope.formComfirm;
        $scope.loadingIcon = !$scope.loadingIcon;
        $scope.optionGroupConfirm.operation_group.name = $scope.optionGroupName;
        $scope.optionGroupConfirm.operation_group.description = $scope.optionGroupDescription;
        $scope.optionGroupConfirm.operation_group.trigger_time =
            $scope.optionGroupInittime !== undefined ? $scope.optionGroupInittime.getHours() + ':' + $scope.optionGroupInittime.getMinutes() : '';
        $scope.optionGroupConfirm.operation_group.is_emergency = $scope.optionGroupEmerge;
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
                    $scope.optionGroupName = undefined;
                    $scope.optionGroupDescription = undefined;
                    $scope.optionGroupInittime = undefined;
                    $scope.optionGroupEmerge = false;
                    $scope.optionNowSelect = undefined;
                    $scope.optionShow = false;
                    $scope.detailInfo = "";
                    $scope.optionGroupConfirmIsNull = true;
                    $scope.optionGroupDataBackup = undefined;
                    // $scope.formComfirm = false;
                }, 0);

                $rootScope.$broadcast('OperationGroupRenew');
                $('#addNewGroups').modal('close');
                $message.Success("表单提交成功");
            },
            onError: function(response) {
                $scope.loadingIcon = !$scope.loadingIcon;
                $message.ModelAlert("表单提交失败，错误代码" + response, 'modalInfoShowAdd');
                // $scope.formComfirm = true;
            }
        });
    };
}]);