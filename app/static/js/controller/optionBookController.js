app.controller('optionBookController', ['$scope', '$rootScope', '$timeout', '$operationBooks', '$message', function($scope, $rootScope, $timeout, $operationBooks, $message) {
    $scope.opBookShellFine = false;
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
    };
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

    $scope.optionBookComAdd = function() {
        $scope.optionBookShellIs = false;
        $scope.optionBookNew = {};
        $scope.optionBookCommand.push($scope.optionBookNew);
    };

    $scope.shellChanged = function() {
        $scope.opBookShellFine = false;
    };

    $scope.optionBookCheckShell = function(index, id) {
        if (id === undefined) {
            $message.ModelAlert("请选择系统", "modalInfoShowDefine");
            return;
        }
        $operationBooks.operationbookCheck({
            sys_id: id,
            data: $scope.optionBookCommand[index],
            onSuccess: function(response) {
                $message.ModelSucess("检查成功", "modalInfoShowDefine");
                $scope.checkShow = false;
                $scope.opBookShellFine = true;
            },
            onError: function(response) {
                $message.ModelAlert("检查失败,脚本文件不存在", "modalInfoShowDefine");
                $scope.checkShow = true;
                $scope.opBookShellFine = false;
                if ($scope.optionBookCommand.length != 1) {
                    $scope.optionBookCommand.splice(index, 1);
                } else {
                    $scope.optionBookCommand[index].shell = "";
                    $scope.optionBookCommand[index].chdir = "";
                }
            }
        });
    };
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
                $timeout(function() {
                    $scope.formComfirm = true;
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
                    $scope.optionBookEditDataPost = {};
                    $scope.opBookShellFine = false;
                }, 0);

                $rootScope.$broadcast('addNewOperateNode');
                $('#defineOptionBook').modal('close');
                $message.Success("表单提交成功");
            },
            onError: function(response) {
                $message.ModelAlert("表单提交失败，错误信息：" + response, "modalInfoShowDefine");
            }
        });
    };
}]);