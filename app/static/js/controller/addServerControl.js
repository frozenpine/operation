app.controller('addServerControl',['$scope', '$systemServer', '$message', '$operationBooks', '$rootScope','$timeout', function($scope, $systemServer, $message, $operationBooks, $rootScope,$timeout){
	$scope.addServerRadio = 0;
	$scope.addServerData = null;
	$scope.editOrPost = true;
	$systemServer.systemTypesGet({
		onSuccess: function(res){
			$scope.systemTypes = res.records;
		},
		onError: function(res){
			$message.Alert("数据获取失败");
		}
	});
	$systemServer.systemVendorGet({
		onSuccess: function(res){
			$scope.systemVendors = res.records;
		}
	});
	$scope.clearSysData = function(){
		$scope.editOrPost = true;
		$scope.addServerData = {
				"name": "",
				"ip": "",
				"password": "",
				"user": "",
				"platform": "",
				"description": "",
				"disabled": false
			};
		$scope.newAddServerData = angular.copy($scope.systemProcessData);
	}
	$scope.editServerData = function(index){
		$scope.clearSysData();
		$scope.editOrPost = false;
        angular.forEach($scope.systemServerData,function(data,dataIndex){
            if(index != dataIndex){
                data.style = {};
            }
            else{
                data.style = {
                    backgroundColor: "#d7effb"
                };
            }
        });
		$scope.addServerData.name = $scope.systemServerData[index].name;
		$scope.addServerData.ip = $scope.systemServerData[index].manage_ip;
		$scope.addServerData.password = "";
		$scope.addServerData.user = $scope.systemServerData[index].admin_user;
		$scope.addServerData.platform = $scope.systemServerData[index].platform;
		$scope.addServerData.description = $scope.systemServerData[index].description;
		$scope.addServerData.id = $scope.systemServerData[index].id;
		$scope.addServerRadio = 0;
	};
	$scope.editSystemData = function(id){
		$scope.clearSysData();
		$scope.editOrPost = false;
        angular.forEach($scope.systemTreeData,function(data,dataIndex){
            if(id != data.id){
            	for(var i=0;i<data.child.length;i++){
            		if(id == data.child[i].id){
                        data.child[i].style = {
                            backgroundColor: "#d7effb"
                        };
					}
					else{
                        data.child[i].style = {};
					}
				}
                data.style = {};
            }
            else{
                for(var j=0;j<data.child.length;j++){
					data.child[j].style = {};
                }
                data.style = {
                    backgroundColor: "#d7effb"
                };
            }
        });
		$systemServer.getSystem({
			id: id,
			onSuccess: function(res) {
				$scope.childSystemData = res;
				$scope.addServerData.id = $scope.childSystemData.id;
				$scope.addServerData.name = $scope.childSystemData.name;
				$scope.addServerData.ip = $scope.childSystemData.manage_ip;
				$scope.addServerData.base_dir = $scope.childSystemData.base_dir;
				$scope.addServerData.user = $scope.childSystemData.login_user;
				$scope.addServerData.version = $scope.childSystemData.version;
				$scope.addServerData.description = $scope.childSystemData.description;
				if($scope.childSystemData.parent_system)
					$scope.addServerData.parent_sys_id = $scope.childSystemData.parent_system.id.toString();
				if($scope.childSystemData.vendor)
					$scope.addServerData.vendor_id = $scope.childSystemData.vendor.id.toString();
				if($scope.childSystemData.type)
					$scope.addServerData.type_id = $scope.childSystemData.type.id.toString();
				$scope.addServerRadio = 1;
			},
			onError: function(res){
				$message.Alert(res);
			}
			
		});
		
	};
	$scope.editServerDataPut = function(){
		$systemServer.editServer({
			data: $scope.addServerData,
			id: $scope.addServerData.id,
			onSuccess: function(res){
				$message.Success("服务器数据修改成功");
				$scope.clearSysData();
				$systemServer.serversGet({
					onSuccess: function(res) {
						$scope.systemServerData = res.records;
					}
				});
			},
			onError: function(res){
				$message.Alert(res);
			}
		})
	}
	$scope.editSystemDataPut = function(){
		$systemServer.editSystem({
			data: $scope.addServerData,
			id: $scope.addServerData.id,
			onSuccess: function(res){
				$message.Success("系统数据修改成功");
				$scope.clearSysData();
				$systemServer.serversGet({
					onSuccess: function(res) {
						$scope.systemServerData = res.records;
						$systemServer.getSystemTree({
							onSuccess: function(res) {
								$scope.systemTreeData = res;
							},
							onError: function(res) {
								$message.Alert(res);
							}
						})
					}
				});
			},
			onError: function(res){
				$message.Alert(res);
			}
		})
	}
	$systemServer.serversGet({
		onSuccess: function(res){
			$scope.systemServerData = res.records;
		}
	});
	$systemServer.getSystemTree({
		onSuccess: function(res){
			$scope.systemTreeData = res;
			$scope.systemTreeSecond = new Array();
			angular.forEach($scope.systemTreeData, function(value, index){
				$scope.systemTreeSecond.push(angular.copy(value));
				if(value.child.length > 0)
					for(var i = 0; i < value.child.length;i ++){
						$scope.systemTreeSecond.push(value.child[i]);
					}
			})
		},
		onError: function(res){
			$message.Alert(res);
		}
	})
	$scope.systemBelongGet = function(){
		$operationBooks.operationBookSystemsGet({
			onSuccess: function(res) {
				$scope.mainSystem = res.records;
				$scope.belongSystem = new Array();
				angular.forEach($scope.mainSystem, function(value, index) {
					$operationBooks.operationBookSystemListGet({
						sys_id: value.id,
						onSuccess: function(res) {
							angular.forEach(res.records, function(value2, index2) {
								var obj = new Object();
								obj = angular.copy(value2);
								$scope.belongSystem.push(obj);
							})
						}
					})
				});
			}
		});
	}
	$scope.systemBelongGet();
	$scope.$watch('addServerRadio',function(scope){
		if($scope.editOrPost == false){
			return;
		}
		if($scope.addServerRadio == 0) {
			$scope.clearSysData();
			$scope.checkDataFull = function(data) {
				if(data.name == "" || data.ip == "" || data.password == "" || data.user == "" || data.platform == "")
					return true;
				else
					return false;
			}
		}
		else{
			$scope.clearSysData();
			$scope.checkDataFull = function(data) {
				if(data.name == "" || data.ip == "" || data.password == "" || data.user == "")
					return true;
				else
					return false;
			}
		}
	});
	$scope.addSystemDataPost = function(){
		$systemServer.addSystem({
		data: $scope.addServerData,
		onSuccess: function(res){
			$message.Success("系统数据提交成功");
			$scope.clearSysData();
			$systemServer.getSystemTree({
				onSuccess: function(res) {
					$scope.systemTreeData = res;
					$scope.systemBelongGet();
				},
				onError: function(res) {
					$message.Alert(res);
				}
			})
		},
		onError: function(res){
			$message.Alert(res);
		}
		})
	}
	$scope.addServerDataPost = function(){
		$systemServer.addServer({
		data: $scope.addServerData,
		onSuccess: function(res){
			$message.Success("服务器数据提交成功");
			$scope.clearSysData();
			$systemServer.serversGet({
				onSuccess: function(res) {
					$scope.systemServerData = res.records;
				}
			});
		},
		onError: function(res){
			$message.Alert(res);
			}
		})
	}
	$scope.editProcessBtn = true;
	$systemServer.getProcess({
		onSuccess: function(res){
			$scope.systemProcessData = res.records;
			$scope.newAddServerData = angular.copy($scope.systemProcessData);
		},
		onError: function(res){
			$message.Alert(res);
		}
	});
	$scope.$watch('addServerData.name',function(newValue,oldValue,scope){
		if(newValue){
			$scope.newAddServerData = new Array();
			angular.forEach($scope.systemProcessData,function(value, index){
				if(value.server.name == newValue || value.system.name == newValue)
					$scope.newAddServerData.push(angular.copy(value));
			});
			console.log($scope.newAddServerData);
		}
	});
	$scope.editProcessData = function(){
		$scope.editProcessBtn = false;
		$scope.systemProcessDataCopy = new Array();
		angular.forEach($scope.newAddServerData,function(value,index){
			var data = new Object();
			data.name = value.name;
			data.description = value.description;
			data.type = value.type;
			data.exec_file = value.exec_file;
			data.sys_id = value.system.id.toString();
			data.base_dir = value.base_dir;
			data.svr_id = value.server.id.toString();
			data.param = value.param;
			data.id = value.id;
			data.disabled = value.disabled;
			$scope.systemProcessDataCopy.push(data);
		});
		$scope.addNewProcess = function(){
			var data = new Object();
			$scope.systemProcessDataCopy.push(data);
		}
	}
	$scope.processEditDelete = function(index){
		$scope.systemProcessDataCopy[index].disabled = true;
	}
	$scope.editProcessCancel = function(){
		$scope.editProcessBtn = true;
	}
	$scope.addProcessData = function(){
		$systemServer.addProcess({
			data: $scope.systemProcessDataCopy,
			onSuccess: function(res){
				$message.Success("进程数据提交成功");
				$systemServer.getProcess({
                        onSuccess: function(res) {
                            $scope.systemProcessData = res.records;
                            $scope.newAddServerData = [];
                            angular.forEach($scope.systemProcessData,function(value, index){
                                if(value.server.name == $scope.addServerData.name || value.system.name == $scope.addServerData.name)
                                    $scope.newAddServerData.push(angular.copy(value));
                            });
                        },
                        onError: function(res) {
                            $message.Alert(res);
                        }
                    });
				$scope.editProcessBtn = true;
			},
			onError: function(res){
				$message.Alert(res);
			}
		});
	}
	$scope.systemDataDelete = function(){
		$('#systemServerDelete').modal({
			relatedTarget: this,
			onConfirm: function(){
				$scope.addServerData.disabled = true;
				$scope.editSystemDataPut();
				$scope.systemBelongGet();
				console.log($scope.addServerData);
			}
		})
	}
	$scope.serverDataDelete = function(){
		$('#systemServerDelete').modal({
			relatedTarget: this,
			onConfirm: function(){
				$scope.addServerData.disabled = true;
				$scope.editServerDataPut();
				console.log($scope.addServerData);
			}
		})
	}
}]);