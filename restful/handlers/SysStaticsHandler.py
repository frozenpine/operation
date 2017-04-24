# -*- coding: UTF-8 -*-
from flask_restful import Resource
from app.models import TradeSystem, TradeProcess, Server
from SysManager import logging
from SysManager.configs import SSHConfig
from SysManager.executor import Executor
import pymysql
pymysql.install_as_MySQLdb()
from sqlalchemy import create_engine
from sqlalchemy.sql import text

class ServerStaticListApi(Resource):
    def __init__(self):
        self.server_list = {}

    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        rtn = []
        if len(self.server_list) > 0:
            self.server_list = {}
        if sys:
            self.find_servers(sys)
            for svr in self.server_list.values():
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

    def find_servers(self, sys):
        for svr in sys.servers:
            if self.server_list.has_key(svr.manage_ip.exploded):
                continue
            else:
                self.server_list[svr.manage_ip.exploded] = svr
        if len(sys.child_systems) > 0:
            for child_sys in sys.child_systems:
                self.find_servers(child_sys)

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
                executor = Executor.Create(conf)
                resultlist.append(executor.run(mod))
            rtn['id'] = svr.id
            rtn['server'] = svr.manage_ip.exploded
            rtn['uptime'] = resultlist[0].data
            rtn['cpu'] = resultlist[1].data
            rtn['disks'] = resultlist[2].data
            rtn['memory'] = resultlist[3].data['mem']
            rtn['swap'] = resultlist[3].data['swap']
        return rtn

class SystemStaticListApi(Resource):
    def __init__(self):
        self.system_list = []

    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        rtn = []
        if len(self.system_list) > 0:
            self.system_list = []
        if sys:
            self.find_systems(sys)
            for each_sys in self.system_list:
                rtn.append(
                    {
                        'name': each_sys.name,
                        'detail': [{
                            'id': proc.id,
                            'process': proc.name,
                            'proc_role': "{}".format(proc.type.name),
                            'status': {
                                'user': None,
                                'pid': None,
                                'cpu': None,
                                'mem': None,
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
                        } for proc in each_sys.processes]
                    }
                )
        return rtn

    def find_systems(self, sys):
        if len(sys.processes) > 0:
            self.system_list.append(sys)
        if len(sys.child_systems) > 0:
            for child_sys in sys.child_systems:
                self.find_systems(child_sys)

class ProcStaticApi(Resource):
    def get(self, **kwargs):
        proc = TradeProcess.find(**kwargs)
        rtn = {}
        if proc:
            rtn['id'] = proc.id
            rtn['process'] = proc.name
            rtn['proc_role'] = "{}".format(proc.type.name)
            rtn['server'] = proc.server.name + "({})"\
                .format(proc.server.manage_ip.exploded)
            conf = SSHConfig(
                proc.server.manage_ip.exploded,
                proc.server.admin_user,
                proc.server.admin_pwd
            )
            executor = Executor.Create(conf)
            mod = {
                'name': 'psaux',
                'args': {
                    'processes': [proc.exec_file],
                    'param': [proc.param]
                }
            }
            result = executor.run(mod).data
            if len(result) > 0:
                rtn['status'] = {
                    'user': result[0]['user'],
                    'pid': result[0]['pid'],
                    'cpu': result[0]['cpu%'],
                    'mem': result[0]['mem%'],
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
                    'cpu': None,
                    'mem': None,
                    'vsz': None,
                    'rss': None,
                    'tty': None,
                    'stat': 'stopped',
                    'start': None,
                    'time': None,
                    'command': None
                }
        return rtn

class LoginListApi(Resource):
    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        rtn = []
        if sys:
            '''
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
            '''
            db = create_engine(sys.db_uri)
            results = db.execute(text("""
                SELECT seat.seat_name, sync.brokerid, sync.exchangeid, sync.frontaddr, sync.seatid 
                FROM t_seat seat, t_sync_seat sync , t_capital_account 
                WHERE seat.seat_id = t_capital_account.seat_id 
                    AND sync.seatid=t_capital_account.account_id 
                    AND sync.isactive = TRUE""")).fetchall()
            for result in results:
                rtn.append({
                    'seat_name': result[0],
                    'broker_id': result[1],
                    'exchange_id': result[2],
                    'front_addr': result[3],
                    'seat_id': result[4]
                })
        return rtn

class LoginCheckApi(Resource):
    def get(self, **kwargs):
        pass
