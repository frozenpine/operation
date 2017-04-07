# -*- coding: UTF-8 -*-
from . import resources
from .handlers.UserHandler import UserApi, UserListApi
from .handlers.DeviceHandler import DeviceApi, DeviceListApi
from .handlers.SystemHandler import SystemApi, SystemListApi
from .handlers.RoleHandler import RoleApi, RoleListApi
from .handlers.SideBarHandler import SideBar

resources.add_resource(UserApi, 
                       '/user/login/<string:login>', 
                       '/user/id/<int:id>',
                       methods=['GET'], endpoint='user')
resources.add_resource(UserListApi, 
                       '/users', 
                       '/users/', 
                       methods=['GET', 'POST'], endpoint='users')

resources.add_resource(DeviceApi, 
                       '/server/name/<string:name>', 
                       '/server/id/<int:id>',
                       methods=['GET'], endpoint='server')
resources.add_resource(DeviceListApi, '/server', '/servers/', methods=['GET', 'POST'], endpoint='servers')

resources.add_resource(SystemApi, 
                       '/system/name/<string:name>', 
                       '/system/id/<int:id>',
                       '/system/ip/<string:manage_ip>',
                       methods=['GET'], endpoint='system')
resources.add_resource(SystemListApi, '/systems', '/systems/', methods=['GET', 'POST'], endpoint='systems')

resources.add_resource(RoleApi, 
                       '/role/name/<string:name>',
                       '/role/id/<int:id>',
                       methods=['GET'], endpoint='role')
resources.add_resource(RoleListApi, '/roles', '/roles/', methods=['GET', 'POST'], endpoint='roles')

resources.add_resource(SideBar, '/sidebar', methods=['GET'], endpoint='sidebar')
