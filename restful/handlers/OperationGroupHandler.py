# -*- coding: UTF-8 -*-
import re
import json
import arrow

from flask import request
from flask_restful import Resource
from werkzeug.exceptions import BadRequest

from app import db
from app.models import Operation, OperationGroup
from restful.errors import (DataNotJsonError,
                            DataNotNullError,
                            DataTypeError,
                            ApiError)
from restful.protocol import RestProtocol


class OperationGroupListApi(Resource):
    def __init__(self):
        super(OperationGroupListApi, self).__init__()
        self.not_null_list = ['name', 'sys_id', 'trigger_time']
        self.pattern = re.compile('^([0-1]?\d|2[0-3]):[0-5]?\d$')
        self.op_group_list = []
        self.disabled_list = []

    def get(self):
        op_groups = OperationGroup.query.all()
        return RestProtocol(op_groups)

    def post(self):
        try:
            data = request.get_json(force=True)
            for param in self.not_null_list:
                if not data['operation_group'].get(param):
                    raise DataNotNullError
            if not self.pattern.match(data['operation_group'].get('trigger_time')):
                raise DataTypeError("Please enter the trigger time formatted as 'HH:MM'.")
        except BadRequest:
            return RestProtocol(DataNotJsonError())
        except ApiError as e:
            return RestProtocol(e)
        else:
            og = OperationGroup(**data['operation_group'])
            last = OperationGroup.query \
                .filter(OperationGroup.sys_id == data['operation_group']['sys_id']) \
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
                try:
                    if not op_list[i].get('book_id'):
                        raise DataNotNullError
                except DataNotNullError as e:
                    return RestProtocol(e)
                else:
                    op = Operation()
                    op.name = op_list[i].get('name')
                    op.description = op_list[i].get('description')
                    op.earliest = op_list[i].get('earliest')
                    op.latest = op_list[i].get('latest')
                    op.book_id = op_list[i].get('book_id')
                    op.order = (i + 1) * 10
                    op.op_group_id = og.id
                    operations.append(op)
            db.session.add_all(operations)
            db.session.commit()
            return RestProtocol(og)

    def put(self):
        try:
            data_list = request.get_json(force=True)
        except BadRequest:
            return RestProtocol(DataNotJsonError())
        else:
            for og in data_list:
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
                                op_group.trigger_time = og.get('trigger_time')
                            self.op_group_list.append(op_group)
                            op_group.order = (self.op_group_list.index(op_group) + 1) * 10
            db.session.add_all(self.op_group_list)
            db.session.add_all(self.disabled_list)
            db.session.commit()
            return RestProtocol(message='Success')


class OperationGroupApi(Resource):
    def __init__(self):
        super(OperationGroupApi, self).__init__()
        self.pattern = re.compile(ur'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)?$')

    def get(self, **kwargs):
        op_group = OperationGroup.find(**kwargs)
        if op_group:
            return RestProtocol(op_group)
        else:
            return RestProtocol(message='Operation group not found', error_code=-1), 404

    def put(self, **kwargs):
        op_group = OperationGroup.find(**kwargs)
        if op_group:
            try:
                data = request.get_json(force=True)
            except BadRequest:
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
                    try:
                        if op_list[i].get('earliest') and not self.pattern.match(op_list[i].get('earliest')):
                            raise DataTypeError("Earlist time format error.")
                        if op_list[i].get('latest') and not self.pattern.match(op_list[i].get('latest')):
                            raise DataTypeError("Latest time format error.")
                    except DataTypeError as e:
                        return RestProtocol(e)
                    else:
                        if 'operation_id' in v and v['operation_id']:
                            for op_e in op_exist:
                                if op_e.id == v['operation_id']:
                                    used_id.append(op_e.id)
                                    op_e.name = op_list[i].get('operation_name', op_e.name)
                                    op_e.description = op_list[i].get('description', op_e.description)
                                    if op_list[i].get('earliest') != '':
                                        op_e.earliest = arrow.get(op_list[i].get('earliest'))\
                                        .to('Asia/Shanghai').strftime('%H:%M:%S')
                                    else:
                                        op_e.earliest = None
                                    if op_list[i].get('latest') != '':
                                        op_e.latest = arrow.get(op_list[i].get('latest'))\
                                            .to('Asia/Shanghai').strftime('%H:%M:%S')
                                    else:
                                        op_e.latest = None
                                    op_e.need_authorization = op_list[i].get('need_authorization',
                                                                             op_e.need_authorization)
                                    op_e.book_id = op_list[i].get('book_id', op_e.book_id)
                                    op_e.order = (i + 1) * 10
                                    op_e.op_group_id = op_group.id
                        else:
                            try:
                                if not op_list[i].get('book_id'):
                                    raise DataNotNullError
                            except DataNotNullError as e:
                                return RestProtocol(e)
                            else:
                                op = Operation()
                                operations.append(op)
                                index += 1
                                operations[index].name = op_list[i].get('operation_name')
                                operations[index].description = op_list[i].get('description')
                                if op_list[i].get('earliest') != '':
                                    operations[index].earliest = arrow.get(op_list[i].get('earliest'))\
                                        .to('Asia/Shanghai').strftime('%H:%M:%S')
                                else:
                                    operations[index].earliest = None
                                if op_list[i].get('latest') != '':
                                    operations[index].latest = arrow.get(op_list[i].get('latest'))\
                                        .to('Asia/Shanghai').strftime('%H:%M:%S')
                                else:
                                    operations[index].earliest = None
                                operations[index].need_authorization = op_list[i].get('need_authorization')
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
            return RestProtocol(message='Operation group not found', error_code=-1), 404
