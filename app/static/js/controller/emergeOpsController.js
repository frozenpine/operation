var app = angular.module('myApp');
app.controller('emergeOpsController', ['$scope', '$http', '$routeParams', '$operationBooks', '$message', function($scope, $http, $routeParams, $operationBooks, $message) {
    /* $scope.optionBookEditDataList = new Array();
    $scope.optionBookEditShow = new Array(); */
    $scope.$on('addNewOperateNode', function() {
        $scope.getOperateBookList();
    });

    $scope.getOperateBookList = function() {
        $http.get('api/system/id/' + $routeParams.sysid + '/catalogs/operation-books')
            .success(function(response) {
                $scope.emergeopList = [];
                $scope.emergeopList = response.data.records;
                $scope.optionBookEditDataList = [];
                $scope.optionBookEditShow = [];
                for (var i = 0; i < $scope.emergeopList.length; i++) {
                    $scope.optionBookEditDataList.push(null);
                    $scope.optionBookEditShow.push(true);
                }
            })
            .error(function(response) {
                console.log(response);
            });
    }
    $scope.getOperateBookList();

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
            data.disabled = value.disabled;
            data.id = value.id;
            data.sys_id = value.sys_id.toString();
            data.connection = value.connection;
            $scope.optionBookEditDataList[index].push(data);
        })
        $scope.optionBookEditCancel = function(index) {
            $scope.optionBookEditShow[index] = true;
        }
        $scope.optionBookEditDelete = function(index_del) {
            $scope.optionBookEditDataList[index][index_del].disabled = true;
        }
        $scope.optionBookEditPut = function() {
            $scope.optionBookEditDataListNew = {
                "data": $scope.optionBookEditDataList[index],
                "catalog_id": $scope.optionBookCatalog_id
            }
            $operationBooks.operationBookEditPut({
                data: $scope.optionBookEditDataListNew,
                onSuccess: function(res) {
                    $scope.optionBookEditShow[index] = true;
                    $message.Success("提交成功");
                    $scope.emergeopList = [];
                    $scope.getOperateBookList();
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