var app = angular.module('myApp');
app.service("fileUpload", ["$http", function($http) {
    this.uploadFileToUrl = function(file, uploadUrl) {
        var fd = new FormData();
        fd.append("file", file)
        $http.post(uploadUrl, fd, {
                transformRequest: angular.identity,
                headers: { "Content-Type": undefined }
            })
            .success(function(res) {
                if (res.error_code == 0) {
                    alert("文件上传成功。");
                    window.location.reload();
                } else {
                    alert("数据已存在于数据库中。")
                }
            })
            .error(function(res) {
                alert(res.message);
            })
    }
}]);