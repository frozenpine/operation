var app = angular.module('myApp');
app.directive('idcmap', [function() {
    return {
        restrict: 'A',
        link: link
    };

    function link(scope, element, attr) {
        $.get('api/UI/map?name=china', function(chinaJson) {
            echarts.registerMap('china', chinaJson);
            myChart = echarts.init(element[0]);
            myChart.showLoading();
            myChart.setOption({
                backgroundColor: '#fff',
                title: {
                    text: '数据中心分布',
                    left: '10px',
                    top: '10px'
                },
                tooltip: {
                    trigger: 'item',
                },
                toolbox: {
                    show: true,
                    feature: {
                        dataView: { show: true, readOnly: true },
                        restore: { show: true }
                    }
                },
                legend: {
                    orient: 'vertical',
                    y: 'bottom',
                    x: 'left',
                    data: ['数据中心'],
                    textStyle: {
                        color: '#111'
                    }
                },
                geo: {
                    map: 'china',
                    itemStyle: {
                        normal: {
                            borderColor: '#111'
                        }
                    }
                }
            });
            myChart.hideLoading();

            $(element[0]).resize(function() {
                //chartResize();
                myChart.resize();
            });

            getIDC();
        });

        function getIDC() {
            $.get('api/UI/idc', function(idcs) {
                myChart.setOption({
                    series: [{
                        name: '数据中心',
                        type: 'effectScatter',
                        coordinateSystem: 'geo',
                        showEffectOn: 'emphasis',
                        rippleEffect: {
                            period: 4,
                            scale: 3,
                            brushType: 'fill'
                        },
                        label: {
                            normal: {
                                show: true,
                                position: 'right',
                                formatter: '{b}'
                            }
                        },
                        symbolSize: function(val) {
                            return val[2];
                        },
                        itemStyle: {
                            normal: {
                                color: '#ddb926'
                            }
                        },
                        data: idcs.data.records
                    }]
                });
            });
        }
    }
}]);