# -*- coding: UTF-8 -*-
from . import resources
from flask import request
from flask_restful import Resource
from .handlers.UserHandler import UserApi, UserListApi
from .handlers.DeviceHandler import DeviceApi, DeviceListApi
from .handlers.SideBarHandler import SideBar

resources.add_resource(UserApi, '/users/<string:login>', 
                       methods=['GET', 'PUT'])
resources.add_resource(UserListApi, '/users', '/users/', 
                       methods=['GET', 'POST'])

resources.add_resource(DeviceApi, '/devices/<string:dev_name>', methods=['GET', 'PUT'])
resources.add_resource(DeviceListApi, '/devices', '/devices/', methods=['GET', 'POST'])

resources.add_resource(SideBar, '/sidebar', methods=['GET'])
