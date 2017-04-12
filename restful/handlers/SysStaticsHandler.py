# -*- coding: UTF-8 -*-
from flask_restful import Resource, reqparse, request
from app.models import TradeSystem
from SysManager.configs import SSHConfig, Result
from SysManager.executor import Executor
from SysManager.Parsers.mpstatParser import mpstatParser
from SysManager.Parsers.dfParser import dfParser
from SysManager.Parsers.freeParser import freeParser
from SysManager.Parsers.uptimeParser import uptimeParser

class ServerStaticsApi(Resource):
    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        rtn = []
        if sys:
            for svr in sys.servers:
                conf = SSHConfig(svr.manage_ip.exploded, svr.admin_user, svr.admin_pwd)
                modlist = [
                    {'name': 'uptime'},
                    {'name': 'mpstat'},
                    {'name': 'df'},
                    {'name': 'free'}
                ]
                resultlist = []
                for mod in modlist:
                    executor = Executor(conf)
                    resultlist.append(executor.run(mod))
                rtn.append({
                    'server': conf.ssh_host,
                    'uptime': uptimeParser(resultlist[0].lines).format2json(),
                    'cpu': mpstatParser(resultlist[1].lines).format2json(),
                    'disks': dfParser(resultlist[2].lines).format2json(),
                    'memory': freeParser(resultlist[3].lines).format2json()['mem'],
                    'swap': freeParser(resultlist[3].lines).format2json()['swap']
                })
        return rtn


class SystemStaticsApi(Resource):
    def get(self, **kwargs):
        return [
            {
                'systemName': 'trade01',
                'server': 'testtest',
                'process': 'qtrade',
                'proc_role': 'master',
                'status': 'running'
            }
        ]
