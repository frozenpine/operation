# -*- coding: UTF-8 -*-
from flask_restful import Resource, reqparse, request
from app.models import TradeSystem
from SysManager.configs import SSHConfig, Result
from SysManager.executor import Executor


class LoginLogApi(Resource):
    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        rtn = []
        if sys:
            conf = SSHConfig(sys.manage_ip.exploded, sys.login_user, sys.login_pwd)
            executor = Executor(conf)
            mod = {
                'name': 'quantdoLogin',
                'quantdoLogin': '/root/right.txt'
            }
            result = executor.run(mod)
            for key in result.data.keys():
                rtn.append({
                    'seatid': key,
                    'detail': result.data[key][-1]
                })
        return rtn
