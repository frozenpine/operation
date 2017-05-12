# -*- coding: UTF-8 -*-
from flask import abort
from flask_restful import Resource
from app.models import (
    TradeSystem, TradeProcess, Server,
    DataSource, DatasourceModel, DataSourceType
)
#from SysManager import logging
import logging
from SysManager.configs import SSHConfig
from SysManager.executor import Executor
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import re
import threading
import json
#from app import db_list

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
        else:
            return {
                'message': 'system not found'
            }, 404

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
        else:
            return {
                'message': 'system not found'
            }, 404

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
        else:
            return {
                'message': 'system not found'
            }, 404

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
        else:
            return {
                'message': 'system not found'
            }, 404

class LoginListApi(Resource):
    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        rtn = []
        if sys:
            src = DataSource.query.filter(
                DataSource.src_type == DataSourceType.SQL,
                DataSource.src_model == DatasourceModel.DbSeat,
                DataSource.sys_id == sys.id
            ).first()
            if src:
                #sys_db = db_list.get(src.source['uri'])
                #if not sys_db:
                try:
                    sys_db = create_engine(src.source['uri']).connect()
                except Exception:
                    return {
                        'message': 'faild to connect to database.'
                    }, 404
                    #else:
                    #    db_list[src.source['uri']] = sys_db
                results = sys_db.execute(text(src.source['sql'])).fetchall()
                for result in results:
                    tmp = {}
                    for idx in xrange(len(src.source['formatter'])):
                        try:
                            tmp[src.source['formatter'][idx]['key']] = unicode(result[idx])
                        except IndexError:
                            tmp[src.source['formatter'][idx]['key']] = \
                                src.source['formatter'][idx]['default']
                    rtn.append(tmp)
                sys_db.close()
                return rtn
            else:
                return {
                    'message': 'no data source configured for system {}'.format(sys.name)
                }, 404
        else:
            return {
                'message': 'system not found'
            }, 404

class LoginCheckApi(Resource):
    def __init__(self):
        self.syslog_list = {}
        self.rtn = []
        self.check = []
        self.mutex = threading.Lock()

    def find_syslog(self, sys):
        log_srcs = DataSource.query.filter(
            DataSource.src_type == DataSourceType.FILE,
            DataSource.src_model == DatasourceModel.LogSeat,
            DataSource.sys_id == sys.id
        ).all()
        for src in log_srcs:
            uri = src.source['uri'].split('#')
            svr = uri[0].rstrip('/')
            log = uri[1]
            if not self.syslog_list.has_key(svr):
                self.syslog_list[svr] = []
            self.syslog_list[svr].append(log)

    def check_log(self, svr, logs):
        reg = re.compile(
            r'^(?P<method>[^:]+)://(?P<user>[^:]+):(?P<pass>[^@]+)@(?P<ip>[^:]+):(?P<port>\d+)$'
        )
        pars = reg.match(svr).groupdict()
        if pars['method'] == 'ssh':
            conf = SSHConfig(
                ip=pars['ip'],
                user=pars['user'],
                password=pars['pass'],
                port=int(pars['port'])
            )
        else:
            conf = SSHConfig(
                ip=pars['ip'],
                user=pars['user'],
                password=pars['pass'],
                port=int(pars['port'])
            )
        executor = Executor.Create(conf)
        for log in logs:
            mod = {
                'name': 'quantdoLogin',
                'quantdoLogin': log
            }
            result = executor.run(mod)
            for (k, v) in result.data.iteritems():
                pattern = re.compile(
                    r'.+TradeDate=\[(?P<trade_date>[^]]+)\]\s+TradeTime=\[(?P<trade_time>[^]]+)\]'
                )
                data = {
                    'seat_id': k,
                    'seat_status': u"",
                    'conn_count': 0,
                    'login_success': 0,
                    'login_fail': 0,
                    'disconn_count': 0
                }
                for each in v:
                    if each.get('message').find('连接成功') >= 0:
                        data['seat_status'] = u'连接成功'
                        data['conn_count'] += 1
                    elif each.get('message').find('登录成功') >= 0:
                        try:
                            pars_message = pattern.match(each.get('message'))\
                                .groupdict()
                        except AttributeError:
                            pass
                        else:
                            data['trading_day'] = pars_message.get('trade_date')
                            data['login_time'] = pars_message.get('trade_time')
                        data['seat_status'] = u'登录成功'
                        data['login_success'] += 1
                    elif each.get('message').find('登录失败') >= 0:
                        data['seat_status'] = u'登录失败'
                        data['login_fail'] += 1
                    elif each.get('message').find('断开') >= 0:
                        data['seat_status'] = u'连接断开'
                        data['disconn_count'] += 1
                    else:
                        data['seat_status'] = u'未连接'
                self.mutex.acquire()
                self.rtn.append(data)
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
        else:
            return {
                'message': 'system not found'
            }, 404

class UserSessionListApi(Resource):
    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        rtn = []
        if sys:
            src = DataSource.query.filter(
                DataSource.src_type == DataSourceType.SQL,
                DataSource.src_model == DatasourceModel.DbSession,
                DataSource.sys_id == sys.id
            ).first()
            if src:
                #sys_db = db_list.get(src.source['uri'])
                #if not sys_db:
                try:
                    sys_db = create_engine(src.source['uri']).connect()
                except Exception:
                    return {
                        'message': 'failed to connect to database.'
                    }, 404
                    #else:
                    #    db_list[src.source['uri']] = sys_db
                results = sys_db.execute(text(src.source['sql'])).fetchall()
                for result in results:
                    tmp = {}
                    for idx in xrange(len(src.source['formatter'])):
                        try:
                            tmp[src.source['formatter'][idx]['key']] = unicode(result[idx])
                        except IndexError:
                            tmp[src.source['formatter'][idx]['key']] = \
                                src.source['formatter'][idx]['default']
                    rtn.append(tmp)
                sys_db.close()
                return rtn
            else:
                return {
                    'message': 'no data source for system {}'.format(sys.name)
                }, 404
        else:
            return {
                'message': 'system not found'
            }, 404
