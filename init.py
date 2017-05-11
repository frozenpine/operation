# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from flask import url_for
from flask_script import Manager
from app import create_app, db
from app.models import (
    Operator, OpRole, OpPrivilege, MethodType, SystemDependece,
    Server, TradeProcess, TradeSystem, HaType, SystemType,
    OperationGroup, Operation, OperateRecord, OperateResult,
    DataSource, DataSourceType, DatasourceModel
)
import arrow
import json, re
from flask.testing import EnvironBuilder

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import codecs
codecs.register(lambda name: name == 'cp65001' and codecs.lookup('utf-8') or None)

test_app = create_app('development')
manager = Manager(test_app)

@manager.command
def create_db():
    db.create_all()

@manager.command
def drop_db():
    db.drop_all()

@manager.command
def init_auth():
    admin_role = OpRole('Admin')
    user_role = OpRole('User')
    admin_user = Operator('admin', 'admin', 'Administrator')
    test_user = Operator('test', 'test', 'Test')
    pri1 = OpPrivilege(uri='/api', bit=MethodType.all)
    pri2 = OpPrivilege(uri='/api', bit=MethodType.get)

    db.session.add_all([admin_role, user_role, admin_user, test_user, pri1, pri2])
    db.session.commit()

    admin_role.privileges.append(pri1)
    user_role.privileges.append(pri2)

    db.session.add_all([admin_role, user_role])
    db.session.commit()

    admin_user.roles.append(admin_role)
    admin_user.roles.append(user_role)
    test_user.roles.append(user_role)

    db.session.add_all([admin_user, test_user])
    db.session.commit()

@manager.command
def init_inventory():
    '''
    qdp_type = SystemType(name='QDP')
    qdiam_type = SystemType(name='QDIAM')
    ctp_type = SystemType(name='CTP')
    exchange_type = SystemType(name=u'大宗商品')

    db.session.add_all([qdp_type, qdiam_type, ctp_type, exchange_type])
    db.session.commit()

    svr01 = Server(
        name='trade+web_bak',
        manage_ip='192.168.101.100',
        admin_user='root',
        admin_pwd='quantdo123456'
    )
    svr02 = Server(
        name='web',
        manage_ip='192.168.101.102',
        admin_user='root',
        admin_pwd='quantdo123456'
    )
    svr03 = Server(
        name='front',
        manage_ip='192.168.101.124',
        admin_user='root',
        admin_pwd='quantdo123456'
    )
    qdiam = TradeSystem(
        name=u'QDIAM',
        manage_ip='192.168.101.100',
        login_user='qdam',
        login_pwd='qdam',
        type_id=qdiam_type.id
    )
    front = TradeSystem(
        name=u'前置子系统',
        manage_ip='192.168.101.124',
        login_user='qdam',
        login_pwd='qdam',
        type_id=qdiam_type.id
    )
    risk = TradeSystem(
        name=u'风控子系统',
        manage_ip='192.168.101.100',
        login_user='qdam',
        login_pwd='qdam',
        type_id=qdiam_type.id
    )
    web = TradeSystem(
        name=u'柜台子系统',
        manage_ip='192.168.101.102',
        login_user='quantdo',
        login_pwd='quantdo'
    )

    db.session.add_all([svr01, svr02, svr03, qdiam, front, risk, web])
    db.session.commit()

    qtrade = TradeProcess(name=u'交易核心', type=HaType.Master, sys_id=qdiam.id, svr_id=svr01.id, exec_file='qtrade')
    qquery = TradeProcess(name=u'查询核心', type=HaType.Master, sys_id=qdiam.id, svr_id=svr01.id, exec_file='qquery')
    qdata = TradeProcess(name=u'数据上场', type=HaType.Master, sys_id=qdiam.id, svr_id=svr01.id, exec_file='qdata')
    qmdb = TradeProcess(name=u'数据下场', type=HaType.Master, sys_id=qdiam.id, svr_id=svr01.id, exec_file='qmdb')
    qsdb = TradeProcess(name=u'qsdb', type=HaType.Master, sys_id=qdiam.id, svr_id=svr01.id, exec_file='qsdb')
    qmarket = TradeProcess(name=u'行情核心', type=HaType.Master, sys_id=qdiam.id, svr_id=svr01.id, exec_file='qmarket')
    qicegateway1 = TradeProcess(name=u'风控进程 1', type=HaType.Master, sys_id=risk.id, svr_id=svr01.id, exec_file='qicegateway', param='1')
    qicegateway2 = TradeProcess(name=u'风控进程 2', type=HaType.Slave, sys_id=risk.id, svr_id=svr01.id, exec_file='qicegateway', param='2')
    qmarket1 = TradeProcess(name=u'行情核心 1', type=HaType.Master, sys_id=front.id, svr_id=svr03.id, exec_file='qmarket', param='1')
    qmarket2 = TradeProcess(name=u'行情核心 2', type=HaType.Slave, sys_id=front.id, svr_id=svr02.id, exec_file='qmarket', param='2')
    mysql = TradeProcess(name=u'后台数据库', type=HaType.Master, sys_id=web.id, svr_id=svr02.id, exec_file='mysqld')
    web1 = TradeProcess(name=u'柜台进程 1', type=HaType.Master, sys_id=web.id, svr_id=svr02.id, exec_file='java', param='tomcat')
    web2 = TradeProcess(name=u'柜台进程 2', type=HaType.Slave, sys_id=web.id, svr_id=svr01.id, exec_file='java', param='tomcat')

    risk.parent_system = qdiam
    front.parent_system = qdiam
    web.parent_system = qdiam

    db.session.add_all([
        qtrade, qquery, qdata, qmdb, qsdb, qmarket, qicegateway1, qicegateway2,
        qmarket1, qmarket2, mysql, web1, web2, risk, front, web
    ])
    db.session.commit()
    '''
    sys = TradeSystem.find(id=1)
    db_src = DataSource(name=u'席位上场表')
    db_src.system = sys
    db_src.src_model = DatasourceModel.DbSeat
    db_src.source = {
        'uri': 'mysql+pymysql://qdam:qdam@192.168.101.100:3306/qdam?charset=utf8',
        'sql': """
            SELECT seat.seat_name, sync.tradingday, sync.frontaddr, sync.seatid 
            FROM t_seat seat, t_sync_seat sync , t_capital_account 
            WHERE seat.seat_id = t_capital_account.seat_id 
                AND sync.seatid=t_capital_account.account_id 
                AND sync.isactive = TRUE
        """,
        'formatter': [
            {'key': 'seat_name', 'default': ''},
            {'key': 'trading_day', 'default': ''},
            {'key': 'front_addr', 'default': ''},
            {'key': 'seat_id', 'default': ''},
            {'key': 'seat_status', 'default': u'未连接'},
            {'key': 'conn_count', 'default': 0},
            {'key': 'login_success', 'default': 0},
            {'key': 'login_fail', 'default': 0},
            {'key': 'disconn_count', 'default': 0}
        ]
    }
    db_session = DataSource(name=u'用户Session表')
    db_session.system = sys
    db_session.src_model = DatasourceModel.DbSession
    db_session.source = {
        'uri': 'mysql+pymysql://qdam:qdam@192.168.101.100:3306/qdam?charset=utf8',
        'sql': """
            SELECT a.brokerid, a.userid, a.usertype, a.sessionid, a.frontid, a.logintime,
                   a.ipaddress, a.macaddress, a.userproductinfo, a.interfaceproductinfo,
                   COUNT(a.id) AS total
            FROM (SELECT * FROM t_oper_usersession ORDER BY id DESC) a
            GROUP BY userid
        """,
        'formatter': [
            {'key': 'broker_id', 'default': ''},
            {'key': 'user_id', 'default': ''},
            {'key': 'user_type', 'default': ''},
            {'key': 'session_id', 'default': ''},
            {'key': 'front_id', 'default': ''},
            {'key': 'login_time', 'default': ''},
            {'key': 'ip_address', 'default': ''},
            {'key': 'mac_address', 'default': ''},
            {'key': 'prod_info', 'default': ''},
            {'key': 'inter_info', 'default': ''},
            {'key': 'total_login', 'default': 0}
        ]
    }

    log_seat = DataSource(name=u'交易系统Syslog')
    log_seat.system = sys
    log_seat.src_type = DataSourceType.FILE
    log_seat.src_model = DatasourceModel.LogSeat
    log_seat.source = {
        'formatter': [
            {"key": "seat_id", "default": ""},
            {"key": "seat_status", "default": ""},
            {"key": "conn_count", "default": 0},
            {"key": "login_success", "default": 0},
            {"key": "login_fail", "default": 0},
            {"key": "disconn_count", "default": 0}
        ],
        'uri': 'ssh://qdam:qdam@192.168.101.100:22/#/home/qdam/qtrade/bin/Syslog.log',
        'grep': 'OnFrontConnected|OnRspUserLogin|OnFrontDisConnected',
        'parser': {
            "pattern": r"^(.+us) .+EXID:([^,]+),SeatID:([^,]+),.+Main:\d+:(.+)$",
            "key_list": [
                "timestamp",
                "exid",
                "seatid",
                "message"
            ],
            "primary_key": "seatid",
            "skip_headline": True
        }
    }

    db.session.add_all([db_src, db_session, log_seat])
    db.session.commit()

@manager.command
def init_operation():
    sys1 = TradeSystem.find(id=1)
    grp1 = OperationGroup(name=u'早盘开盘操作')
    grp2 = OperationGroup(name=u'早盘收盘操作')
    grp3 = OperationGroup(name=u'夜盘开盘操作')
    grp4 = OperationGroup(name=u'夜盘收盘操作')
    sys1.operation_groups.append(grp1)
    sys1.operation_groups.append(grp2)
    sys1.operation_groups.append(grp3)
    sys1.operation_groups.append(grp4)

    db.session.add_all([grp1, grp2, grp3, grp4])
    db.session.commit()

@manager.command
def printurl():     
    print url_for('main.index'), url_for('main.adddevice')
    print url_for('auth.login'), url_for('auth.register')
    print url_for('api.users'), url_for('api.user', login='admin'), url_for('api.user', id=1)

@manager.command
def printuser():
    for user in Operator.query.all():
        print "username:", user.name
        for role in user.roles:
            print u"\trole name : ", role.name
            print u"\t\tprivileges : "
            for pri in role.privileges:
                print u"\t\t\t", pri.uri, pri.bit

@manager.command
def printsys():
    '''
    for sys in TradeSystem.query.filter(TradeSystem.parent_sys_id==None).all():
        print "system:", sys.name
        for svr in sys.servers:
            print "\tsvr info: {0} {1}".format(svr.name, svr.manage_ip)
            for proc in [p for p in sys.processes if p.svr_id == svr.id]:
                print "\t\tproc info: {0}({1})".format(proc.name, proc.id), proc.type
        print "child systems:"
        for child in sys.child_systems:
            print "\t", child.name
        print "up systems:"
        for up in sys.up_systems:
            print "\t", up.name
        print "down systems:"
        for down in sys.down_systems:
            print "\t", down.name
        print "administrators:"
        for usr in sys.administrators:
            print "\t", usr.name
    '''

    proc = TradeProcess.find(id=12)
    print proc.type.value

@manager.command
def modeltest():
    sys = TradeSystem.find(id=1)
    #svr = Server.find(id=1)
    #proc = TradeProcess.find(id=1)
    #usr = Operator.find(id=1)
    print sys.to_json()
    #from SysManager.Parsers import ymlParser
    #print ymlParser.Dump(sys.to_json())
    #print svr.to_json()
    #print proc.to_json()
    #print usr.to_json()
    '''
    op = Operation.find(id=6)
    records = OperateRecord.query\
        .filter(OperateRecord.operation_id==op.id)\
            .order_by(OperateRecord.operated_at.desc())
    print records.first().operated_at
    '''

@manager.command
def route_test():
    #print dir(test_app)
    '''
    urls = test_app.url_map.bind('localhost')
    a = urls.match('api/user/id/1')
    print a
    rsp = test_app.view_functions[a[0]](**a[1])
    print json.dumps(rsp.response)
    '''
    urls = test_app.url_map.bind('localhost')
    match = urls.match('api/user/id/1')
    with test_app.request_context(
        EnvironBuilder().get_environ()
    ):
        rsp = test_app.view_functions[match[0]](**match[1])
        print json.dumps(rsp.response)

if __name__ == '__main__':
    manager.run()
