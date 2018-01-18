# -*- coding: UTF-8 -*-

import yaml
from flask.testing import EnvironBuilder
from flask_script import Manager

from app import create_app
from app.models import *

test_app = create_app('development')
manager = Manager(test_app)


def _encrypt(match):
    return (match.group(1),
            AESCrypto.encrypt(match.group(2), test_app.config['SECRET_KEY']),
            match.group(3))


def _decrypt(match):
    return (match.group(1),
            AESCrypto.decrypt(match.group(2), test_app.config['SECRET_KEY']),
            match.group(3))


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
        roles[role['name']] = OpRole(name=role['name'])
    db.session.add_all(roles.values())
    db.session.commit()

    users = {}
    user_role_relation = {}
    for user in auth['Users']:
        if 'roles' in user:
            for role in user['roles']:
                if role in roles:
                    if role not in user_role_relation:
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

    privileges = {}
    role_privilege_relation = {}
    for pri in auth['Privileges']:
        typ, cat = pri['bit'].split('.')
        pri['bit'] = getattr(globals()[typ], cat).value
        if 'roles' in pri:
            for role in pri.pop('roles'):
                if role not in role_privilege_relation:
                    role_privilege_relation[role] = []
                role_privilege_relation[role].append(
                    "{uri}#{bit}".format(uri=pri['uri'], bit=pri['bit'])
                )
        privileges["{uri}#{bit}".format(uri=pri['uri'], bit=pri['bit'])] = OpPrivilege(**pri)
    db.session.add_all(privileges.values())
    db.session.commit()

    for role, pris in role_privilege_relation.iteritems():
        for pri in pris:
            roles[role].privileges.append(privileges[pri])
    db.session.add_all(roles.values())
    db.session.commit()


@manager.command
def init_inventory():
    f = open('inventory.yml')
    inventory = yaml.load(f)

    servers = {}
    for svr in inventory['Servers']:
        if 'platform' in svr:
            typ, cat = svr['platform'].split('.')
            svr['platform'] = getattr(globals()[typ], cat).value
        servers[svr['uuid']] = Server(**svr)
    db.session.add_all(servers.values())
    db.session.commit()

    sys_types = {}
    for typ in inventory['SystemTypes']:
        sys_types[typ['name']] = SystemType(**typ)
    db.session.add_all(sys_types.values())
    db.session.commit()

    systems = {}
    for sys in inventory['Systems']:
        if 'type' in sys:
            if sys['type'] in sys_types:
                typ = sys_types[sys.pop('type')]
            else:
                typ = SystemType.find(name=sys.pop('type'))
                sys_types[typ.name] = typ
            sys['type_id'] = typ.id
        systems[sys['uuid']] = TradeSystem(**sys)
    db.session.add_all(systems.values())
    db.session.commit()

    processes = {}
    for proc in inventory['Processes']:
        if 'type' in proc:
            typ, cat = proc['type'].split('.')
            proc['type'] = getattr(globals()[typ], cat).value
        proc['sys_id'] = systems[proc.pop('system')].id
        proc['svr_id'] = servers[proc.pop('server')].id
        processes[proc['uuid']] = TradeProcess(**proc)
    db.session.add_all(processes.values())
    db.session.commit()

    sockets = {}
    for sock in inventory['Sockets']:
        if 'direction' in sock:
            typ, cat = sock['direction'].split('.')
            sock['direction'] = getattr(globals()[typ], cat).value
        if 'process' in sock:
            sock['proc_id'] = processes[sock.pop('process')].id
        sockets[sock['uuid']] = Socket(**sock)
    db.session.add_all(sockets.values())
    db.session.commit()

    for parent, childs in inventory['Relations']['Parents'].iteritems():
        for child in childs:
            systems[parent].child_systems.append(systems[child])
    db.session.add_all(systems.values())
    db.session.commit()

    config_files = []
    for conf in inventory['ConfigFiles']:
        conf['proc_id'] = processes[conf.pop('process')].id
        typ, cat = conf.pop('config_type').split('.')
        conf['config_type'] = getattr(globals()[typ], cat).value
        config_files.append(ConfigFile(**conf))
    db.session.add_all(config_files)
    db.session.commit()


@manager.command
def init_operation():
    f = open('operations.yml')
    opers = yaml.load(f)

    catalogs = {}
    for cata in opers['OperationCatalog']:
        check = OperationCatalog.find(name=cata['name'])
        if check:
            catalogs[check.name] = check
        else:
            catalog = OperationCatalog(**cata)
            catalogs[catalog.name] = catalog
    db.session.add_all(catalogs.values())
    db.session.commit()

    operation_book = {}
    for bk in opers['OperationBook']:
        typ, cat = bk['type'].split('.')
        bk['type'] = getattr(globals()[typ], cat).value
        if test_app.config['GLOBAL_ENCRYPT'] and ScriptType(bk['type']).IsInteractivator():
            bk['detail']['remote']['params']['password'] = \
                AESCrypto.encrypt(
                    bk['detail']['remote']['params']['password'],
                    test_app.config['SECRET_KEY']
                )
        if 'sys_id' in bk and 'system' in bk:
            bk.pop('system')
        elif 'system' in bk:
            name = bk.pop('system')
            if re.match(r'[\da-zA-Z]{8}-(?:[\da-zA-Z]{4}-){3}[\da-zA-Z]{12}', name):
                sys = TradeSystem.find(uuid=name)
            else:
                sys = TradeSystem.find(name=name)
            bk['sys_id'] = sys.id
        if 'catalog' in bk:
            bk['catalog_id'] = catalogs[bk.pop('catalog')].id
        operation_book[bk['name']] = OperationBook(**bk)
    db.session.add_all(operation_book.values())
    db.session.commit()


@manager.command
def encrypt():
    pass


@manager.command
def decrypt():
    pass


@manager.command
def route_test():
    # print dir(test_app)
    '''
    urls = test_app.url_map.bind('localhost')
    a = urls.match('api/user/id/1')
    print a
    rsp = test_app.view_functions[a[0]](**a[1])
    print json.dumps(rsp.response)
    '''
    urls = test_app.url_map.bind('localhost')
    match = urls.match('api/user/id/1')
    with test_app.request_context(EnvironBuilder().get_environ()):
        rsp = test_app.view_functions[match[0]](**match[1])
        print json.dumps(rsp.response)


if __name__ == '__main__':
    manager.run()
