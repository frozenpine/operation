# -*- coding: UTF-8 -*-
import re

from flask import request
from flask_restful import Resource
from werkzeug.exceptions import BadRequest

from app import db
from app.models import Operation, OperationGroup
from restful.errors import DataNotJsonError, DataNotNullError, DataTypeError
from restful.protocol import RestProtocol


class OperationGroupListApi(Resource):
    def __init__(self):
        super(OperationGroupListApi, self).__init__()
        self.pattern = re.compile('^([0-1]?\d|2[0-3]):[0-5]?\d$')
        self.eng_to_chi = {
            'name': '操作组名',
            'sys_id': '系统',
            'trigger_time': '触发时间'
        }
        self.op_group_list = []
        self.disabled_list = []

    def get(self):
        op_groups = OperationGroup.query.all()
        return RestProtocol(op_groups)

    def post(self):
        try:
            data = request.get_json(force=True)
        except BadRequest:
            try:
                raise DataNotJsonError
            except DataNotJsonError:
                return RestProtocol(DataNotJsonError())
        else:
            try:
                not_null_list = ['name', 'sys_id', 'trigger_time']
                for param in not_null_list:
                    if not data['operation_group'].get(param):
                        raise DataNotNullError
                if not self.pattern.match(data['operation_group'].get('trigger_time')):
                    raise DataTypeError("请输入例如'HH:MM'格式的时间.")
            except DataNotNullError as err:
                return RestProtocol(err)
            except DataTypeError as err:
                return RestProtocol(err)
            og = OperationGroup(**data['operation_group'])
            ''' og.name = data['operation_group'].get('name')
            og.description = data['operation_group'].get('description')
            og.sys_id = data['operation_group'].get('sys_id')
            og.trigger_time = data['operation_group'].get('trigger_time') '''
            last = OperationGroup.query\
                .filter(OperationGroup.sys_id == data['operation_group']['sys_id'])\
                .order_by(OperationGroup.order.desc()).limit(1).first()
            if last:
                og.order = last.order + 10
            else:
                og.order = 10
            db.session.add(og)
            db.session.commit()
            operations = []
            op_list = data['operations']
            for i in xrange(len(op_list)):
                op = Operation()
                operations.append(op)
                try:
                    if not op_list[i].get('book_id'):
                        raise DataNotNullError
                except DataNotNullError:
                    return RestProtocol(DataNotNullError())
                operations[i].name = op_list[i].get('name')
                operations[i].description = op_list[i].get('description')
                operations[i].earliest = op_list[i].get('earliest')
                operations[i].latest = op_list[i].get('latest')
                operations[i].book_id = op_list[i].get('book_id')
                operations[i].order = (i + 1) * 10
                operations[i].op_group_id = og.id
            db.session.add_all(operations)
            db.session.commit()
            return RestProtocol(og)

    def put(self):
        try:
            data_list = request.get_json(force=True)
        except BadRequest:
            return RestProtocol(DataNotJsonError())
        else:
            for data in data_list:
                if len(data):
                    for og in data:
                        op_group = OperationGroup.find(id=og.get('id'))
                        if op_group:
                            if og.get('disabled'):
                                self.disabled_list.append(op_group)
                                op_group.disabled = True
                            else:
                                try:
                                    if og.get('trigger_time') and not self.pattern.match(og.get('trigger_time')):
                                        raise DataTypeError("Please enter the trigger time formatted as 'HH:MM'.")
                                except DataTypeError as e:
                                    return RestProtocol(e)
                                else:
                                    op_group.name = og.get('name', op_group.name)
                                    if og.get('trigger_time'):
                                        op_group.trigger_time = og.get('trigger_time') + ':00'
                                    self.op_group_list.append(op_group)
                                    op_group.order = (self.op_group_list.index(op_group) + 1) * 10
            db.session.add_all(self.op_group_list)
            db.session.add_all(self.disabled_list)
            db.session.commit()
            return RestProtocol(message='Success')


class OperationGroupApi(Resource):
    def __init__(self):
        super(OperationGroupApi, self).__init__()

    def get(self, **kwargs):
        op_group = OperationGroup.find(**kwargs)
        if op_group is not None:
            return RestProtocol(op_group)
        else:
            return {'message': 'Not found'}, 404

    def put(self, **kwargs):
        op_group = OperationGroup.find(**kwargs)
        if op_group is not None:
            try:
                data = request.get_json(force=True)
            except BadRequest:
                try:
                    raise DataNotJsonError
                except DataNotJsonError:
                    return RestProtocol(DataNotJsonError())
            else:
                # Modify operation group itself
                op_group.name = data['operation_group'].get('name', op_group.name)
                op_group.description = data['operation_group'].get('description', op_group.description)
                op_group.order = data['operation_group'].get('order', op_group.order)
                db.session.add(op_group)
                db.session.commit()

                # Modify operations of operation group
                operations = []
                used_id = []
                index = -1
                op_list = data['operations']
                op_exist = op_group.operations
                for i, v in enumerate(op_list):
                    if 'operation_id' in v and v['operation_id']:
                        for op_e in op_exist:
                            if op_e.id == v['operation_id']:
                                used_id.append(op_e.id)
                                op_e.name = op_list[i].get('operation_name', op_e.name)
                                op_e.description = op_list[i].get('description', op_e.description)
                                op_e.earliest = op_list[i].get('earliest', op_e.earliest)
                                op_e.latest = op_list[i].get('latest', op_e.latest)
                                op_e.need_authorization = op_list[i].get('need_authorization', op_e.need_authorization)
                                op_e.book_id = op_list[i].get('book_id', op_e.book_id)
                                op_e.order = (i + 1) * 10
                                op_e.op_group_id = op_group.id
                    else:
                        try:
                            if not op_list[i].get('book_id'):
                                raise DataNotNullError
                        except DataNotNullError:
                            return RestProtocol(DataNotNullError())
                        else:
                            op = Operation()
                            operations.append(op)
                            index += 1
                            operations[index].name = op_list[i].get('operation_name')
                            operations[index].description = op_list[i].get('description')
                            operations[index].earliest = op_list[i].get('earliest')
                            operations[index].latest = op_list[i].get('latest')
                            operations[index].need_authoriaztion = op_list[i].get('need_authorization')
                            operations[index].book_id = op_list[i].get('book_id')
                            operations[index].order = (i + 1) * 10
                            operations[index].op_group_id = op_group.id
                for op_e2 in op_exist:
                    if op_e2.id not in used_id:
                        op_e2.disabled = True
                db.session.add_all(operations)
                db.session.commit()
                return RestProtocol(op_group)
        else:
            return {'message': 'Not found'}, 404


'''class OperationGroupAdjustApi(Resource):
    def __init__(self):
        super(OperationGroupAdjustApi, self).__init__()
        self.pattern = re.compile('^[0-1]?\d|2[0-3]:[0-5]?\d$')
        self.op_group_list = []
        self.disabled_list = []

    def put(self):
        try:
            data_list = request.get_json(force=True)
        except BadRequest:
            return RestProtocol(DataNotJsonError())
        else:
            for data in data_list:
                if len(data):
                    for og in data:
                        op_group = OperationGroup.find(id=og.get('id'))
                        if op_group:
                            if og.get('disabled') is True:
                                self.disabled_list.append(op_group)
                                op_group.disabled = True
                            else:
                                try:
                                    if og.get('trigger_time') and not self.pattern.match(og.get('trigger_time')):
                                        raise DataTypeError("Please enter the trigger time formatted as 'HH:MM'.")
                                except DataTypeError as e:
                                    return RestProtocol(e)
                                else:
                                    op_group.name = og.get('name', op_group.name)
                                    if og.get('trigger_time'):
                                        op_group.trigger_time = og.get('trigger_time') + ':00'
                                    self.op_group_list.append(op_group)
                                    op_group.order = (self.op_group_list.index(op_group) + 1) * 10
            db.session.add_all(self.op_group_list)
            db.session.add_all(self.disabled_list)
            db.session.commit()
            return RestProtocol(message='Success')'''
