app.controller('dataSourceController', ['$scope', '$timeout', '$datasources', '$systemServer', '$message', function($scope, $timeout, $datasources, $systemServer, $message) {
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
            if ($scope.dataSourceDefine.src_type === sourceType.SQL.id 
                && !$scope.dataSourceDefine.hasOwnProperty('charset')) {
                    $scope.dataSourceDefine.charset = 'utf8';
            }
            $scope.sourceModel = $datasources.getDsModel(newValue);
            $scope.dataSourceDefine = {
                sys_id: $scope.dataSourceDefine.sys_id,
                name: $scope.dataSourceDefine.name,
                description: $scope.dataSourceDefine.description,
                src_type: $scope.dataSourceDefine.src_type
            }
        }
    });
    $scope.$watch('dataSourceDefine.src_model', function(newValue, oldValue){
        if (newValue !== undefined && $scope.dataSourceDefine.src_model === $scope.sourceModel.Custom.id) {
            switch($scope.dataSourceDefine.src_type){
                case $scope.sourceType.SQL.id:
                    if (!$scope.dataSourceDefine.hasOwnProperty('formatter')) {
                        $scope.dataSourceDefine.formatter = [];
                    }
                    break;
                case $scope.sourceType.FILE.id:
                    if(!$scope.dataSourceDefine.hasOwnProperty('key_words')) {
                        $scope.dataSourceDefine.key_words = [];
                        $scope.keyword_valid = false;
                    }
                    break;
                default:
                    break;
            }
        } else {
            if ($scope.dataSourceDefine.hasOwnProperty('charset')) {
                delete $scope.dataSourceDefine.charset;
            }
            if ($scope.dataSourceDefine.hasOwnProperty('formatter')) {
                delete $scope.dataSourceDefine.formatter;
            }
        }
    });

    $scope.dataSourceDefine = {};

    $scope.clearForm = function() {
        $scope.dataSourceDefine = {}
        delete $scope.dataSourceDefineForm;
    };

    $scope.formatterDataType = {
        string: '字符串',
        number: '数字'
    };

    $scope.addDataSourceDefineFormatter = function() {
        $scope.dataSourceDefine.formatter.push({
            key: null,
            name: null,
            default: "",
            fmtSelection: null
        });
    };

    $scope.delDataSourceDefineFormatter = function(idx) {
        $scope.dataSourceDefine.formatter.splice(idx, 1);
    };

    $scope.addDataSourceDefine = function() {
        angular.forEach($scope.dataSourceDefine.formatter, function(value, index){
            delete value.fmtSelection;
            if (value.default === undefined) {
                value.default = "";
            }
        });
        $datasources.AddDataSource({
            data: $scope.dataSourceDefine,
            onSuccess: function(data) {
                // $message.Success("")
            },
            onError: function(data) {
                // $message.Error();
            }
        });
    };

    $scope.keyword_valid = true;
    $scope.addKeyword = function(keyword) {
        if (keyword !== undefined || keyword !== null || keyword !== "") {
            var exist = false;
            angular.forEach($scope.dataSourceDefine.key_words, function(value, index){
                if (value === keyword) {
                    exist = true;
                }
            })
            if (!exist) {
                $scope.dataSourceDefine.key_words.push(angular.copy(keyword));
                $scope.keyword_valid = true;
            }
        }
    }
    $scope.delKeyword = function(idx) {
        $scope.dataSourceDefine.key_words.splice(idx, 1);
    }
}]);
