/**
 * 模态框指令，包含header，footer
 * 传入body部分
 */
app.directive('modalDialog', function($http, $message) {
    return {
        restrict: 'EA',
        replace: true,
        scope: {
            headTitle: '@',
            subTitle: '@',
            /* dialogId: '@', */
            modalClass: '@',
            url: '@'
        },
        template: '<div ng-class="{{modalClass}}" class="am-modal" tabindex="-1">' +
            '<div class="am-modal-dialog">' +
            '<div class="am-modal-hd" style="font-weight: bold; color: #000">' +
            '{{headTitle}}' +
            '<div class="am-text-sm" ng-if="subTitle != undefined || subTitle != \'\'">{{subTitle}}</div>' +
            '</div>' +
            '<div class="am-modal-bd am-vertical-align" ng-bind-html="bodyHtml | html_trust">' +
            '<div ng-if="loading"><i class="am-icon-spinner am-icon-spic">Loading...</i></div>' +
            '</div>' +
            '<div class="am-modal-footer"> ' +
            '<span ng-if="modalClass != \'am-modal-alert\'" class="am-modal-btn" data-am-modal-cancel>取消</span>' +
            '<span ng-if="modalClass != \'am-modal-alert\'" class="am-modal-btn" data-am-modal-confirm>确定</span>' +
            '<span ng-if="modalClass == \'am-modal-alert\'" class="am-modal-btn">确定</span>' +
            '</div>' +
            '</div></div>',
        link: function($scope, $element, $attr) {
            // console.log(scope);
            /* $element.on('open.modal.amui', function() {
                $http.get($scope.url)
                    .success(function(response) {
                        $scope.bodyHtml = response;
                    })
                    .error(function(response) {
                        console.log(response);
                        $message.Alert(response.message);
                    });
            }); */
            $scope.$watch('url', function(newValue, oldValue) {
                if (newValue !== oldValue && newValue !== '') {
                    $scope.loading = true;
                    $http.get(newValue)
                        .success(function(response) {
                            $scope.bodyHtml = response;
                            $scope.loading = false;
                        })
                        .error(function(response) {
                            console.log(response);
                            $scope.loading = false;
                            if (response.hasOwnProperty('message')) {
                                $message.Alert(response.message);
                            }
                        });
                }
            });
        }
    };
});