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
        self.op_books = []
        self.system_list = []

    def find_systems(self, sys):
        self.system_list.append(sys.id)
        for child_sys in sys.child_systems:
            self.find_systems(child_sys)

    def find_operation_books(self):
        self.op_books = OperationBook.query.filter(
            OperationBook.sys_id.in_(self.system_list),
            OperationBook.disabled == False
        ).all()

    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        if sys:
            self.find_systems(sys)
            self.find_operation_books()
            return RestProtocol(self.op_books)

    def post(self):
        try:
            data = request.get_json(force=True)
        except BadRequest:
            return RestProtocol(DataNotJsonError())
        else:
            try:
                if not data.get('name') or not data.get('sys_id') or \
                    not data.get('mod') or not data.get('catalog_id') or not data.get('type'):
                    raise DataNotNullError
                try:
                    ScriptType[data.get('type')]
                except KeyError:
                    raise DataEnumValueError('操作节点类型定义不正确.')
            except ApiError as e:
                return RestProtocol(e)
            else:
                mod_data = data.pop('mod')
                method = data.pop('remote_name')
                ob_type = ScriptType[data.pop('type')]
                if len(mod_data) > 1:
                    data['detail'] = [{
                        'remote': {
                            'name': method
                        },
                        'mod': {
                            'name': 'shell',
                            'shell': x.pop('shell'),
                            'args': x.has_key('chdir') and {
                                'chdir': x.pop('chdir')
                            } or {}
                        }
                    } for x in mod_data]
                else:
                    data['detail'] = {
                        'remote': {
                            'name': method
                        },
                        'mod': {
                            'name': 'shell',
                            'shell': mod_data[0].pop('shell'),
                            'args': mod_data[0].has_key('chdir') and {
                                'chdir': mod_data[0].pop('chdir')
                            } or {}
                        }
                    }
                ob = OperationBook(**data)
                ob.type = ob_type
                self.find_systems(TradeSystem.find(id=data.get('sys_id')))
                op_list = OperationBook.query.filter(
                    OperationBook.catalog_id == ob.catalog_id,
                    OperationBook.sys_id.in_(self.system_list)
                ).order_by(OperationBook.order).all()
                if len(op_list):
                    ob.order = (op_list[-1].order + 10) / 10 * 10
                else:
                    ob.order = 10
                db.session.add(ob)
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
                ob = OperationBook.query.filter_by(id=v.get('id')).first()
                if ob:
                    if v.get('catalog_id') == cata_id:
                        ob_list.append(ob)
                        ob.order = (ob_list.index(ob) + 1) * 10
                    else:
                        ob_temp.append(ob)
                        obs = OperationBook.query.filter(
                            OperationBook.catalog_id == v.get('catalog_id'),
                            OperationBook.disabled == False
                        ).order_by(OperationBook.order).all()
                        if len(obs):
                            ob.order = (obs[-1].order + 10) / 10 * 10
                        else:
                            ob.order = 10
                    ob.name = v.get('op_name', ob.name)
                    ob.description = v.get('op_desc', ob.description)
                    ob.type = ScriptType[v.get('type')] or ob.type
                    ob.catalog_id = v.get('catalog_id', ob.catalog_id)
                    ob.sys_id = v.get('sys_id', ob.sys_id)
                    ob.disabled = v.get('disabled')
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
            return RestProtocol(DataNotJsonError())
        else:
            try:
                if not data.get('shell'):
                    raise DataNotNullError
            except DataNotNullError as e:
                return RestProtocol(e)
            else:
                system = TradeSystem.find(**kwargs)
                if system:
                    file_name, chdir = data.get('shell').split(' ')[0], data.get('chdir')
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect('{}'.format(system.ip), 22, '{}'.format(system.user), '{}'.format(system.password))
                    if chdir:
                        stdin, stdout, stderr = ssh.exec_command(
                            'cd {0};if [ -f {1} ];then echo 0;else echo 1;fi'.format(chdir, file_name))
                    else:
                        stdin, stdout, stderr = ssh.exec_command(
                            'if [ -f {0} ];then echo 0;else echo 1;fi'.format(file_name))
                    res = stdout.readlines()[0].strip('\n')
                    ssh.close()
                    if res == '0':
                        return RestProtocol(error_code=0,
                                            message='Script check success.')
                    else:
                        return RestProtocol(error_code=1,
                                            message='Script check fails.')


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
