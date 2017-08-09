app.directive('repeatFinish', function() {
    return {
        restrict: "A",
        scope: {
            onBind: '='
        }
    };
});