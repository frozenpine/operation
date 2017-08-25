app.directive('fixTop', function(scroll) {
    return {
        restrict: 'A',
        scope: {
            topOffset: '@',
            fixStyle: '=',
            top: '@',
            left: '@',
            right: '@'
        },
        require: '',
        link: function(scope, element, attr, ctrl) {
            scroll.bind();
            scope.$on('scroll', function(event, data) {
                if (data.y > scope.topOffset) {
                    scope.fixStyle = {
                        position: "fixed",
                        top: scope.top,
                        left: scope.left,
                        right: scope.right,
                        zIndex: "999"
                    };
                } else {
                    scope.fixStyle = {};
                }
            });
        }
    };
});