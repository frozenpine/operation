# -*- coding: UTF-8 -*-
import json
import logging
import re

#import threading
import arrow
import gevent
from flask_restful import Resource
from sqlalchemy import create_engine
from sqlalchemy.sql import text

from app import globalEncryptKey
from app.models import (DataSource, DataSourceModel, DataSourceType,
                        SocketDirection, TradeSystem)
from SysManager.Common import AESCrypto
from SysManager.configs import SSHConfig, WinRmConfig
from SysManager.executor import Executor


def _decrypt(match):
    return match.group(1) + \
        AESCrypto.decrypt(
            match.group(2),
            globalEncryptKey
        ) + \
        match.group(3)

class ServerList(object):
    def __init__(self):
        self.server_list = {}
        self.rtn = {'details': []}

    def find_servers(self, sys):
        for svr in sys.servers:
            if self.server_list.has_key(svr.ip):
                continue
            else:
                self.server_list[svr.ip] = (svr, {'status': {}})
        if len(sys.child_systems) > 0:
            for child_sys in sys.child_systems:
                self.find_servers(child_sys)

    def make_response(self):
        for data in self.server_list.values():
            self.rtn['details'].append({
                'id': data[0].id,
                'server': data[0].ip,
                'updated_time': arrow.now().format('HH:mm:ss'),
                'uptime': data[1]['status'].get('uptime'),
                'cpu': data[1]['status'].get('cpu'),
                'disks': data[1]['status'].get('disks'),
                'memory': data[1]['status'].get('memory'),
                'swap': data[1]['status'].get('swap')
            })

class ServerStaticListApi(Resource, ServerList):
    def __init__(self):
        super(ServerStaticListApi, self).__init__()

    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
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
        if sys:
            self.rtn['sys_id'] = sys.id
            self.find_servers(sys)
            for entry in self.server_list.values():
                self.checker.append(gevent.spawn(self.check_svr, entry))
            gevent.joinall(self.checker)
            self.make_response()
            return self.rtn
        else:
            return {
                'message': 'system not found'
            }, 404

    def check_svr(self, entry):
        result = {}
        conf = SSHConfig(entry[0].ip, entry[0].user, entry[0].password)
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
        result['id'] = entry[0].id
        result['server'] = entry[0].ip
        result['uptime'] = resultlist[0].data
        result['cpu'] = resultlist[1].data
        result['disks'] = resultlist[2].data
        result['memory'] = resultlist[3].data['mem']
        result['swap'] = resultlist[3].data['swap']
        entry[1]['status'] = result
        executor.client.close()

class SystemList(object):
    def __init__(self):
        self.system_list = []
        self.rtn = []
        self.proc_status = {}

    def find_systems(self, sys):
        if len(sys.processes) > 0:
            self.system_list.append(sys)
        if len(sys.child_systems) > 0:
            for child_sys in sys.child_systems:
                self.find_systems(child_sys)

    def make_response(self):
        for each_sys in self.system_list:
            self.rtn.append(
                {
                    'name': each_sys.name,
                    'updated_time': arrow.now().format('HH:mm:ss'),
                    'detail': [{
                        'id': proc.id,
                        'process': proc.name,
                        'proc_role': "{}".format(proc.type.name),
                        'status': {
                            'user': self.proc_status.has_key(proc) and \
                                self.proc_status[proc].get('user') or None,
                            'pid': self.proc_status.has_key(proc) and \
                                self.proc_status[proc].get('pid') or None,
                            'cpu': self.proc_status.has_key(proc) and \
                                self.proc_status[proc].get('cpu%') or None,
                            'mem': self.proc_status.has_key(proc) and \
                                self.proc_status[proc].get('mem%') or None,
                            'vsz': self.proc_status.has_key(proc) and \
                                self.proc_status[proc].get('vsz') or None,
                            'rss': self.proc_status.has_key(proc) and \
                                self.proc_status[proc].get('rss') or None,
                            'tty': self.proc_status.has_key(proc) and \
                                self.proc_status[proc].get('tty') or None,
                            'stat': self.proc_status.has_key(proc) and \
                                self.proc_status[proc].get('stat') or None,
                            'start': self.proc_status.has_key(proc) and \
                                self.proc_status[proc].get('start') or None,
                            'time': self.proc_status.has_key(proc) and \
                                self.proc_status[proc].get('time') or None,
                            'command': self.proc_status.has_key(proc) and \
                                self.proc_status[proc].get('command') or None
                        },
                        'server':
                            proc.server.name + "({})".format(proc.server.ip),
                        'sockets': [{
                            'id': sock.id,
                            'name': sock.name,
                            'uri': sock.uri,
                            'ip': sock.ip,
                            'port': sock.port,
                            'status':
                                hasattr(self, 'socket_status') \
                                and getattr(self, 'socket_status').get(
                                    '{}://{}:{}'.format(
                                        sock.type.name.lower(),
                                        sock.ip, sock.port
                                    ), {'stat': u'未侦听'}
                                ) or {'stat': u'未侦听'}
                        } for sock in proc.sockets \
                            if sock.direction.value == SocketDirection.Listen.value],
                        'connections': [{
                            'id': sock.id,
                            'name': sock.name,
                            'uri': sock.uri,
                            'ip': sock.ip,
                            'port': sock.port,
                            'status':
                                hasattr(self, 'connection_status') \
                                and getattr(self, 'connection_status').get(
                                    '{}://{}:{}'.format(
                                        sock.type.name.lower(),
                                        sock.ip, sock.port
                                    ), {'stat': u'未连接'}
                                ) or {'stat': u'未连接'}
                        } for sock in proc.sockets \
                            if sock.direction.value == SocketDirection.Establish.value]
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
        self.socket_status = {}
        self.connection_status = {}

    def find_processes(self):
        for child_sys in self.system_list:
            for proc in child_sys.processes:
                key = (proc.server.ip, proc.system.user, proc.system.password)
                if not self.proc_list.has_key(key):
                    self.proc_list[key] = []
                self.proc_list[key].append(proc)

    def check_proc(self, entry, processes):
        port_list = set()
        process_list = set()
        conf = SSHConfig(
            entry[0],
            entry[1],
            entry[2]
        )
        executor = Executor.Create(conf)
        for proc in processes:
            process_list.add(proc.exec_file)
            port_list |= set([socket.port for socket in proc.sockets])
            mod = {
                'name': 'psaux',
                'args': {
                    'processes': [proc.exec_file],
                    'param': [proc.param]
                }
            }
            result = executor.run(mod).data
            if len(result) > 0:
                self.proc_status[proc] = result[0]
            else:
                self.proc_status[proc] = {
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
        mod = {'name': 'netstat'}
        if len(port_list) > 0:
            if not mod.has_key('args'):
                mod['args'] = {}
            mod['args']['ports'] = list(port_list)
        if len(process_list) > 0:
            if not mod.has_key('args'):
                mod['args'] = {}
            mod['args']['processes'] = list(process_list)
        if mod.has_key('args'):
            socket_result = executor.run(mod)
            if 'LISTEN' in socket_result.data.keys():
                # 处理Windows Linux平台的不同
                try:
                    sockets = socket_result.data['LISTEN']
                except KeyError:
                    sockets = socket_result.data['LISTENING']
                for socket in sockets:
                    self.socket_status['{}://{}:{}'.format(
                        socket['proto'],
                        socket['local_ip'],
                        socket['local_port']
                    )] = {
                        'proto': socket['proto'],
                        'ip': socket['local_ip'],
                        'port': socket['local_port'],
                        'stat': u'侦听中'
                    }
            if socket_result.data.has_key('ESTABLISHED'):
                for socket in socket_result.data['ESTABLISHED']:
                    self.connection_status['{}://{}:{}'.format(
                        socket['proto'],
                        socket['remote_ip'],
                        socket['remote_port']
                    )] = {
                        'proto': socket['proto'],
                        'ip': socket['remote_ip'],
                        'port': socket['remote_port'],
                        'stat': u'已连接'
                    }
        executor.client.close()

    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        if sys:
            self.find_systems(sys)
            self.find_processes()
            for entry, proc_list in self.proc_list.iteritems():
                self.checker.append(
                    gevent.spawn(self.check_proc, entry, proc_list)
                )
            gevent.joinall(self.checker)
            self.make_response()
            return self.rtn
        else:
            return {
                'message': 'system not found'
            }, 404

class LoginListApi(Resource, SystemList):
    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        self.find_systems(sys)
        rtn = []
        if sys:
            src = DataSource.query.filter(
                DataSource.src_type == DataSourceType.SQL,
                DataSource.src_model == DataSourceModel.Seat,
                DataSource.sys_id.in_([x.id for x in self.system_list])
            ).first()
            if src:
                try:
                    if globalEncryptKey:
                        uri = re.sub(
                            '^(.+://[^:]+:)([^@]+)(@.+)$',
                            _decrypt,
                            src.source['uri']
                        )
                    else:
                        uri = src.source['uri']
                    sys_db = create_engine(uri).connect()
                except Exception:
                    return {
                        'message': 'faild to connect to database.'
                    }, 404
                else:
                    results = sys_db.execute(text(src.source['sql'])).fetchall()
                    for result in results:
                        tmp = {}
                        for idx in xrange(len(src.source['formatter'])):
                            try:
                                tmp[src.source['formatter'][idx]['key']] = unicode(result[idx])
                            except IndexError:
                                tmp[src.source['formatter'][idx]['key']] = \
                                    src.source['formatter'][idx]['default']
                            tmp['updated_time'] = arrow.now().format('HH:mm:ss')
                        rtn.append(tmp)
                    sys_db.close()
                    return rtn
            else:
                return {
                    'message': u'no data source configured for system {}'.format(sys.name)
                }, 404
        else:
            return {
                'message': 'system not found'
            }, 404

class LoginCheckApi(Resource):
    def __init__(self):
        self.syslog_list = {}
        self.rtn = []
        self.checker = []
        #self.mutex = threading.Lock()

    def find_syslog(self, sys):
        log_srcs = DataSource.query.filter(
            DataSource.src_type == DataSourceType.FILE,
            DataSource.src_model == DataSourceModel.Seat,
            DataSource.sys_id == sys.id,
            DataSource.disabled == False
        ).all()
        for src in log_srcs:
            if globalEncryptKey:
                uri = re.sub(
                    '^(.+://[^:]+:)([^@]+)(@.+)$',
                    _decrypt,
                    src.source['uri']
                )
            else:
                uri = src.source['uri']
            uri = uri.split('#')
            svr = uri[0].rstrip('/')
            log = uri[1]
            if not self.syslog_list.has_key(svr):
                self.syslog_list[svr] = {
                    'formatter': src.source['formatter'],
                    'msg_pattern': src.source['msg_pattern'],
                    'key_words': src.source['key_words'],
                    'logs': []
                }
            self.syslog_list[svr]['logs'].append(log)

    def check_log(self, uri, datas):
        reg = re.compile(
            r'^(?P<method>[^:]+)://(?P<user>[^:]+):(?P<pass>[^@]+)@(?P<ip>[^:]+):(?P<port>\d+)$'
        )
        pars = reg.match(uri).groupdict()
        if pars['method'] == 'ssh':
            conf = SSHConfig(
                ip=pars['ip'],
                user=pars['user'],
                password=pars['pass'],
                port=int(pars['port'])
            )
        else:
            conf = WinRmConfig(
                ip=pars['ip'],
                user=pars['user'],
                password=pars['pass'],
                port=int(pars['port'])
            )
        executor = Executor.Create(conf)
        for log in datas['logs']:
            logfile, module = log.split('?')
            mod = {}
            mod['name'] = module
            mod[module] = logfile.rstrip('/')
            result = executor.run(mod)
            for k, v in result.data.iteritems():
                pattern = re.compile(datas['msg_pattern'])
                data = {}
                for idx in xrange(len(datas['formatter'])):
                    data[datas['formatter'][idx]['key']] = \
                        datas['formatter'][idx]['default']
                data['seat_id'] = k
                data['updated_time'] = arrow.now().format('HH:mm:ss')
                for each in v:
                    try:
                        message = each.get('message').decode('utf-8')
                    except UnicodeDecodeError:
                        message = each.get('mesage').decode('gbk')
                    if datas['key_words']['conn'] in message:
                        data['seat_status'] = u'连接成功'
                        data['conn_count'] += 1
                    elif datas['key_words']['login'] in message:
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
                    elif datas['key_words']['logfail'] in message:
                        data['seat_status'] = u'登录失败'
                        data['login_fail'] += 1
                    elif datas['key_words']['disconn'] in message:
                        data['seat_status'] = u'连接断开'
                        data['disconn_count'] += 1
                    else:
                        data['seat_status'] = u'未连接'
                #self.mutex.acquire()
                self.rtn.append(data)
                #self.mutex.release()
        executor.client.close()

    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        if sys:
            self.find_syslog(sys)
            for (k, v) in self.syslog_list.items():
                self.checker.append(gevent.spawn(self.check_log, k, v))
            gevent.joinall(self.checker)
            return self.rtn
        else:
            return {
                'message': 'system not found'
            }, 404

class UserSessionListApi(Resource, SystemList):
    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        self.find_systems(sys)
        rtn = []
        if sys:
            src = DataSource.query.filter(
                DataSource.src_type == DataSourceType.SQL,
                DataSource.src_model == DataSourceModel.Session,
                DataSource.sys_id.in_([x.id for x in self.system_list]),
                DataSource.disabled == False
            ).first()
            if src:
                try:
                    if globalEncryptKey:
                        uri = re.sub(
                            '^(.+://[^:]+:)([^@]+)(@.+)$',
                            _decrypt,
                            src.source['uri']
                        )
                    else:
                        uri = src.source['uri']
                    sys_db = create_engine(uri).connect()
                except Exception:
                    return {
                        'message': 'failed to connect to database.'
                    }, 404
                else:
                    results = sys_db.execute(text(src.source['sql'])).fetchall()
                    for result in results:
                        tmp = {}
                        for idx in xrange(len(src.source['formatter'])):
                            try:
                                tmp[src.source['formatter'][idx]['key']] = unicode(result[idx])
                            except IndexError:
                                tmp[src.source['formatter'][idx]['key']] = \
                                    src.source['formatter'][idx]['default']
                            finally:
                                tmp['updated_time'] = arrow.now().strftime('%H:%M:%S')
                        rtn.append(tmp)
                    sys_db.close()
                    return rtn
            else:
                return {
                    'message': u'no data source for system {}'.format(sys.name)
                }, 404
        else:
            return {
                'message': 'system not found'
            }, 404
