# -*- coding: UTF-8 -*-
from . import resources
from .handlers.UserHandler import UserApi, UserListApi
from .handlers.DeviceHandler import DeviceApi, DeviceListApi
from .handlers.SystemHandler import SystemApi, SystemListApi
from .handlers.RoleHandler import RoleApi, RoleListApi
from .handlers.UIDataHandler import UIDataApi
from .handlers.OperationHandler import OperationListApi, OperationApi
from .handlers.SysStaticsHandler import (
    ServerStaticListApi, SystemStaticListApi,
    ServerStaticApi, ProcStaticApi
)

resources.add_resource(
    UserApi,
    '/user/login/<string:login>',
    '/user/id/<int:id>',
    methods=['GET'], endpoint='user'
)
resources.add_resource(
    UserListApi,
    '/users',
    '/users/',
    methods=['GET', 'POST'], endpoint='users'
)

resources.add_resource(
    DeviceApi,
    '/server/name/<string:name>',
    '/server/id/<int:id>',
    methods=['GET'],
    endpoint='server'
)
resources.add_resource(
    DeviceListApi,
    '/server',
    '/servers/',
    methods=['GET', 'POST'],
    endpoint='servers'
)

resources.add_resource(
    SystemApi,
    '/system/name/<string:name>',
    '/system/id/<int:id>',
    '/system/ip/<string:manage_ip>',
    methods=['GET'],
    endpoint='system'
)
resources.add_resource(
    SystemListApi,
    '/systems',
    '/systems/',
    methods=['GET', 'POST'],
    endpoint='systems'
)

resources.add_resource(
    RoleApi,
    '/role/name/<string:name>',
    '/role/id/<int:id>',
    methods=['GET'],
    endpoint='role'
)
resources.add_resource(
    RoleListApi,
    '/roles',
    '/roles/',
    methods=['GET', 'POST'],
    endpoint='roles'
)

resources.add_resource(
    OperationListApi,
    '/op_group/id/<int:id>',
    methods=['GET'],
    endpoint='operations'
)

resources.add_resource(
    OperationApi,
    '/operation/id/<int:id>',
    methods=['GET'],
    endpoint='operation'
)

resources.add_resource(
    ServerStaticListApi,
    '/system/id/<int:id>/svr_statics',
    '/system/id/<int:id>/svr_statics/',
    methods=['GET'],
    endpoint='svr_static_list'
)

resources.add_resource(
    ServerStaticApi,
    '/server/id/<int:id>/statics',
    '/server/id/<int:id>/statics/',
    methods=['GET'],
    endpoint='svr_statics'
)

resources.add_resource(
    SystemStaticListApi,
    '/system/id/<int:id>/sys_statics',
    '/system/id/<int:id>/sys_statics/',
    methods=['GET'],
    endpoint='sys_static_list'
)

resources.add_resource(
    ProcStaticApi,
    '/process/id/<int:id>/static',
    '/process/id/<int:id>/statics/',
    methods=['GET'],
    endpoint='proc_statics'
)

resources.add_resource(UIDataApi, '/UI/<string:name>', methods=['GET'], endpoint='UIdata')
