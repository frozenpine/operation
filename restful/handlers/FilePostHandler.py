# -*- coding: UTF-8 -*-
from flask_restful import Resource
from flask import request, render_template, make_response, redirect, url_for
from app.models import Socket, TradeProcess, Server, SystemType, TradeSystem, PlatformType, HaType, DataSource, \
    DataSourceType, DataSourceModel, OpRole, Operator, OperationBook, ScriptType, Operation, OperationGroup, \
    SocketDirection, OperationCatalog, OpPrivilege, MethodType
from app import db
from ..output import Output
from ..errors import DataUniqueError, LoaderNotFoundError, DataNotNullError
import os
import time
import yaml


class FilePostApi(Resource):
    def __init__(self):
        super(FilePostApi, self).__init__()

    def post(self):
        file_upload = request.files['file']
        if file_upload:
            if not os.path.exists('uploaded_files'):
                os.mkdir('uploaded_files')
            new_filename = '{0}_{1}'.format(time.strftime("%Y-%m-%d-%H-%M-%S"), file_upload.filename)
            file_upload.save(os.path.join('uploaded_files', new_filename))
            with open('uploaded_files/{0}'.format(new_filename)) as f:
                import_loader = 'from loaders.{0}loader import {0}loader as loader'.format(
                    new_filename.rsplit('.', 1)[1])
                try:
                    exec import_loader
                except ImportError:
                    data_temp = yaml.load(f)
                    if isinstance(data_temp, dict):
                        exec 'from loaders.ymlloader import ymlloader as loader'
                        f = yaml.dump(data_temp)
                    else:
                        return Output(LoaderNotFoundError())
                data_from_file = loader(f)

                # Add server
                if 'Servers' in data_from_file:
                    servers = []
                    for i, svr in enumerate(data_from_file['Servers']):
                        server = Server()
                        servers.append(server)
                        try:
                            if Server.query.filter_by(name=svr.get('name')).first() is not None:
                                raise DataUniqueError
                            elif not svr.get('name') or not svr.get('user') or not svr.get('password') or not svr.get(
                                    'ip'):
                                raise DataNotNullError
                        except DataUniqueError:
                            return Output(DataUniqueError())
                        except DataNotNullError:
                            return Output(DataNotNullError())
                        else:
                            servers[i].name = svr['name']
                            if 'description' in svr:
                                servers[i].description = svr.get('description')
                            servers[i].ip = svr.get('ip')
                            servers[i].user = svr.get('user')
                            servers[i].password = svr.get('password')
                            if 'platform' in svr:
                                servers[i].platform = PlatformType[svr.get('platform').split('.')[1]].value
                    db.session.add_all(servers)
                    db.session.commit()

                # Add system type
                if 'SystemTypes' in data_from_file:
                    sys_types = []
                    for i, sys_type in enumerate(data_from_file['SystemTypes']):
                        system_type = SystemType()
                        sys_types.append(system_type)
                        try:
                            if SystemType.query.filter_by(name=sys_type.get('name')).first() is not None:
                                raise DataUniqueError
                            elif not sys_type.get('name'):
                                raise DataNotNullError
                        except DataUniqueError:
                            return Output(DataUniqueError())
                        except DataNotNullError:
                            return Output(DataNotNullError())
                        else:
                            sys_types[i].name = sys_type.get('name')
                            if 'description' in sys_type:
                                sys_types[i].description = sys_type.get('description')
                    db.session.add_all(sys_types)
                    db.session.commit()

                # Add system
                if 'Systems' in data_from_file:
                    systems = []
                    for i, sys in enumerate(data_from_file['Systems']):
                        system = TradeSystem()
                        systems.append(system)
                        try:
                            if TradeSystem.query.filter_by(name=sys.get('name')).first() is not None:
                                raise DataUniqueError
                            elif not sys.get('name') or not sys.get('user') or not sys.get('password') or not sys.get(
                                    'ip'):
                                raise DataNotNullError
                        except DataUniqueError:
                            return Output(DataUniqueError())
                        except DataNotNullError:
                            return Output(DataNotNullError())
                        else:
                            systems[i].name = sys['name']
                            systems[i].ip = sys['ip'].decode('utf-8')
                            systems[i].user = sys['user']
                            systems[i].password = sys['password']
                            if 'description' in sys:
                                systems[i].description = sys['description']
                            if 'version' in sys:
                                systems[i].version = sys['version']
                            if 'type' in sys:
                                sys_type = SystemType.find(name=sys['type'])
                                if sys_type:
                                    systems[i].type_id = sys_type.id
                    db.session.add_all(systems)
                    db.session.commit()

                # Add process
                if 'Processes' in data_from_file:
                    processes = []
                    for i, pro in enumerate(data_from_file['Processes']):
                        try:
                            if TradeProcess.query.filter_by(name=pro.get('name')).first() is not None:
                                raise DataUniqueError
                            elif not pro.get('name') or not pro.get('system') or not pro.get('server') or not pro.get(
                                    'exec_file'):
                                raise DataNotNullError
                        except DataUniqueError:
                            return Output(DataUniqueError())
                        except DataNotNullError:
                            return Output(DataNotNullError())
                        else:
                            system = TradeSystem.find(name=pro['system'])
                            server = Server.find(name=pro['server'])
                            if system and server:
                                process = TradeProcess(name=pro['name'],
                                                       sys_id=system.id,
                                                       svr_id=server.id)
                                processes.append(process)
                            processes[i].exec_file = pro['exec_file']
                            if 'param' in pro:
                                processes[i].param = pro['param']
                            if 'type' in pro:
                                processes[i].type = HaType[pro['type'].split('.')[1]].value
                    db.session.add_all(processes)
                    db.session.commit()

                # Add socket
                if 'Sockets' in data_from_file:
                    sockets = []
                    for i, sock in enumerate(data_from_file['Sockets']):
                        socket = Socket()
                        sockets.append(socket)
                        try:
                            if Socket.query.filter_by(name=sock.get('name')).first() is not None:
                                raise DataUniqueError
                            elif not sock.get('name') or not sock.get('uri'):
                                raise DataNotNullError
                        except DataUniqueError:
                            return Output(DataUniqueError())
                        except DataNotNullError:
                            return Output(DataNotNullError())
                        else:
                            sockets[i].name = sock.get('name')
                            sockets[i].description = sock.get('description')
                            sockets[i].uri = sock.get('uri').decode('utf-8')
                            process = TradeProcess.find(name=sock.get('process'))
                            if process:
                                sockets[i].proc_id = process.id
                            '''sockets[i].port = sock.get('uri').rsplit(':', 1)[1]
                            sockets[i].address = sock.get('uri').split(':')[1].strip('//')
                            if sock['uri'].split(':', 1)[0] == 'udp':
                                sockets[i].type = 2
                            if 'direction' in sock:
                                sockets[i].direction = SocketDirection[sock.get('direction').split('.')[1]].value'''
                    db.session.add_all(sockets)
                    db.session.commit()

                # Add relation
                if 'Relations' in data_from_file:
                    for parent, children in data_from_file['Relations']['Parents'].iteritems():
                        parent_sys = TradeSystem.find(name=parent)
                        for child in children:
                            child_sys = TradeSystem.find(name=child)
                            child_sys.parent_sys_id = parent_sys.id
                            db.session.add(child_sys)
                        db.session.commit()

                # Add data source
                if 'DataSources' in data_from_file:
                    data_sources = []
                    for i, ds in enumerate(data_from_file['DataSources']):
                        data_source = DataSource()
                        data_sources.append(data_source)
                        try:
                            if DataSource.query.filter_by(name=ds.get('name')).first() is not None:
                                raise DataUniqueError
                            elif not ds.get('name') or not ds.get('src_type') or not ds.get('src_model') or not ds.get(
                                    'source'):
                                raise DataNotNullError
                        except DataUniqueError:
                            return Output(DataUniqueError())
                        except DataNotNullError:
                            return Output(DataNotNullError())
                        else:
                            data_sources[i].name = ds.get('name')
                            if 'description' in ds:
                                data_sources[i].description = ds.get('description')
                            system = TradeSystem.find(name=ds.get('system'))
                            if system:
                                data_sources[i].sys_id = system.id
                            data_sources[i].src_type = DataSourceType[ds.get('src_type').split('.')[1]].value
                            data_sources[i].src_model = DataSourceModel[ds.get('src_model').split('.')[1]].value
                            data_sources[i].source = ds.get('source')
                    db.session.add_all(data_sources)
                    db.session.commit()

                # Add role
                if 'Roles' in data_from_file:
                    roles = []
                    for i, role in enumerate(data_from_file['Roles']):
                        try:
                            if OpRole.query.filter_by(name=role['name']).first() is not None:
                                raise DataUniqueError
                            elif not role.get('name'):
                                raise DataNotNullError
                        except DataUniqueError:
                            return Output(DataUniqueError())
                        except DataNotNullError:
                            return Output(DataNotNullError())
                        else:
                            r = OpRole(name=role.get('name'))
                            roles.append(r)
                    db.session.add_all(roles)
                    db.session.commit()

                # Add user
                if 'Users' in data_from_file:
                    users = []
                    for i, user in enumerate(data_from_file['Users']):
                        try:
                            if Operator.query.filter_by(login=user.get('login')).first() is not None:
                                raise DataUniqueError
                            elif not user.get('login') or not user.get('password'):
                                raise DataNotNullError
                        except DataUniqueError:
                            return Output(DataUniqueError())
                        except DataNotNullError:
                            return Output(DataNotNullError())
                        else:
                            u = Operator(login=user.get('login'),
                                         password=user.get('password'))
                            users.append(u)
                            if 'name' in user:
                                users[i].name = user.get('name')
                            else:
                                users[i].name = user.get('login')
                            for role in user.get('roles'):
                                op_role = OpRole.find(name=role)
                                op_role.users.append(u)
                                u.roles.append(op_role)
                    db.session.add_all(users)
                    db.session.commit()

                # Add privilege
                if 'Privileges' in data_from_file:
                    privileges = []
                    for i, pri in enumerate(data_from_file['Privileges']):
                        try:
                            if not pri.get('uri') or not pri.get('bit'):
                                raise DataNotNullError
                        except DataNotNullError:
                            return Output(DataNotNullError())
                        else:
                            p = OpPrivilege()
                            privileges.append(p)
                            privileges[i].uri = pri.get('uri')
                            privileges[i].bit = MethodType[pri.get('bit').split('.')[1]].value
                            for role in pri.get('roles'):
                                op_role = OpRole.find(name=role)
                                op_role.privileges.append(p)
                                p.roles.append(op_role)
                    db.session.add_all(privileges)
                    db.session.commit()

                # Add operation catalogs
                if 'OperationCatalog' in data_from_file:
                    op_catalogs = []
                    for i, oc in enumerate(data_from_file['OperationCatalog']):
                        operation_catalog = OperationCatalog()
                        op_catalogs.append(operation_catalog)
                        try:
                            if OperationCatalog.query.filter_by(name=oc.get('name')).first() is not None:
                                raise DataUniqueError
                            elif not oc.get('name'):
                                raise DataNotNullError
                        except DataUniqueError:
                            return Output(DataUniqueError())
                        except DataNotNullError:
                            return Output(DataNotNullError())
                        else:
                            op_catalogs[i].name = oc.get('name')
                            op_catalogs[i].order = oc.get('order')
                            if 'description' in oc:
                                op_catalogs[i].description = oc.get('description')
                    db.session.add_all(op_catalogs)
                    db.session.commit()

                # Add operation book
                if 'OperationBook' in data_from_file:
                    op_books = []
                    for i, ob in enumerate(data_from_file['OperationBook']):
                        try:
                            if OperationBook.find(name=ob.get('name')) is not None:
                                raise DataUniqueError
                            elif not ob.get('name') or not ob.get('detail'):
                                raise DataNotNullError
                        except DataUniqueError:
                            return Output(DataUniqueError())
                        except DataNotNullError:
                            return Output(DataNotNullError())
                        else:
                            operation_book = OperationBook()
                            op_books.append(operation_book)
                            op_books[i].name = ob.get('name')
                            if 'description' in ob:
                                op_books[i].description = ob.get('description')
                            op_books[i].type = ScriptType[ob.get('type').split('.')[1]].value
                            op_books[i].detail = ob.get('detail')
                            op_books[i].order = ob.get('order')
                            op_books[i].is_emergency = ob.get('is_emergency')
                            if 'sys_id' in ob:
                                op_books[i].sys_id = ob.get('sys_id')
                            elif 'system' in ob:
                                system = TradeSystem.find(uuid=ob.get('system')) or TradeSystem.find(
                                    name=ob.get('system'))
                                if system:
                                    op_books[i].sys_id = system.id
                            if 'catalog_id' in ob:
                                op_books[i].catalog_id = ob.get('catalog_id')
                            elif 'catalog' in ob:
                                catalog = OperationCatalog.find(name=ob.get('catalog'))
                                if catalog:
                                    op_books[i].catalog_id = catalog.id
                    db.session.add_all(op_books)
                    db.session.commit()

                # Add operation group
                if 'OperationGroups' in data_from_file:
                    op_groups = []
                    for i, og in enumerate(data_from_file['OperationGroups']):
                        operation_group = OperationGroup()
                        op_groups.append(operation_group)
                        try:
                            if not og.get('name') or not og.get('order') or \
                                    (not og.get('sys_id') and not og.get('system')):
                                raise DataNotNullError
                        except DataNotNullError:
                            return Output(DataNotNullError())
                        else:
                            op_groups[i].name = og.get('name')
                            if 'description' in og:
                                op_groups[i].description = og.get('description')
                            op_groups[i].order = og.get('order')
                            if 'sys_id' in og:
                                op_groups[i].sys_id = og.get('sys_id')
                            elif 'system' in og:
                                system = TradeSystem.find(name=og.get('system'))
                                if system:
                                    op_groups[i].sys_id = system.id
                    db.session.add_all(op_groups)
                    db.session.commit()

                # Add operation
                if 'Operations' in data_from_file:
                    operations = []
                    for i, op in enumerate(data_from_file['Operations']):
                        operation = Operation()
                        operations.append(operation)
                        try:
                            if not op.get('op_book') or not op.get('order') or \
                                    (not op.get('op_group_id') and not op.get('group')):
                                raise DataNotNullError
                        except DataNotNullError:
                            return Output(DataNotNullError())
                        else:
                            operations[i].name = op.get('name')
                            if 'description' in op:
                                operations[i].description = op.get('description')
                            if 'earliest' in op:
                                operations[i].earliest = op.get('earliest')
                            if 'latest' in op:
                                operations[i].latest = op.get('latest')
                            op_book = OperationBook.find(name=op.get('op_book'))
                            if op_book:
                                operations[i].book_id = op_book.id
                            operations[i].order = op.get('order')
                            if 'op_group_id' in op:
                                operations[i].op_group_id = op.get('op_group_id')
                            elif 'group' in op:
                                operation_group = OperationGroup.find(name=op.get('group'))
                                if operation_group:
                                    operations[i].op_group_id = operation_group.id
                            if 'need_authorization' in op:
                                operations[i].need_authorization = op.get('need_authorization')
                    db.session.add_all(operations)
                    db.session.commit()

            return {'message': 'File post successfully.',
                    'error_code': 0,
                    'data': None}
