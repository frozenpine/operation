# -*- coding: UTF-8 -*-
from flask_restful import Resource, reqparse, request
from app.models import TradeSystem
from SysManager import Result
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
        res = Result
        result = {}
        mod = {
                'name': 'df'
            }
        stdin, stdout, stderr = executor.run(mod)
        result['return_code'] = stdout.channel.recv_exit_status()
        res.return_code = stdout.channel.recv_exit_status()
        result['destination'] = conf.ssh_host
        res.destination = conf.ssh_host
        result['module'] = mod
        res.module = mod
        if result.get('return_code') == 0:
            result['lines'] = stdout.readlines()
            res.lines = stdout.readlines()
        else:
            result['lines'] = stderr.readlines()
            res.lines = stderr.readlines()
        #return result
        return json.dumps(res)
