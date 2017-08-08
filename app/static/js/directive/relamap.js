var app = angular.module('myApp');
app.directive('relamap', [function () {
    return {
        restrict: 'A',
        link: link
    };

    function link(scope, element, attr) {
        var myChart = echarts.init(element[0]);
        myChart.showLoading();
        $.get('api/UI/relation', function (option) {
            myChart.hideLoading();
            myChart.setOption(option.data);
        });

        $(element[0]).resize(function () {
            myChart.resize();
        });
    }
}]);