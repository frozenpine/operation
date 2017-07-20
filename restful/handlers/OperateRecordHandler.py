# -*- coding: UTF-8 -*-
from flask_restful import Resource
from app.models import OperateRecord, Operator, Operation
from flask import request
from werkzeug.exceptions import BadRequest
from restful.errors import DataNotJsonError
from restful.protocol import RestProtocol
import arrow


class OperateRecordListApi(Resource):
    def __init__(self):
        super(OperateRecordListApi, self).__init__()

    def post(self):
        try:
            data = request.get_json(force=True)
        except BadRequest:
            return RestProtocol(DataNotJsonError())
        else:
            operate_records = []
            if 'datetime' not in data and 'operator' not in data:
                operate_records = OperateRecord.query.all()
            elif data.get('operator') and 'datetime' not in data:
                operator = Operator.find(login=data.get('operator'))
                if operator:
                    operate_records = OperateRecord.query.filter(OperateRecord.operator_id == operator.id).all()
            elif data.get('datetime') and 'operator' not in data:
                operate_records = OperateRecord.query.filter(
                    OperateRecord.operated_at > arrow.get(data.get('datetime'))).all()
            elif data.get('datetime') and data.get('operator'):
                operator = Operator.find(login=data.get('operator'))
                if operator:
                    operate_records = OperateRecord.query.filter(
                        OperateRecord.operated_at > arrow.get(data.get('datetime'))).filter(
                        OperateRecord.operator_id == operator.id).all()

            record_list = []
            for op_record in operate_records:
                result_list = []
                for op_result in op_record.results:
                    result_list.append(op_result.to_json())
                operation = Operation.find(id=op_record.operation_id)
                if operation:
                    record_list.append(dict(op_record_id=op_record.id,
                                            operation=operation.name,
                                            operator=Operator.find(id=op_record.operator_id).login,
                                            operated_at=op_record.operated_at.to('local').format(
                                                'YYYY-MM-DD HH:mm:ss ZZ'),
                                            authorizer=None if not Operator.find(
                                                id=op_record.authorizor_id) else Operator.find(
                                                id=op_record.authorizor_id).login,
                                            authorized_at=None if not op_record.authorized_at else op_record.operated_at.to(
                                                'local').format('YYYY-MM-DD HH:mm:ss ZZ'),
                                            operation_results=result_list))
            return {'message': 'All data listed.',
                    'error_code': 0,
                    'data': {'count': len(record_list),
                             'records': record_list}}
            # return RestProtocol(record_list)
