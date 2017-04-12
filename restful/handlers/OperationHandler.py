# -*- coding: UTF-8 -*-
from flask_restful import Resource, reqparse, request
from app.models import TradeSystem
from SysManager.configs import Result
from SysManager.configs import SSHConfig
from SysManager.executor import Executor
import json

class OperationListApi(Resource):
    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        return {
            'target': sys.to_json(),
            'operations': [x for x in range(1, 10)],
            'method': request.method
        }

class OperationApi(Resource):
    def get(self, **kwargs):
        conf = SSHConfig('192.168.101.152', 'qdp', 'qdp')
        executor = Executor(conf)
        result = {}
        mod = {
                'name': 'df'
            }
        res = executor.run(mod)
        result['return_code'] = res.return_code
        result['destination'] = res.destination
        result['module'] = res.module
        result['lines'] = res.lines
        return result
        #return res
