# -*- coding: UTF-8 -*-
from . import resources
from .handlers.UserHandler import UserApi, UserListApi
from .handlers.DeviceHandler import DeviceApi, DeviceListApi
from .handlers.SystemHandler import SystemApi, SystemListApi
from .handlers.RoleHandler import RoleApi, RoleListApi
from .handlers.UIDataHandler import UIDataApi
from .handlers.OperationHandler import (
    OperationListApi, OperationApi, OperationCaptchaApi,
    OperationLoginApi, OperationExecuteApi, OperationUIApi,
    OperationCSVApi
)
from .handlers.TradingDayHandler import NextTradingDayApi
from .handlers.SysStaticsHandler import (
    ServerStaticListApi, SystemStaticListApi,
    ServerStaticApi, ProcStaticApi,
    LoginListApi, LoginCheckApi, UserSessionListApi
)
from .handlers.LogHandler import LogApi

resources.add_resource(
    UserApi,
    '/user/login/<string:login>',
    '/user/id/<int:id>',
    methods=['GET', 'PUT'], endpoint='user'
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
    methods=['POST'],
    endpoint='operation'
)

resources.add_resource(
    OperationUIApi,
    '/operation/id/<int:id>/ui',
    methods=['GET'],
    endpoint='operation_ui'
)

resources.add_resource(
    OperationCaptchaApi,
    '/operation/id/<int:id>/captcha',
    methods=['GET'],
    endpoint='operation_captcha'
)

resources.add_resource(
    OperationLoginApi,
    '/operation/id/<int:id>/login',
    methods=['POST'],
    endpoint='operation_login'
)

resources.add_resource(
    OperationExecuteApi,
    '/operation/id/<int:id>/execute',
    methods=['POST'],
    endpoint='operation_execute'
)

resources.add_resource(
    OperationCSVApi,
    '/operation/id/<int:id>/csv',
    methods=['POST'],
    endpoint='operation_csv'
)

resources.add_resource(
    NextTradingDayApi,
    '/nextTradingDay',
    methods=['GET'],
    endpoint='next_trading_day'
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
    '/system/id/<int:id>/svr_statics/check',
    '/system/id/<int:id>/svr_statics/check/',
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
    '/system/id/<int:id>/sys_statics/check',
    '/system/id/<int:id>/sys_statics/check/',
    methods=['GET'],
    endpoint='proc_statics'
)

resources.add_resource(
    LoginListApi,
    '/system/id/<int:id>/login_statics',
    '/system/id/<int:id>/login_statics/',
    methods=['GET'],
    endpoint='login_statics_list'
)

resources.add_resource(
    LoginCheckApi,
    '/system/id/<int:id>/login_statics/check',
    '/system/id/<int:id>/login_statics/check/',
    methods=['GET'],
    endpoint='login_statics'
)

resources.add_resource(
    UserSessionListApi,
    '/system/id/<int:id>/user_sessions',
    '/system/id/<int:id>/user_sessions/',
    methods=['GET'],
    endpoint='user_sessions'
)

resources.add_resource(LogApi, '/logs', methods=['POST'])

resources.add_resource(UIDataApi, '/UI/<string:name>', methods=['GET'], endpoint='UIdata')
