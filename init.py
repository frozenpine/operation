# -*- coding: UTF-8 -*-
from flask import url_for
from flask_script import Manager
from app import create_app, db
from app.models import (Operator, OpRole, OpPrivilege, MethodType,
    Server, TradeProcess, TradeSystem, HaType, SystemType)

manager = Manager(create_app('development'))

@manager.command
def create_db():
    db.create_all()

@manager.command
def drop_db():
    db.drop_all()

@manager.command
def init_db():
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

    qdp_type = SystemType(name='QDP')
    qdiam_type = SystemType(name='QDIAM')
    ctp_type = SystemType(name='CTP')
    
    db.session.add_all([qdp_type, qdiam_type, ctp_type])
    db.session.commit()

    svr01 = Server(name='qdp01.shsq', 
        manage_ip='10.47.55.21',
        admin_user='root', 
        admin_pwd='quantdo123456'
    )
    svr02 = Server(name='qmarket01.shsq', 
        manage_ip='10.47.55.22',
        admin_user='root', 
        admin_pwd='quantdo123456'
    )
    qdp01 = TradeSystem(name=u'上期大厦1号', 
        manage_ip='10.47.55.21',
        login_user='qdp',
        login_pwd='qdp',
        type_id=qdp_type.id
    )
    qdp02 = TradeSystem(name=u'上期大厦2号', 
        manage_ip='10.47.55.21',
        login_user='qdp',
        login_pwd='qdp',
        type_id=qdp_type.id
    )
    qtrade1 = TradeProcess(name='qtrade', type=HaType.master)
    qdata1 = TradeProcess(name='qdata', type=HaType.master)
    qmdb1 = TradeProcess(name='qmdb', type=HaType.master)
    qsdb1 = TradeProcess(name='qsdb', type=HaType.master)
    qmarket1 = TradeProcess(name='qmarket', type=HaType.master)
    qtrade2 = TradeProcess(name='qtrade', type=HaType.master)
    qdata2 = TradeProcess(name='qdata', type=HaType.master)
    qmdb2 = TradeProcess(name='qmdb', type=HaType.master)
    qsdb2 = TradeProcess(name='qsdb', type=HaType.master)
    qmarket2 = TradeProcess(name='qmarket', type=HaType.master)

    db.session.add_all(
        [svr01, svr02, qdp01, qdp02,
         qtrade1, qdata1, qmdb1, qsdb1, qmarket1,
         qtrade2, qdata2, qmdb2, qsdb2, qmarket2]
    )
    db.session.commit()

    qtrade1.sys_id = qdp01.id
    qtrade1.svr_id = svr01.id
    qdata1.sys_id = qdp01.id
    qdata1.svr_id = svr01.id
    qmdb1.sys_id = qdp01.id
    qmdb1.svr_id = qdp01.id
    qsdb1.sys_id = qdp01.id
    qsdb1.svr_id = svr01.id
    qmarket1.sys_id = qdp01.id
    qmarket1.svr_id = svr02.id
    qtrade2.sys_id = qdp02.id
    qtrade2.svr_id = svr02.id
    qdata2.sys_id = qdp02.id
    qdata2.svr_id = svr02.id
    qmdb2.sys_id = qdp02.id
    qmdb2.svr_id = qdp02.id
    qsdb2.sys_id = qdp02.id
    qsdb2.svr_id = svr02.id
    qmarket2.sys_id = qdp02.id
    qmarket2.svr_id = svr01.id

    db.session.add_all([qtrade1, qdata1, qmdb1, qsdb1, qmarket1,
        qtrade2, qdata2, qmdb2, qsdb2, qmarket2]
    )
    db.session.commit()

@manager.command
def printurl():
    print url_for('main.index'), url_for('main.adddevice')
    print url_for('auth.login'), url_for('auth.register')
    print url_for('api.userlistapi'), url_for('api.userapi', login='test')

@manager.command
def usertest():
    #user = Operator.find(login='admin')
    for user in Operator.query.all():
        print user.name
        for role in user.roles:
            print "role name : ", role.name
            print "\tprivileges : "
            for pri in role.privileges:
                print "\t", pri.uri, pri.bit

@manager.command
def systemtest():
    #sys = TradeSystem.find(name=u'上期大厦1号')
    for sys in TradeSystem.query.all():
        print sys.name
        for svr in sys.servers:
            print svr.name, svr.manage_ip
            for proc in filter(lambda x: x.sys_id == sys.id, svr.processes):
                print proc.name, proc.id

if __name__ == '__main__':
    manager.run()
