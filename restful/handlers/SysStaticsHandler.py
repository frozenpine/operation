# -*- coding: UTF-8 -*-
from flask_restful import Resource, reqparse, request
from app.models import TradeSystem, TradeProcess, Server
from SysManager.configs import SSHConfig, Result
from SysManager.executor import Executor
'''
from SysManager.Parsers.mpstatParser import mpstatParser
from SysManager.Parsers.dfParser import dfParser
from SysManager.Parsers.freeParser import freeParser
from SysManager.Parsers.uptimeParser import uptimeParser
from SysManager.Parsers.psauxParser import psauxParser
'''

class ServerStaticListApi(Resource):
    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        rtn = []
        if sys:
            for svr in sys.servers:
                rtn.append({
                    'id': svr.id,
                    'server': svr.manage_ip.exploded,
                    'uptime': None,
                    'cpu': None,
                    'disks': None,
                    'memory': None,
                    'swap': None
                })
        return rtn

class ServerStaticApi(Resource):
    def get(self, **kwargs):
        svr = Server.find(**kwargs)
        rtn = {}
        if svr:
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
            rtn['id'] = svr.id
            rtn['server'] = svr.manage_ip.exploded
            '''
            rtn['uptime'] = uptimeParser(resultlist[0].lines).format2json()
            rtn['cpu'] = mpstatParser(resultlist[1].lines).format2json()
            rtn['disks'] = dfParser(resultlist[2].lines).format2json()
            rtn['memory'] = freeParser(resultlist[3].lines).format2json()['mem']
            rtn['swap'] = freeParser(resultlist[3].lines).format2json()['swap']
            '''
            rtn['uptime'] = resultlist[0].data
            rtn['cpu'] = resultlist[1].data
            rtn['disks'] = resultlist[2].data
            rtn['memory'] = resultlist[3].data['mem']
            rtn['swap'] = resultlist[3].data['swap']
        return rtn

class SystemStaticListApi(Resource):
    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        rtn = []
        if sys:
            rtn.append(
                {
                    'name': sys.name,
                    'detail': [{
                        'id': proc.id,
                        'process': proc.name,
                        'proc_role': proc.type.name,
                        'status': {
                            'user': None,
                            'pid': None,
                            'cpu%': None,
                            'mem%': None,
                            'vsz': None,
                            'rss': None,
                            'tty': None,
                            'stat': 'checking...',
                            'start': None,
                            'time': None,
                            'command': None
                        },
                        'server':
                            proc.server.name + "({})".format(proc.server.manage_ip.exploded)
                    } for proc in sys.processes]
                }
            )
            if len(sys.child_systems) > 0:
                for child in sys.child_systems:
                    rtn.append(
                        {
                            'name': child.name,
                            'detail': [{
                                'id': child_proc.id,
                                'process': child_proc.name,
                                'proc_role': child_proc.type.name,
                                'status': {
                                    'user': None,
                                    'pid': None,
                                    'cpu%': None,
                                    'mem%': None,
                                    'vsz': None,
                                    'rss': None,
                                    'tty': None,
                                    'stat': 'checking...',
                                    'start': None,
                                    'time': None,
                                    'command': None
                                },
                                'server':
                                    child_proc.server.name + "({})"\
                                        .format(child_proc.server.manage_ip.exploded)
                            } for child_proc in child.processes]
                        }
                    )
        return rtn

class ProcStaticApi(Resource):
    def get(self, **kwargs):
        proc = TradeProcess.find(**kwargs)
        rtn = {}
        if proc:
            rtn['id'] = proc.id
            rtn['process'] = proc.name
            rtn['proc_role'] = proc.type.name
            rtn['server'] = proc.server.name + "({})"\
                .format(proc.server.manage_ip.exploded)
            conf = SSHConfig(
                proc.server.manage_ip.exploded,
                proc.server.admin_user,
                proc.server.admin_pwd
            )
            executor = Executor(conf)
            mod = {
                'name': 'psaux',
                'args': {
                    'processes': [proc.name]
                }
            }
            #result = psauxParser(executor.run(mod).lines).format2json()
            result = executor.run(mod).data
            if len(result) > 0:
                rtn['status'] = {
                    'user': result[0]['user'],
                    'pid': result[0]['pid'],
                    'cpu%': result[0]['cpu%'],
                    'mem%': result[0]['mem%'],
                    'vsz': result[0]['vsz'],
                    'rss': result[0]['rss'],
                    'tty': result[0]['tty'],
                    'stat': result[0]['stat'],
                    'start': result[0]['start'],
                    'time': result[0]['time'],
                    'command': result[0]['command']
                }
            else:
                rtn['status'] = {
                    'user': None,
                    'pid': None,
                    'cpu%': None,
                    'mem%': None,
                    'vsz': None,
                    'rss': None,
                    'tty': None,
                    'stat': 'stopped',
                    'start': None,
                    'time': None,
                    'command': None
                }
        return rtn
