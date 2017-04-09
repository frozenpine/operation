var app = angular.module('myApp', ['ngRoute']);

app.config(['$routeProvider','$compileProvider', function($routeProvider,$compileProvider) {
	$routeProvider
		.when('/dashboard', {
			templateUrl: 'UI/views/dashboard',
			controller: 'dashBoardControl'
		})
		.when('/statics', {
			templateUrl: 'UI/views/statics',
			controller: 'svrStaticsControl'
		})
		.when('/system', {
			templateUrl: 'UI/views/system'
		})
		.when('/temp31', {
			templateUrl: 'template/template31.html'
		})
		.when('/temp32', {
			templateUrl: 'template/template32.html'
		})
		.when('/temp33', {
			templateUrl: 'template/template33.html'
		})
		.when('/temp5', {
			templateUrl: 'template/template4.html'
		})
		.otherwise({
			redirectTo: '/dashboard'
		});
}]);
app.run(function($rootScope){
	$rootScope.tab = 1;//default
});
app.controller('dashBoardControl', ['$scope', function($scope) {
	
}]);
app.controller('svrStaticsControl', ['$scope', '$http', function($scope, $http) {
	$http.get('api/system/id/1/svr_statics').success(function (data) {
        $scope.serverStatics = data;
   });
}]);
app.controller('sysStaticsControl', ['$scope', '$http', function($scope, $http) {
	$http.get('api/system/id/1/sys_statics').success(function (data) {
        $scope.systemStatics = data;
   });
}]);
app.controller('sideBarCtrl', ['$scope', '$http', function($scope, $http) {
	$http.get('api/UI/sideBarCtrl').success(function (data) {
        $scope.listName = data;
   });
	$scope.showListChage = function (id) {
		$scope.listName[id-1].isShow = !$scope.listName[id-1].isShow;
	}
}]);
app.controller('statusCtrl',['$scope','$http', function ($scope,$http) {
	$http.get('json/Status.json').success(function (data) {
		$scope.statusList = data[0].population;
		$scope.serverList = data[0].server;
		$scope.systemList = data[0].subSystem;
	});
	$('#cmdOut1').scrollTop($('#cmdOut1')[0].scrollHeight);
}]);
app.controller('singleSysCtrl',['$scope','$http', function ($scope,$http) {
	$http.get('json/Status.json').success(function (data) {
		$scope.systemList1 = data[0].subSystem;
	});
}])
app.controller('warningCtrl', ['$scope',function($scope){
	$scope.isRadioClick = false;
	$scope.tagSele = {
		statusNum: '',
		handleNum: ''
	};
	$scope.warningData = [{
		"id": 1,
		"name": "主机1号",
		"systemType": "Linux",
		"userType": "root",
		"Date": "展开详情",
		"Status": "正常",
		"statusNum": 0, 
		"handleStatus": "已处理",
		"handleNum": 0,
		"handle": "处理异常",
		"isDetailShow": true
	},{
		"secId": 1,
		"Date" : '详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭',
		"isDetailShow": false
	},{
		"id": 2,
		"name": "主机2号",
		"systemType": "windows",
		"userType": "user",
		"Date": "展开详情",
		"Status": "警告",
		"statusNum": 1,
		"handleStatus": "未处理",
		"handleNum": 1,
		"handle": "处理异常",
		"isDetailShow": true
	},{
		"secId": 2,
		"Date" : '详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭',
		"isDetailShow": false
	},{
		"id": 3,
		"name": "主机3号",
		"systemType": "Linux",
		"userType": "root",
		"Date": "展开详情",
		"Status": "危险",
		"statusNum": 2,
		"handleStatus": "未处理",
		"handleNum": 1,
		"handle": "处理异常",
		"isDetailShow": true
	},{
		"secId": 3,
		"Date" : '详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭',
		"isDetailShow": false
	},{
		"id": 4,
		"name": "主机3号",
		"systemType": "Linux",
		"userType": "root",
		"Date": "展开详情",
		"Status": "危险",
		"statusNum": 2,
		"handleStatus": "未处理",
		"handleNum": 1,
		"handle": "处理异常",
		"isDetailShow": true
	},{
		"secId": 4,
		"Date" : '详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭',
		"isDetailShow": false
	},{
		"id": 5,
		"name": "主机3号",
		"systemType": "Linux",
		"userType": "root",
		"Date": "展开详情",
		"Status": "危险",
		"statusNum": 2,
		"handleStatus": "未处理",
		"handleNum": 1,
		"handle": "处理异常",
		"isDetailShow": true
	},{
		"secId": 5,
		"Date" : '详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭',
		"isDetailShow": false
	},{
		"id": 6,
		"name": "主机3号",
		"systemType": "Linux",
		"userType": "root",
		"Date": "展开详情",
		"Status": "危险",
		"statusNum": 2,
		"handleStatus": "未处理",
		"handleNum": 1,
		"handle": "处理异常",
		"isDetailShow": true
	},{
		"secId": 6,
		"Date" : '详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭',
		"isDetailShow": false
	},{
		"id": 7,
		"name": "主机3号",
		"systemType": "Linux",
		"userType": "root",
		"Date": "展开详情",
		"Status": "危险",
		"statusNum": 2,
		"handleStatus": "未处理",
		"handleNum": 1,
		"handle": "处理异常",
		"isDetailShow": true
	},{
		"secId": 7,
		"Date" : '详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭',
		"isDetailShow": false
	},{
		"id": 8,
		"name": "主机1号",
		"systemType": "Linux",
		"userType": "root",
		"Date": "展开详情",
		"Status": "正常",
		"statusNum": 0,
		"handleStatus": "已处理",
		"handleNum": 0,
		"handle": "处理异常",
		"isDetailShow": true
	},{
		"secId": 8,
		"Date" : '详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭详细内容的是是我我我的饿饿人人封封封吃饭',
		"isDetailShow": false
	}];
	$scope.outData = [];
	$scope.ischeck = function(){
		$scope.isRadioClick = true;
		$scope.outData = [];
		angular.forEach($scope.warningData,function(o,index,array){
			if(($scope.tagSele.statusNum == o.statusNum && $scope.tagSele.handleNum == o.handleNum)){
				$scope.outData.push(o);
				$scope.outData.push(array[index+1]);
			}else if($scope.tagSele.statusNum == o.statusNum && $scope.tagSele.handleNum == ''){
				$scope.outData.push(o);
				$scope.outData.push(array[index+1]);
			}else if($scope.tagSele.statusNum == '' && $scope.tagSele.handleNum == o.handleNum){
				$scope.outData.push(o);
				$scope.outData.push(array[index+1]);
			}
		})
		console.log($scope.outData);
	};
	$scope.clearRadio = function(){
		$scope.isRadioClick = false;
		$scope.tagSele.statusNum = '';
		$scope.tagSele.handleNum = '';
	}
	$scope.showDetail = function(data){
		angular.forEach($scope.warningData,function(o){
			if(data.id == o.secId && data.name){
				o.isDetailShow = !o.isDetailShow;
			}
		})
	}
}]);
app.filter('filterStatus',function(){
	//return function (obj) {
	//	var newObj = [];
	//	angular.forEach(obj,function(o){
	//		if(o.id == 7){
	//			newObj.push(o);
	//		}
	//	});
	//	return newObj;
	//}
});
app.directive('echart', [function() {
	return {
		restrict: 'AE',
		scope: {
			echart: '='
		},
		link: link
	};

	function link(scope, element, attr) {
		var myChart = echarts.init(element[0]);
		// 指定图表的配置项和数据
		var defaultOption = {
			title: {
				text: '内存使用率',
				x: 'center'
			},
			tooltip: {
				trigger: 'item',
				formatter: "{a} <br/>{b} : {c} ({d}%)"
			},
			series: [{
				name: '内存使用',
				type: 'pie',
				radius: '55%',
				center: ['50%', '60%'],
				data: [{
					value: 1000,
					name: '已使用内存(MB)'
				}, {
					value: 3100,
					name: '剩余内存(MB)'
				}],
				itemStyle: {
					emphasis: {
						shadowBlur: 10,
						shadowOffsetX: 0,
						shadowColor: 'rgba(0, 0, 0, 0.5)'
					}
				}
			}]
		};
		// 使用刚指定的配置项和数据显示图表。
		myChart.setOption(defaultOption);

		// 双向传值
		// scope.$watch('echart', function(n, o) {
		//  if (n === o || !n) return;
		//  myChart.setOption(n);
		// });

		//当浏览器窗口发生变化的时候调用div的resize方法
		window.addEventListener('resize', chartResize);

		scope.$on('$destory', function() {
			window.removeEventListener('resize', chartResize);
		})

		function chartResize() {
			myChart.resize();
		}
	}
}]);
app.directive('echart2', [function() {
	return {
		restrict: 'AE',
		scope: {
			echart: '='
		},
		link: link
	};

	function link(scope, element, attr) {
		var myChart = echarts.init(element[0]);
		// 指定图表的配置项和数据
		var defaultOption = {
			title: {
				text: '内存使用率',
				x: 'center'
			},
			tooltip: {
				trigger: 'item',
				formatter: "{a} <br/>{b} : {c} ({d}%)"
			},
			series: [{
				name: '内存使用',
				type: 'pie',
				radius: '55%',
				center: ['50%', '60%'],
				data: [{
					value: 2000,
					name: '已使用内存(MB)'
				}, {
					value: 3100,
					name: '剩余内存(MB)'
				}],
				itemStyle: {
					emphasis: {
						shadowBlur: 10,
						shadowOffsetX: 0,
						shadowColor: 'rgba(0, 0, 0, 0.5)'
					}
				}
			}]
		};
		// 使用刚指定的配置项和数据显示图表。
		myChart.setOption(defaultOption);

		// 双向传值
		// scope.$watch('echart', function(n, o) {
		//  if (n === o || !n) return;
		//  myChart.setOption(n);
		// });

		//当浏览器窗口发生变化的时候调用div的resize方法
		window.addEventListener('resize', chartResize);

		scope.$on('$destory', function() {
			window.removeEventListener('resize', chartResize);
		})

		function chartResize() {
			myChart.resize();
		}
	}
}]);