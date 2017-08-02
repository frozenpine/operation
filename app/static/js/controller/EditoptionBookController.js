var app = angular.module('myApp');
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