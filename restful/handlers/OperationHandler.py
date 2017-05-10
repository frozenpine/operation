# -*- coding: UTF-8 -*-
from app import db
from flask_login import current_user
from flask_restful import Resource, reqparse, request
from app.models import (
    OperationGroup, Operation, ScriptType,
    OperateRecord, OperateResult
)
import arrow
import json
from SysManager.configs import Result, SSHConfig
from SysManager.executor import Executor

class OperationListApi(Resource):
    def __init__(self):
        super(OperationListApi, self).__init__()
        self.rtn = {}

    def find_op_results(self, op):
        record = OperateRecord.query\
            .filter(OperateRecord.operation_id==op.id)\
                .order_by(OperateRecord.operated_at.desc()).first()
        if record:
            return record.operated_at.timestamp > \
                arrow.get(arrow.now().strftime('%Y-%m-%d')).timestamp, record
        else:
            return False, None

    def get(self, **kwargs):
        op_group = OperationGroup.find(**kwargs)
        if op_group:
            self.rtn['name'] = op_group.name
            self.rtn['details'] = []
            for op in op_group.operations:
                skip, record = self.find_op_results(op)
                if skip:
                    self.rtn['details'].append({
                        'id': op.id,
                        'op_name': op.name,
                        'op_desc': op.description,
                        'err_code': -1,
                        'enabled': False,
                        're_enter': True,
                        'checker': {
                            'isTrue': op.type == ScriptType.Checker,
                            'checked': False
                        },
                        'skip': skip,
                        'his_results': {
                            'operated_at': record.operated_at.humanize(),
                            'operator': record.operator.name,
                            'lines': json.loads(record.results[-1].detail)
                        }
                    })
                else:
                    self.rtn['details'].append({
                        'id': op.id,
                        'op_name': op.name,
                        'op_desc': op.description,
                        'err_code': -1,
                        'enabled': False,
                        're_enter': True,
                        'checker': {
                            'isTrue': op.type == ScriptType.Checker,
                            'checked': False
                        },
                        'skip': skip
                    })
            if len(self.rtn['details']) > 0:
                self.rtn['details'][0]['enabled'] = True
            return self.rtn
        else:
            return {
                'message': 'operation group not found'
            }, 404

class OperationApi(Resource):
    def get(self, **kwargs):
        op = Operation.find(**kwargs)
        rtn = {}
        if op:
            op_rec = OperateRecord()
            op_rec.operation_id = op.id
            op_rec.operator_id = current_user.id
            op_rec.operated_at = arrow.utcnow().to("Asia/Shanghai")
            db.session.add(op_rec)
            db.session.commit()
            rtn['id'] = op.id
            rtn['op_name'] = op.name
            rtn['op_desc'] = op.description
            rtn['checker'] = {
                'isTrue': op.type == ScriptType.Checker,
                'checked': False
            }
            conf = SSHConfig(
                op.system.manage_ip.exploded,
                op.system.login_user,
                op.system.login_pwd
            )
            executor = Executor.Create(conf)
            result = executor.run(op.detail)
            executor.client.close()
            if result.return_code == 0:
                rtn['err_code'] = 0
            else:
                rtn['err_code'] = 10
            #rtn['enabled'] = rtn['err_code'] == 0
            rtn['output_lines'] = result.lines
            res = OperateResult()
            res.op_rec_id = op_rec.id
            res.succeed = result.return_code == 0
            res.error_code = result.error_code.name
            res.detail = json.dumps(result.lines)
            db.session.add(res)
            db.session.commit()
            return rtn
        else:
            return {
                'message': 'operation not found'
            }, 404
