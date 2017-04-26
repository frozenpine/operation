# -*- coding: UTF-8 -*-
from flask import abort
from flask_restful import Resource
from app.models import TradeSystem, TradeProcess, Server
from SysManager import logging
from SysManager.configs import SSHConfig
from SysManager.executor import Executor
import pymysql
pymysql.install_as_MySQLdb()
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import re
import threading
import json

class ServerList(object):
    def __init__(self):
        self.server_list = {}
        self.rtn = {'details': []}

    def find_servers(self, sys):
        for svr in sys.servers:
            if self.server_list.has_key(svr.manage_ip.exploded):
                continue
            else:
                self.server_list[svr.manage_ip.exploded] = svr
        if len(sys.child_systems) > 0:
            for child_sys in sys.child_systems:
                self.find_servers(child_sys)

    def make_response(self):
        for svr in self.server_list.values():
            try:
                self.rtn['details'].append({
                    'id': svr.id,
                    'server': svr.manage_ip.exploded,
                    'uptime': svr.status.get('uptime'),
                    'cpu': svr.status.get('cpu'),
                    'disks': svr.status.get('disks'),
                    'memory': svr.status.get('memory'),
                    'swap': svr.status.get('swap')
                })
            except Exception:
                self.rtn['details'].append({
                    'id': svr.id,
                    'server': svr.manage_ip.exploded,
                    'uptime': None,
                    'cpu': None,
                    'disks': None,
                    'memory': None,
                    'swap': None
                })

class ServerStaticListApi(Resource, ServerList):
    def __init__(self):
        super(ServerStaticListApi, self).__init__()

    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        if len(self.server_list) > 0:
            self.server_list = {}
        if sys:
            self.rtn['sys_id'] = sys.id
            self.find_servers(sys)
            self.make_response()
        return self.rtn

class ServerStaticApi(Resource, ServerList):
    def __init__(self):
        super(ServerStaticApi, self).__init__()
        self.checker = []

    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        if len(self.server_list) > 0:
            self.server_list = {}
        if sys:
            self.rtn['sys_id'] = sys.id
            self.find_servers(sys)
            for svr in self.server_list.values():
                self.checker.append(threading.Thread(target=self.check_svr, args=(svr,)))
            for tr in self.checker:
                tr.start()
                tr.join()
            self.make_response()
        return self.rtn

    def check_svr(self, svr):
        result = {}
        conf = SSHConfig(svr.manage_ip.exploded, svr.admin_user, svr.admin_pwd)
        modlist = [
            {'name': 'uptime'},
            {'name': 'mpstat'},
            {'name': 'df'},
            {'name': 'free'}
        ]
        resultlist = []
        executor = Executor.Create(conf)
        for mod in modlist:
            resultlist.append(executor.run(mod))
        result['id'] = svr.id
        result['server'] = svr.manage_ip.exploded
        result['uptime'] = resultlist[0].data
        result['cpu'] = resultlist[1].data
        result['disks'] = resultlist[2].data
        result['memory'] = resultlist[3].data['mem']
        result['swap'] = resultlist[3].data['swap']
        svr.status = result
        executor.client.close()

class SystemList(object):
    def __init__(self):
        self.system_list = []
        self.rtn = []

    def find_systems(self, sys):
        if len(sys.processes) > 0:
            self.system_list.append(sys)
        if len(sys.child_systems) > 0:
            for child_sys in sys.child_systems:
                self.find_systems(child_sys)

    def make_response(self):
        for each_sys in self.system_list:
            try:
                self.rtn.append(
                    {
                        'name': each_sys.name,
                        'detail': [{
                            'id': proc.id,
                            'process': proc.name,
                            'proc_role': "{}".format(proc.type.name),
                            'status': {
                                'user': proc.status.get('user'),
                                'pid': proc.status.get('pid'),
                                'cpu': proc.status.get('cpu%'),
                                'mem': proc.status.get('mem%'),
                                'vsz': proc.status.get('vsz'),
                                'rss': proc.status.get('rss'),
                                'tty': proc.status.get('tty'),
                                'stat': proc.status.get('stat'),
                                'start': proc.status.get('start'),
                                'time': proc.status.get('time'),
                                'command': proc.status.get('command')
                            },
                            'server':
                                proc.server.name + "({})".format(proc.server.manage_ip.exploded)
                        } for proc in each_sys.processes]
                    }
                )
            except Exception:
                self.rtn.append(
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

class SystemStaticListApi(Resource, SystemList):
    def __init__(self):
        super(SystemStaticListApi, self).__init__()

    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        if len(self.system_list) > 0:
            self.system_list = []
        if sys:
            self.find_systems(sys)
            self.make_response()
        return self.rtn

class ProcStaticApi(Resource, SystemList):
    def __init__(self):
        super(ProcStaticApi, self).__init__()
        self.proc_list = {}
        self.checker = []

    def find_processes(self):
        for child_sys in self.system_list:
            for proc in child_sys.processes:
                if not self.proc_list.has_key(proc.server):
                    self.proc_list[proc.server] = []
                self.proc_list[proc.server].append(proc)

    def check_proc(self, svr, processes):
        conf = SSHConfig(
            svr.manage_ip.exploded,
            svr.admin_user,
            svr.admin_pwd
        )
        executor = Executor.Create(conf)
        for proc in processes:
            mod = {
                'name': 'psaux',
                'args': {
                    'processes': [proc.exec_file],
                    'param': [proc.param]
                }
            }
            result = executor.run(mod).data
            if len(result) > 0:
                proc.status = result[0]
            else:
                proc.status = {
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
        executor.client.close()

    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        if sys:
            self.find_systems(sys)
            self.find_processes()
            for svr in self.proc_list.keys():
                self.checker.append(
                    threading.Thread(
                        target=self.check_proc,
                        args=(svr, self.proc_list[svr])
                    )
                )
            for tr in self.checker:
                tr.start()
                tr.join()
            self.make_response()
        return self.rtn

class LoginListApi(Resource):
    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        rtn = []
        if sys:
            try:
                sys_db = create_engine(sys.db_uri)
            except Exception:
                abort(404)
            else:
                results = sys_db.execute(text("""
                    SELECT seat.seat_name, sync.tradingday, sync.frontaddr, sync.seatid 
                    FROM t_seat seat, t_sync_seat sync , t_capital_account 
                    WHERE seat.seat_id = t_capital_account.seat_id 
                        AND sync.seatid=t_capital_account.account_id 
                        AND sync.isactive = TRUE""")).fetchall()
                for result in results:
                    rtn.append({
                        'seat_name': result[0],
                        'trading_day': result[1],
                        'front_addr': result[2],
                        'seat_id': result[3],
                        'seat_status': u'未连接'
                    })
                sys_db.dispose()
        return rtn

class LoginCheckApi(Resource):
    def __init__(self):
        self.syslog_list = {}
        self.rtn = []
        self.check = []
        self.mutex = threading.Lock()

    def find_syslog(self, sys):
        for log in sys.syslog_files:
            if self.syslog_list.has_key(log.server):
                self.syslog_list[log.server].append(log)
            else:
                self.syslog_list[log.server] = []
                self.syslog_list[log.server].append(log)
        if len(sys.child_systems) > 0:
            for child_sys in sys.child_systems:
                self.find_syslog(child_sys)

    def check_log(self, svr, logs):
        if svr.platform:                        #不同平台，使用不同的执行器，当前测试均为SSH
            conf = SSHConfig(
                svr.manage_ip.exploded,
                svr.admin_user,
                svr.admin_pwd
            )
        else:
            conf = SSHConfig(
                svr.manage_ip.exploded,
                svr.admin_user,
                svr.admin_pwd
            )
        executor = Executor.Create(conf)
        for log in logs:
            mod = {
                'name': 'quantdoLogin',
                'quantdoLogin': log.file_path
            }
            result = executor.run(mod)
            self.mutex.acquire()
            for key in result.data.keys():
                if u'连接成功' in result.data[key][-1]['message'].decode('utf-8'):
                    self.rtn.append({
                        'seat_id': key,
                        'seat_status': u'连接成功'
                    })
                elif u'登录成功' in result.data[key][-1]['message'].decode('utf-8'):
                    self.rtn.append({
                        'seat_id': key,
                        'seat_status': u'登录成功'
                    })
                elif u'登录失败' in result.data[key][-1]['message'].decode('utf-8'):
                    self.rtn.append({
                        'seat_id': key,
                        'seat_status': u'登录失败'
                    })
                elif u'断开' in result.data[key][-1]['message'].decode('utf-8'):
                    self.rtn.append({
                        'seat_id': key,
                        'seat_status': u'连接断开'
                    })
                else:
                    self.rtn.append({
                        'seat_id': key,
                        'seat_status': u'未连接'
                    })
            self.mutex.release()
        executor.client.close()

    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        if sys:
            self.find_syslog(sys)
            for (k, v) in self.syslog_list.items():
                self.check.append(threading.Thread(target=self.check_log, args=(k, v)))
            for tr in self.check:
                tr.start()
                tr.join()
        return self.rtn

class UserSessionListApi(Resource):
    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        rtn = []
        if sys:
            try:
                sys_db = create_engine(sys.db_uri)
            except Exception:
                abort(404)
            else:
                results = sys_db.execute(text("""
                    SELECT brokerid, userid, usertype, sessionid, frontid,
                        logintime, ipaddress, macaddress
                    FROM t_oper_usersession
                """)).fetchall()
                for result in results:
                    rtn.append({
                        'broker_id': result[0],
                        'user_id': result[1],
                        'user_type': result[2],
                        'session_id': result[3],
                        'front_id': result[4],
                        'login_time': result[5],
                        'ip_address': result[6],
                        'mac_address': result[7],
                    })
                sys_db.dispose()
        return rtn
