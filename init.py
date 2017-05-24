# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from flask import url_for
from flask_script import Manager
from app import create_app, db
from app.models import *
import arrow
import json, re
from flask.testing import EnvironBuilder
import yaml

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

    qdp_type = SystemType(name='QDP')
    qdiam_type = SystemType(name='QDIAM')
    ctp_type = SystemType(name='CTP')
    db.session.add_all([qdp_type, qdiam_type, ctp_type])
    db.session.commit()

@manager.command
def drop_db():
    db.drop_all()

@manager.command
def init_auth():
    f = open('auth.yml')
    auth = yaml.load(f)

    users = {}
    for user in auth['Users']:
        users[user['login']] = Operator(**user)
    db.session.add_all([usr for usr in users.values()])
    db.session.commit()

@manager.command
def init_inventory():
    f = open('inventory.yml')
    inventory = yaml.load(f)

    servers = {}
    for svr in inventory['Servers']:
        if svr.has_key('platform'):
            typ, cat = svr['platform'].split('.')
            svr['platform'] = getattr(globals()[typ], cat).value
        servers[svr['name']] = Server(**svr)
    db.session.add_all([svr for svr in servers.values()])
    db.session.commit()

    systems = {}
    sys_types = {}
    for sys in inventory['Systems']:
        if sys.has_key('type'):
            if sys_types.has_key(sys['type']):
                typ = sys_types[sys.pop('type')]
            else:
                typ = SystemType.find(name=sys.pop('type'))
                sys_types[typ.name] = typ
            sys['type_id'] = typ.id
        systems[sys['name']] = TradeSystem(**sys)
    db.session.add_all([sys for sys in systems.values()])
    db.session.commit()

    processes = {}
    for proc in inventory['Processes']:
        if proc.has_key('type'):
            typ, cat = proc['type'].split('.')
            proc['type'] = getattr(globals()[typ], cat).value
        proc['sys_id'] = systems[proc.pop('system')].id
        proc['svr_id'] = servers[proc.pop('server')].id
        processes[proc['name']] = TradeProcess(**proc)
    db.session.add_all([proc for proc in processes.values()])
    db.session.commit()

    for parent, childs in inventory['Relations']['Parents'].iteritems():
        for child in childs:
            systems[parent].child_systems.append(systems[child])
    db.session.add_all([sys for sys in systems.values()])
    db.session.commit()

    datasources = []
    for ds in inventory['DataSources']:
        ds['sys_id'] = systems[ds.pop('system')].id
        typ, cat = ds['src_type'].split('.')
        ds['src_type'] = getattr(globals()[typ], cat).value
        typ, cat = ds['src_model'].split('.')
        ds['src_model'] = getattr(globals()[typ], cat).value
        datasources.append(DataSource(**ds))
    db.session.add_all(datasources)
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
    proc = TradeProcess.find(id=12)
    print proc.type.value
    '''
    svr = Server.query.filter()

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
