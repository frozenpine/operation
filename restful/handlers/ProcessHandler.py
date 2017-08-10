# -*- coding: UTF-8 -*-
from flask import request
from flask_restful import Resource
from werkzeug.exceptions import BadRequest

from app import db
from app.models import HaType
from app.models import TradeProcess
from restful.errors import (DataNotJsonError,
                            DataNotNullError,
                            DataEnumValueError,
                            ApiError)
from restful.protocol import RestProtocol


class ProcessApi(Resource):
    def __init__(self):
        super(ProcessApi, self).__init__()

    def get(self, **kwargs):
        process = TradeProcess.find(**kwargs)
        if process:
            return RestProtocol(process)
        else:
            return {'message': 'Process not found'}, 404

    '''def put(self, **kwargs):
        process = TradeProcess.find(**kwargs)
        if process:
            try:
                data = request.get_json(force=True)
                if data.get('type'):
                    HaType[data.get('type')]
            except BadRequest:
                return RestProtocol(DataNotJsonError())
            except KeyError:
                return RestProtocol(DataEnumValueError())
            else:
                process.name = data.get('name', process.name)
                if data.get('type'):
                    process.type = HaType[data.get('type')]
                process.sys_id = data.get('sys_id', process.sys_id)
                process.svr_id = data.get('svr_id', process.svr_id)
                process.param = data.get('param', process.param)
                process.description = data.get('description', process.description)
                process.base_dir = data.get('base_dir', process.base_dir)
                process.exec_file = data.get('exec_file', process.exec_file)
                db.session.add(process)
                db.session.commit()
                return RestProtocol(process)
        else:
            return {'message': 'Process not found'}, 404'''


class ProcessListApi(Resource):
    def __init__(self):
        super(ProcessListApi, self).__init__()
        self.not_null_list = ['name', 'sys_id', 'svr_id', 'type', 'exec_file']

    def get(self):
        process = TradeProcess.query.filter(TradeProcess.disabled == False).all()
        return RestProtocol(process)

    '''def post(self):
        try:
            data = request.get_json(force=True)
            for param in self.not_null_list:
                if not data.get(param):
                    raise DataNotNullError('Please input {}'.format(param))
            if data.get('type'):
                HaType[data.get('type')]
        except BadRequest:
            return RestProtocol(DataNotJsonError())
        except ApiError as e:
            return RestProtocol(e)
        except KeyError:
            return RestProtocol(DataEnumValueError())
        else:
            process = TradeProcess(name=data.get('name'),
                                   sys_id=data.get('sys_id'),
                                   svr_id=data.get('svr_id'),
                                   type=HaType[data.get('type')])
            process.description = data.get('description')
            process.base_dir = data.get('base_dir')
            process.exec_file = data.get('exec_file')
            process.param = data.get('param')
            db.session.add(process)
            db.session.commit()
            return RestProtocol(process)

    def put(self):
        try:
            data_list = request.get_json(force=True)
        except BadRequest:
            return RestProtocol(DataNotJsonError())
        else:
            process_list = []
            for data in data_list:
                if data.get('type'):
                    try:
                        HaType[data.get('type')]
                    except KeyError:
                        return RestProtocol(DataEnumValueError())
                process = TradeProcess.find(id=data.get('id'))
                if process:
                    process.name = data.get('name', process.name)
                    if data.get('type'):
                        process.type = HaType[data.get('type')]
                    process.sys_id = data.get('sys_id', process.sys_id)
                    process.svr_id = data.get('svr_id', process.svr_id)
                    process.param = data.get('description', process.param)
                    process.description = data.get('description', process.description)
                    process.base_dir = data.get('base_dir', process.base_dir)
                    process.exec_file = data.get('exec_file', process.exec_file)
                    process.disabled = data.get('disabled', process.disabled)
                    process_list.append(process)
            db.session.add_all(process_list)
            db.session.commit()
            return RestProtocol(process_list)'''

    def post(self):
        try:
            data_list = request.get_json(force=True)
        except BadRequest:
            return RestProtocol(DataNotJsonError())
        else:
            process_list = []
            for data in data_list:
                if data.get('type'):
                    try:
                        HaType[data.get('type')]
                    except KeyError:
                        return RestProtocol(DataEnumValueError())
                if data.get('id'):
                    process = TradeProcess.find(id=data.get('id'))
                    if process:
                        process.name = data.get('name', process.name)
                        if data.get('type'):
                            process.type = HaType[data.get('type')]
                        process.sys_id = data.get('sys_id', process.sys_id)
                        process.svr_id = data.get('svr_id', process.svr_id)
                        process.param = data.get('param', process.param)
                        process.description = data.get('description', process.description)
                        process.base_dir = data.get('base_dir', process.base_dir)
                        process.exec_file = data.get('exec_file', process.exec_file)
                        process.disabled = data.get('disabled', process.disabled)
                        process_list.append(process)
                else:
                    try:
                        for param in self.not_null_list:
                            if not data.get(param):
                                raise DataNotNullError('Please input {}'.format(param))
                    except ApiError as e:
                        return RestProtocol(e)
                    else:
                        process = TradeProcess(name=data.get('name'),
                                               sys_id=data.get('sys_id'),
                                               svr_id=data.get('svr_id'),
                                               type=HaType[data.get('type')])
                        process.description = data.get('description')
                        process.base_dir = data.get('base_dir')
                        process.exec_file = data.get('exec_file')
                        process.param = data.get('param')
                        process_list.append(process)
            db.session.add_all(process_list)
            db.session.commit()
            return RestProtocol(process_list)
