# -*- coding: UTF-8 -*-
import paramiko
from flask import request
from flask_restful import Resource
from werkzeug.exceptions import BadRequest

from app import db
from app.models import OperationBook, PlatformType, ScriptType, TradeSystem
from restful.errors import (ApiError, DataEnumValueError, DataNotJsonError,
                            DataNotNullError, DataUniqueError,
                            PlatFormNotFoundError)
from restful.protocol import RestProtocol


class OperationBookListApi(Resource):
    def __init__(self):
        super(OperationBookListApi, self).__init__()

    def get(self):
        operation_books = OperationBook.query.all()
        return RestProtocol(operation_books)

    def post(self):
        try:
            data = request.get_json(force=True)
        except BadRequest:
            return RestProtocol(DataNotJsonError())
        else:
            try:
                if not data.get('name') or not data.get('sys_id') or not data.get('mod') or not data.get(
                        'catalog_id') or not data.get('type'):
                    raise DataNotNullError
                elif OperationBook.query.filter_by(name=data.get('name')).first() is not None:
                    raise DataUniqueError
                elif data.get('type') is not None:
                    try:
                        ScriptType[data.get('type')]
                    except KeyError:
                        raise DataEnumValueError
                ob = OperationBook()
                ob.name = data.get('name')
                ob.description = data.get('description')
                ob.type = ScriptType[data.get('type')]
                ob.catalog_id = data.get('catalog_id')
                ob.sys_id = data.get('sys_id')
                if data.get('is_emergency') == 'false':
                    ob.is_emergency = 0
                elif data.get('is_emergency') == 'true':
                    ob.is_emergency = 1

                system = TradeSystem.find(id=data.get('sys_id'))
                if system:
                    if system.servers.first().platform is not None:
                        if system.servers.first().platform == PlatformType.Linux or data.get(
                                        'remote_name' == 'SSHConfig'):
                            params_dict = dict(ip=system.ip, user=system.user, password=system.password)
                            remote_dict = dict(name='SSHConfig', params=params_dict)
                            mod_list = []
                            mod_data = data.get('mod')
                            for j in xrange(len(mod_data)):
                                if mod_data[j].get('chdir'):
                                    mod_list.append(dict(name='shell',
                                                         shell=mod_data[j].get('shell'),
                                                         args=dict(chdir=mod_data[j].get('chdir'))))
                                else:
                                    mod_list.append(dict(name='shell', shell=mod_data[j].get('shell')))
                            detail_dict = dict(remote=remote_dict, mod=mod_list)
                    else:
                        return RestProtocol(PlatFormNotFoundError())

                    ob.detail = detail_dict
                else:
                    return {'message': 'System not found.'}, 404

            except ApiError as e:
                return RestProtocol(e)
            else:
                db.session.add(ob)

                # Add order of operation book
                op_list = OperationBook.query.filter(OperationBook.catalog_id == ob.catalog_id).order_by(
                    OperationBook.order).all()
                if len(op_list):
                    ob.order = (op_list[-1].order + 10) / 10 * 10
                else:
                    ob.order = 10

                db.session.commit()
                return RestProtocol(ob)

    def put(self):
        try:
            data = request.get_json(force=True)
        except BadRequest:
            return RestProtocol(DataNotJsonError())
        else:
            cata_id = data.get('catalog_id')
            ob_data = data.get('data')
            ob_list = []
            ob_temp = []
            for i, v in enumerate(ob_data):
                # ob = OperationBook.find(id=v.get('id'))
                ob = OperationBook.query.filter_by(id=v.get('id')).first()
                if ob:
                    if v.get('catalog_id') == cata_id:
                        ob_list.append(ob)
                        ob.order = (ob_list.index(ob) + 1) * 10
                    else:
                        ob_temp.append(ob)
                        obs = OperationBook.query.filter(OperationBook.catalog_id == v.get('catalog_id')).filter(OperationBook.disabled==False).order_by(
                            OperationBook.order).all()
                        if len(obs):
                            ob.order = (obs[-1].order + 10) / 10 * 10
                        else:
                            ob.order = 10
                    ob.name = v.get('op_name', ob.name)
                    ob.description = v.get('op_desc', ob.description)
                    ob.type = ScriptType[v.get('type')] or ob.type
                    ob.catalog_id = v.get('catalog_id', ob.catalog_id)
                    ob.sys_id = v.get('sys_id', ob.sys_id)
                    if v.get('is_emergency') == 'false':
                        ob.is_emergency = 0
                    elif v.get('is_emergency') == 'true':
                        ob.is_emergency = 1
                    if v.get('disabled') == 'false':
                        ob.disabled = 0
                    elif v.get('disabled') == 'true':
                        ob.disabled = 1
            db.session.add_all(ob_list)
            db.session.add_all(ob_temp)
            db.session.commit()
            return RestProtocol(ob_list)


class OperationBookCheckApi(Resource):
    def __init__(self):
        super(OperationBookCheckApi, self).__init__()

    def post(self, **kwargs):
        try:
            data = request.get_json(force=True)
        except BadRequest:
            try:
                raise DataNotJsonError
            except DataNotJsonError:
                return RestProtocol(DataNotJsonError())
        else:
            try:
                if not data.get('shell'):
                    raise DataNotNullError
            except DataNotNullError:
                return RestProtocol(DataNotNullError())
            else:
                system=TradeSystem.find(**kwargs)
                if system:
                    file_name, chdir = data.get('shell'), data.get('chdir')
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect('{}'.format(system.ip), 22, '{}'.format(system.user), '{}'.format(system.password))
                    if chdir:
                        stdin, stdout, stderr = ssh.exec_command(
                            'cd {0};if [ -f {1} ];then echo 0;else echo 1;fi'.format(chdir, file_name))
                    else:
                        stdin, stdout, stderr = ssh.exec_command(
                            'if [ -f {0} ];then echo 0;else echo 1;fi'.format(file_name))
                    ans = stdout.readlines()[0]
                    ssh.close()
                    return {'error_code': '0',
                            'data': ans,
                            'message': 'Script Check successfully'}


class OperationBookApi(Resource):
    def __init__(self):
        super(OperationBookApi, self).__init__()

    def get(self, **kwargs):
        op_book = OperationBook.find(**kwargs)
        if op_book is not None:
            return RestProtocol(op_book)
        else:
            return {'message': 'Not found'}, 404

    def put(self, **kwargs):
        op_book = OperationBook.find(**kwargs)
        if op_book is not None:
            try:
                data = request.get_json(force=True)
            except BadRequest:
                try:
                    raise DataNotJsonError
                except DataNotJsonError:
                    return RestProtocol(DataNotJsonError())
            else:
                try:
                    if op_book.name != data.get('name') and OperationBook.query.filter_by(
                            name=data.get('name')).first() is not None:
                        raise DataUniqueError
                    elif data.get('type') is not None:
                        try:
                            ScriptType[data.get('type')]
                        except KeyError:
                            raise DataEnumValueError
                except DataUniqueError:
                    return RestProtocol(DataUniqueError())
                except DataEnumValueError:
                    return RestProtocol(DataEnumValueError())
                else:
                    op_book.name = data.get('name', op_book.name)
                    op_book.description = data.get('description', op_book.description)
                    op_book.type = ScriptType[data.get('type')] or op_book.type
                    op_book.catalog_id = data.get('catalog_id', op_book.catalog_id)
                    op_book.sys_id = data.get('sys_id', op_book.sys_id)
                    if data.get('is_emergency') == 'false':
                        op_book.is_emergency = 0
                    elif data.get('is_emergency') == 'true':
                        op_book.is_emergency = 1
                    db.session.add(op_book)
                    db.session.commit()
                    return RestProtocol(op_book)
        else:
            return {'message': 'Not found'}, 404
