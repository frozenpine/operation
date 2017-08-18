app.directive('fixTop', function(scroll) {
    return {
        restrict: 'A',
        scope: {
            offsetTop: '@',
            fixStyle: '='
        },
        link: function(scope, element, attr) {
            scroll.bind();
            scope.$on('scroll', function(event, data) {
                if (data.y > scope.offsetTop) {
                    scope.fixStyle = {
                        position: "fixed",
                        top: "3px",
                        left: 0,
                        right: "15px",
                        zIndex: "999"
                    };
                } else {
                    scope.fixStyle = {};
                }
            });
        }
    };
});