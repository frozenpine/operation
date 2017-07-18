# -*- coding: UTF-8 -*-
from . import resources
from .handlers.DeviceHandler import DeviceApi, DeviceListApi
from .handlers.EmergeOpHandler import (EmergeOpApi, EmergeOpCaptchaApi,
                                       EmergeOpCSVApi, EmergeOpExecuteApi,
                                       EmergeOpListApi, EmergeOpLoginApi,
                                       EmergeOpUIApi)
from .handlers.LogHandler import LogApi
from .handlers.OperationHandler import (OperationApi, OperationCallbackApi,
                                        OperationCaptchaApi, OperationCSVApi,
                                        OperationExecuteApi, OperationListApi,
                                        OperationListRunAllApi,
                                        OperationListRunApi,
                                        OperationListSnapshotApi,
                                        OperationLoginApi, OperationUIApi)
from .handlers.RoleHandler import RoleApi, RoleListApi
from .handlers.SysStaticsHandler import (ConfigCheckApi, ConfigListApi,
                                         LoginCheckApi, LoginListApi,
                                         ProcStaticApi, ServerStaticApi,
                                         ServerStaticListApi,
                                         SystemStaticListApi,
                                         UserSessionListApi)
from .handlers.SystemHandler import SystemApi, SystemListApi
from .handlers.TradingDayHandler import NextTradingDayApi
from .handlers.UIDataHandler import UIDataApi
from .handlers.UserHandler import UserApi, UserListApi
from .handlers.WebshellHandler import WebshellUIApi

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
    methods=['GET', 'PUT'],
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
    methods=['GET', 'POST', 'PUT'],
    endpoint='operations'
)

resources.add_resource(
    OperationListRunApi,
    '/op_group/id/<int:id>/next',
    endpoint='op_group_next'
)

resources.add_resource(
    OperationListRunAllApi,
    '/op_group/id/<int:id>/all',
    endpoint='op_group_all'
)

resources.add_resource(
    OperationListSnapshotApi,
    '/op_group/id/<int:id>/snapshot',
    endpoint='op_group_snapshot'
)

resources.add_resource(
    OperationApi,
    '/operation/id/<int:id>',
    methods=['GET'],
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
    EmergeOpListApi,
    '/emerge_ops/system/id/<int:id>',
    methods=['GET'],
    endpoint='emerge_ops'
)

resources.add_resource(
    EmergeOpApi,
    '/emerge_ops/id/<int:id>',
    methods=['POST'],
    endpoint='emerge_op'
)

resources.add_resource(
    EmergeOpUIApi,
    '/emerge_ops/id/<int:id>/ui',
    methods=['GET'],
    endpoint='emergeop_ui'
)

resources.add_resource(
    EmergeOpCaptchaApi,
    '/emerge_ops/id/<int:id>/captcha',
    methods=['GET'],
    endpoint='emergeop_captcha'
)

resources.add_resource(
    EmergeOpLoginApi,
    '/emerge_ops/id/<int:id>/login',
    methods=['POST'],
    endpoint='emergeop_login'
)

resources.add_resource(
    EmergeOpExecuteApi,
    '/emerge_ops/id/<int:id>/execute',
    methods=['POST'],
    endpoint='emergeop_execute'
)

resources.add_resource(
    EmergeOpCSVApi,
    '/emerge_ops/id/<int:id>/csv',
    methods=['POST'],
    endpoint='emergeop_csv'
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

resources.add_resource(
    ConfigListApi,
    '/system/id/<int:id>/config_files',
    '/system/id/<int:id>/config_files/',
    methods=['GET'],
    endpoint='config_files_list'
)

resources.add_resource(
    ConfigCheckApi,
    '/system/id/<int:id>/config_files/check',
    '/system/id/<int:id>/config_files/check/',
    methods=['GET'],
    endpoint='config_files'
)

resources.add_resource(WebshellUIApi, '/webshell/system/id/<int:id>', methods=['GET'])

resources.add_resource(LogApi, '/logs', methods=['POST'])

resources.add_resource(UIDataApi, '/UI/<string:name>', methods=['GET'], endpoint='UIdata')

resources.add_resource(
    OperationCallbackApi,
    '/operation/uuid/<string:uuid>/callback',
    methods=['POST'],
    endpoint='op_callback'
)
