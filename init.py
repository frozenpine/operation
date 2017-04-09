# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from flask import url_for
from flask_script import Manager
from app import create_app, db
from app.models import (
    Operator, OpRole, OpPrivilege, MethodType, SystemDependece,
    Server, TradeProcess, TradeSystem, HaType, SystemType,
    OperationGroup, Operation
)

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import codecs
codecs.register(lambda name: name == 'cp65001' and codecs.lookup('utf-8') or None)

manager = Manager(create_app('development'))

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
    qdp_type = SystemType(name='QDP')
    qdiam_type = SystemType(name='QDIAM')
    ctp_type = SystemType(name='CTP')

    db.session.add_all([qdp_type, qdiam_type, ctp_type])
    db.session.commit()

    svr01 = Server(
        name='qdp01.shsq',
        manage_ip='10.47.55.21',
        admin_user='root',
        admin_pwd='quantdo123456'
    )
    svr02 = Server(
        name='qmarket01.shsq',
        manage_ip='10.47.55.22',
        admin_user='root',
        admin_pwd='quantdo123456'
    )
    qdp01 = TradeSystem(
        name=u'QDP上期1号',
        manage_ip='10.47.55.21',
        login_user='qdp',
        login_pwd='qdp',
        type_id=qdp_type.id
    )
    qdiam01 = TradeSystem(
        name=u'QDIAM上期1号',
        manage_ip='10.47.55.22',
        login_user='qdam',
        login_pwd='qdam',
        type_id=qdiam_type.id
    )
    ctp01 = TradeSystem(
        name='CTP主席',
        manage_ip='10.47.55.23',
        login_user='ctp',
        login_pwd='ctp',
        type_id=ctp_type.id
    )
    risk01 = TradeSystem(
        name='risk01',
        manage_ip='1.1.1.1',
        login_user='risk',
        login_pwd='risk'
    )
    risk02 = TradeSystem(
        name='risk02',
        manage_ip='1.1.1.2',
        login_user='risk',
        login_pwd='risk'
    )

    db.session.add_all([qdp01, qdiam01, ctp01, risk01, risk02, svr01, svr02])
    db.session.commit()

    qtrade1 = TradeProcess(name='qtrade', type=HaType.master, sys_id=qdp01.id, svr_id=svr01.id)
    qdata1 = TradeProcess(name='qdata', type=HaType.master, sys_id=qdp01.id, svr_id=svr01.id)
    qmdb1 = TradeProcess(name='qmdb', type=HaType.master, sys_id=qdp01.id, svr_id=svr01.id)
    qsdb1 = TradeProcess(name='qsdb', type=HaType.master, sys_id=qdp01.id, svr_id=svr01.id)
    qmarket1 = TradeProcess(name='qmarket', type=HaType.master, sys_id=qdp01.id, svr_id=svr02.id)
    risk01.parent_sys_id = qdiam01.id
    risk02.parent_system = qdiam01
    #sys_rel1 = SystemDependece(qdp01.id, qdiam01.id)
    #sys_rel2 = SystemDependece(ctp01.id, qdiam01.id)
    qdiam01.AddDependence(qdp01)
    qdiam01.AddDependence(ctp01)

    #db.session.add_all([qtrade1, qdata1, qmdb1, qsdb1, qmarket1, sys_rel1, sys_rel2, risk01, risk02])
    db.session.add_all([qtrade1, qdata1, qmdb1, qsdb1, qmarket1, risk01, risk02])
    db.session.commit()

@manager.command
def init_operation():
    qdp = TradeSystem.find(id=1)
    grp1 = OperationGroup(name=u'早盘操作')
    grp2 = OperationGroup(name=u'夜盘操作')
    grp3 = OperationGroup(name=u'周操作')
    qdp.operation_groups.append(grp1)
    qdp.operation_groups.append(grp2)
    qdp.operation_groups.append(grp3)

    db.session.add_all([grp1, grp2, grp3])
    db.session.commit()

@manager.command
def printurl():     
    print url_for('main.index'), url_for('main.adddevice')
    print url_for('auth.login'), url_for('auth.register')
    print url_for('api.users'), url_for('api.user', login='admin'), url_for('api.user', id=1)

@manager.command
def printuser():
    #user = Operator.find(login='admin')
    for user in Operator.query.all():
        print "username:", user.name
        for role in user.roles:
            print u"\trole name : ", role.name
            print u"\t\tprivileges : "
            for pri in role.privileges:
                print u"\t\t\t", pri.uri, pri.bit

@manager.command
def printsys():
    for sys in TradeSystem.query.filter(TradeSystem.parent_sys_id==None).all():
        print "system:", sys.name
        for svr in sys.servers:
            print "\tsvr info: {0} {1}".format(svr.name, svr.manage_ip)
            for proc in [p for p in sys.processes if p.svr_id == svr.id]:
                print "\t\tproc info: {0}({1})".format(proc.name, proc.id)
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

@manager.command
def modeltest():
    sys = TradeSystem.find(id=1)
    svr = Server.find(id=1)
    proc = TradeProcess.find(id=1)
    usr = Operator.find(id=1)
    print sys.to_json()
    #print svr.to_json()
    #print proc.to_json()
    #print usr.to_json()

if __name__ == '__main__':
    manager.run()
