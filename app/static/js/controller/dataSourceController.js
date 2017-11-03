app.controller('dataSourceController', ['$scope', '$timeout', '$datasources', '$systemServer', function($scope, $timeout, $datasources, $systemServer) {
    $scope.systemTreeSelected = undefined;

    var systemTreeView = [];
    function makeSystemTree(parent, nodes){
        nodes.forEach(function(value, index) {
            var node = {
                id: value.id,
                name: value.name,
                children: []
            };
            if(value.child.length > 0) {
                makeSystemTree(node.children, value.child);
            }
            parent.push(node);
        });
    }

    $systemServer.getSystemTree({
        onSuccess: function(response){
            makeSystemTree(systemTreeView, response);
            $scope.systemTree = angular.copy(systemTreeView);
        }
    });

    $scope.$watch('systemTreeSelected', function(newValue, oldValue){
        if(newValue !== undefined && newValue !== oldValue) {
            $scope.dataSourceDefine.sys_id = newValue.id;
        }
    });

    $scope.sourceType = $datasources.getDsType();
    $scope.sourceModel = $datasources.getDsModel();
    $scope.charset = [
        'utf8',
        'gbk',
        'gb2312',
        'ansi'
    ];

    $scope.$watch('dataSourceDefine.src_type', function(newValue, oldValue){
        if (newValue !== undefined && newValue !== oldValue) {
            $scope.sourceModel = $datasources.getDsModel(newValue);
        }
    })

    $scope.dataSourceDefine = $datasources.getDsDefault();

    $scope.clearForm = function() {
        $scope.dataSourceDefine = $datasources.getDsDefault();
    };

    $scope.formatterDataType = {
        string: '字符串',
        number: '数字'
    }

    $scope.formatterDataTypeSelection = {}

    $scope.addDataSourceDefineFormatter = function() {
        if (!$scope.dataSourceDefine.hasOwnProperty('formatter')) {
            $scope.dataSourceDefine.formatter = [];
        }
        var node = {
            key: null,
            name: null,
            default: null
        };
        $scope.dataSourceDefine.formatter.push(node);
    }
}]);
