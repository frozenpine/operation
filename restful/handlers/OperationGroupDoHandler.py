# -*- coding: UTF-8 -*-
from flask_restful import Resource
from flask import request
from app import db
from app.models import TradeSystem, OperationGroup, Operation
from werkzeug.exceptions import BadRequest
from ..output import Output
from ..errors import DataNotJsonError, DataNotNullError


class OperationGroupAddApi(Resource):
    def __init__(self):
        super(OperationGroupAddApi, self).__init__()

    def post(self):
        try:
            data = request.get_json(force=True)
        except BadRequest:
            try:
                raise DataNotJsonError
            except DataNotJsonError:
                return Output(DataNotJsonError())
        else:
            # Add operation group
            og = OperationGroup()
            try:
                if not data['operation_group'].get('name') or not data['operation_group'].get('sys_id'):
                    raise DataNotNullError
            except DataNotNullError:
                return Output(DataNotNullError())
            og.name = data['operation_group'].get('name')
            og.description = data['operation_group'].get('description')
            og.sys_id = data['operation_group'].get('sys_id')
            ogs = OperationGroup.query.all()
            if len(ogs):
                ogs_order = [op_group.order for op_group in ogs]
                og.order = max(ogs_order) + 10
            else:
                og.order = 10
            db.session.add(og)
            db.session.commit()

            # Add operations
            operations = []
            # order_base = 0
            op_list = data['operations']
            for i in xrange(len(op_list)):
                op = Operation()
                operations.append(op)
                try:
                    if not op_list[i].get('book_id'):
                        raise DataNotNullError
                except DataNotNullError:
                    return Output(DataNotNullError())
                operations[i].name = op_list[i].get('name')
                operations[i].description = op_list[i].get('description')
                operations[i].earliest = op_list[i].get('earliest')
                operations[i].latest = op_list[i].get('latest')
                operations[i].book_id = op_list[i].get('book_id')
                operations[i].order = (i + 1) * 10
                operations[i].op_group_id = og.id
            db.session.add_all(operations)
            db.session.commit()
            return Output(og)


class OperationGroupAdjustApi(Resource):
    def __init__(self):
        super(OperationGroupAdjustApi, self).__init__()

    
    def put(self):
        try:
            data = request.get_json(force=True)
        except BadRequest:
            try:
                raise DataNotJsonError
            except DataNotJsonError:
                return Output(DataNotJsonError())
        else:
            # Modify operation group itself
            op_group = OperationGroup.find(id=data['operation_group'].get('id'))
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
                        return Output(DataNotNullError())
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
            return Output(op_group)
