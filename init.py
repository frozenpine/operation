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
from datetime import time
from SysManager.Common import AESCrypto

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os

import codecs
codecs.register(lambda name: name == 'cp65001' and codecs.lookup('utf-8') or None)

test_app = create_app('development')
manager = Manager(test_app)

def _encrypt(match):
    return match.group(1) + \
        AESCrypto.encrypt(
            match.group(2),
            current_app.config['SECRET_KEY']
        ) + \
        match.group(3)

def _decrypt(match):
    return match.group(1) + \
        AESCrypto.decrypt(
            match.group(2),
            current_app.config['SECRET_KEY']
        ) + \
        match.group(3)

@manager.command
def create_db():
    db.create_all()

@manager.command
def drop_db():
    db.drop_all()

@manager.command
def init_auth():
    f = open('auth.yml')
    auth = yaml.load(f)

    roles = {}
    for role in auth['Roles']:
        roles[role['name']] = OpRole(role['name'])
    db.session.add_all(roles.values())
    db.session.commit()

    users = {}
    user_role_relation = {}
    for user in auth['Users']:
        if user.has_key('roles'):
            for role in user['roles']:
                if roles.has_key(role):
                    if not user_role_relation.has_key(role):
                        user_role_relation[role] = []
                    user_role_relation[role].append(user['login'])
            user.pop('roles')
        users[user['login']] = Operator(**user)
    db.session.add_all([usr for usr in users.values()])
    db.session.commit()

    for role, usernames in user_role_relation.iteritems():
        for usr in usernames:
            roles[role].users.append(users[usr])
    db.session.add_all(roles.values())
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
    db.session.add_all(servers.values())
    db.session.commit()

    sys_types = {}
    for typ in inventory['SystemTypes']:
        sys_types[typ['name']] = SystemType(**typ)
    db.session.add_all(sys_types.values())
    db.session.commit()

    systems = {}
    for sys in inventory['Systems']:
        if sys.has_key('type'):
            if sys_types.has_key(sys['type']):
                typ = sys_types[sys.pop('type')]
            else:
                typ = SystemType.find(name=sys.pop('type'))
                sys_types[typ.name] = typ
            sys['type_id'] = typ.id
        systems[sys['name']] = TradeSystem(**sys)
    db.session.add_all(systems.values())
    db.session.commit()

    processes = {}
    for proc in inventory['Processes']:
        if proc.has_key('type'):
            typ, cat = proc['type'].split('.')
            proc['type'] = getattr(globals()[typ], cat).value
        proc['sys_id'] = systems[proc.pop('system')].id
        proc['svr_id'] = servers[proc.pop('server')].id
        processes[proc['name']] = TradeProcess(**proc)
    db.session.add_all(processes.values())
    db.session.commit()

    for parent, childs in inventory['Relations']['Parents'].iteritems():
        for child in childs:
            systems[parent].child_systems.append(systems[child])
    db.session.add_all(systems.values())
    db.session.commit()

    datasources = []
    for ds in inventory['DataSources']:
        ds['sys_id'] = systems[ds.pop('system')].id
        typ, cat = ds['src_type'].split('.')
        ds['src_type'] = getattr(globals()[typ], cat).value
        typ, cat = ds['src_model'].split('.')
        ds['src_model'] = getattr(globals()[typ], cat).value
        if test_app.config['GLOBAL_ENCRYPT']:
            ds['source']['uri'] = re.sub(
                '^(.+://[^:]+:)([^@]+)(@.+)$',
                _encrypt,
                ds['source']['uri']
            )
        datasources.append(DataSource(**ds))
    db.session.add_all(datasources)
    db.session.commit()

@manager.command
def modify_operation():
    operations = Operation.query.filter(Operation.sys_id == 3).all()
    for op in operations:
        params = op.detail['remote']['params']
        params['ip'] = '192.168.56.1'
        params['password'] = 'qdamqdam'
    db.session.add_all(operations)
    db.session.commit()

@manager.command
def init_operation():
    f = open('operations.yml')
    opers = yaml.load(f)

    groups = {}
    for grp in opers['OperationGroups']:
        if grp.has_key('system'):
            sys = TradeSystem.find(name=grp.pop('system'))
            grp['sys_id'] = sys.id
        groups[grp['name']] = OperationGroup(**grp)
    db.session.add_all(groups.values())
    db.session.commit()

    operations = []
    for op in opers['Operations']:
        typ, cat = op['type'].split('.')
        op['type'] = getattr(globals()[typ], cat).value
        if test_app.config['GLOBAL_ENCRYPT'] and ScriptType(op['type']).IsInteractivator():
            op['detail']['remote']['params']['password'] = \
                AESCrypto.encrypt(
                    op['detail']['remote']['params']['password'],
                    test_app.config['SECRET_KEY']
                )
        if op.has_key('op_group_id') and op.has_key('group'):
            op.pop('group')
        elif op.has_key('group'):
            op['op_group_id'] = groups[op.pop('group')].id
        if op.has_key('sys_id') and op.has_key('system'):
            op.pop('system')
        elif op.has_key('system'):
            sys = TradeSystem.find(name=op.pop('system'))
            if sys:
                op['sys_id'] = sys.id
        operations.append(Operation(**op))
    db.session.add_all(operations)
    db.session.commit()

@manager.command
def global_encrypt():
    pass

@manager.command
def modify_system(option_file):
    if os.path.exists(option_file):
        try:
            f = open(option_file)
            options = yaml.load(f)
        except Exception, err:
            print err.message
        else:
            if isinstance(options, dict):
                sys = TradeSystem.find(id=options['id'])
                if sys:
                    if options.has_key('ip'):
                        sys.ip = options['ip']
                    if options.has_key('username'):
                        sys.user = options['username']
                    if options.has_key('password'):
                        sys.password = options['password']
                    db.session.add(sys)
                    db.session.commit()
            elif isinstance(options, list):
                for config in options:
                    sys = TradeSystem.find(id=config['id'])
                    if sys:
                        if config.has_key('ip'):
                            sys.ip = config['ip']
                        if config.has_key('username'):
                            sys.user = config['username']
                        if config.has_key('password'):
                            sys.password = config['password']
                        db.session.add(sys)
                db.session.commit()
    else:
        print "file({}) not exists.".format(option_file)

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
    #sys = TradeSystem.find(id=1)
    #svr = Server.find(id=1)
    #proc = TradeProcess.find(id=1)
    #usr = Operator.find(id=1)
    #print sys.to_json()
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
    conf = ConfigFile(
        dir='/home/qdp/qtrade/bin',
        file='qtrade.ini',
        active=True
    )
    db.session.add(conf)
    db.session.commit()

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
