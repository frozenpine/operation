app.controller('optionResultControl', ['$scope', '$operationBooks', function($scope, $operationBooks) {
    $scope.executeResult = [];
    $scope.operationName = null;
    $scope.loadingShow = true;
    $scope.filter_keywords = {};
    $scope.currentPage = 0;
    $scope.listsPerPage = 10;
    $scope.listCounts = [10, 20, 30, 50, 100];
    $operationBooks.operationRecordsPost({
        onSuccess: function(res) {
            $scope.operationRecordsData = res.records;
            $scope.pages = Math.ceil($scope.operationRecordsData.length / $scope.listsPerPage);
            $scope.loadingShow = false;
        }
    });
    $scope.$watch('listsPerPage', function() {
        if ($scope.operationRecordsData !== undefined) {
            $scope.pages = Math.ceil($scope.operationRecordsData.length / $scope.listsPerPage);
        }
    });
    $scope.$watch('pages', function() {
        $scope.pagesNum = [];
        for (var i = 0; i < $scope.pages; i++) {
            $scope.pagesNum.push(i);
        }
        $scope.currentPage = 0;
    });
    /* $scope.makePageList = function(length) {
        $scope.pages = Math.ceil(length / $scope.listsPerPage);
        $scope.pagesNum = [];
        for (var i = 0; i < $scope.pages; i++) {
            $scope.pagesNum.push(i);
        }
    } */
    $scope.setPages = function(num) {
        $scope.currentPage = num;
    };
    $scope.prePage = function() {
        if ($scope.currentPage > 0)
            $scope.currentPage--;
    };
    $scope.nextPage = function() {
        if ($scope.currentPage < $scope.pages - 1)
            $scope.currentPage++;
    };
    $scope.firstPage = function() {
        $scope.currentPage = 0;
    };
    $scope.lastPage = function() {
        $scope.currentPage = $scope.pages - 1;
    };
    $scope.show_result = function(index) {
        $('#op_result' + index).modal({ relatedTarget: this });
    };
}]);