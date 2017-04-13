# -*- coding: UTF-8 -*-
from flask_restful import Resource, reqparse, request
from app.models import OperationGroup, Operation
from SysManager.configs import Result
from SysManager.configs import SSHConfig
from SysManager.executor import Executor

class OperationListApi(Resource):
    def get(self, **kwargs):
        op_group = OperationGroup.find(**kwargs)
        rtn = {}
        if op_group:
            rtn['name'] = op_group.name
            rtn['details'] = [
                {
                    'id': op.id,
                    'op_name': op.name,
                    'op_desc': op.description,
                    'succeed': None,
                    'enabled': False
                } for op in op_group.operations]
            if len(rtn['details']) > 0:
                rtn['details'][0]['enabled'] = True
        return rtn

class OperationApi(Resource):
    def get(self, **kwargs):
        op = Operation.find(**kwargs)
        rtn = {}
        if op:
            rtn['id'] = op.id
            rtn['op_name'] = op.name
            rtn['op_desc'] = op.description
            conf = SSHConfig(
                op.group.system.manage_ip.exploded,
                op.group.system.login_user,
                op.group.system.login_pwd
            )
            executor = Executor(conf)
            result = executor.run(op.detail)
            if result.return_code == 0:
                rtn['succeed'] = True
            else:
                rtn['succeed'] = False
            rtn['enabled'] = not rtn['succeed']
            rtn['output_lines'] = result.lines
        return rtn
