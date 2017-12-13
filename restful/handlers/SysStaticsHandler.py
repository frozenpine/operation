# -*- coding: UTF-8 -*-
import logging
import re
import threading

import arrow
import gevent
from flask import current_app
from flask_restful import Resource
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from sqlalchemy.exc import NoSuchColumnError, OperationalError

from SysManager.Common import AESCrypto
from SysManager.configs import SSHConfig, WinRmConfig
from SysManager.executor import Executor
from app import flask_logger as logging
from app import globalEncryptKey
from app.models import (DataSource, DataSourceModel, PlatformType,
                        DataSourceType, SocketDirection, TradeSystem)
from restful.protocol import RestProtocol


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
            if svr.ip in self.server_list.keys():
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
                'updated_time': arrow.utcnow()
                .to(current_app.config['TIME_ZONE']).format('HH:mm:ss'),
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
            return RestProtocol(self.rtn)
        else:
            return RestProtocol(
                message='System not found',
                error_code=-1
            ), 404


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
                ''' self.checker.append(threading.Thread(
                    target=self.check_svr,
                    args=(entry,)
                )) '''
            ''' for tr in self.checker:
                tr.setDaemon(True)
                tr.start()
                gevent.sleep(0)
                tr.join() '''
            # gevent.sleep(0)
            gevent.joinall(self.checker)
            self.make_response()
            return RestProtocol(self.rtn)
        else:
            return RestProtocol(message='System not found', error_code=-1), 404

    def check_svr(self, entry):
        result = {}
        conf = SSHConfig(entry[0].ip, entry[0].user, entry[0].password)
        modlist = [
            {'name': 'uptime'},
            {'name': 'mpstat' if entry[0].platform.value == 1 else 'cyg_mpstat'},
            {'name': 'df' if entry[0].platform.value == 1 else 'cyg_df'},
            {'name': 'free' if entry[0].platform.value == 1 else 'cyg_free'}
        ]
        resultlist = []
        executor = Executor.Create(conf)
        if executor:
            for mod in modlist:
                resultlist.append(executor.run(mod))
        result['id'] = entry[0].id
        result['server'] = entry[0].ip
        result['uptime'] = resultlist and resultlist[0].data or ''
        result['cpu'] = resultlist and resultlist[1].data
        result['disks'] = resultlist and resultlist[2].data
        result['memory'] = resultlist and resultlist[3].data['mem']
        result['swap'] = resultlist and resultlist[3].data['swap']
        entry[1]['status'] = result


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
            sys_define = {
                'name': each_sys.name,
                'updated_time': arrow.utcnow()
                .to(current_app.config['TIME_ZONE']).format('HH:mm:ss'),
                'version': each_sys.version,
                'detail': []
            }
            for proc in each_sys.processes:
                proc_define = {
                    'id': proc.id,
                    'process': proc.name,
                    'proc_role': "{}".format(proc.type.name),
                    'version': proc.version,
                    'status': {
                        'user': self.proc_status[proc].get('user'),
                        'pid': self.proc_status[proc].get('pid'),
                        'cpu': self.proc_status[proc].get('cpu%'),
                        'mem': self.proc_status[proc].get('mem%'),
                        'vsz': self.proc_status[proc].get('vsz'),
                        'rss': self.proc_status[proc].get('rss'),
                        'tty': self.proc_status[proc].get('tty'),
                        'stat': self.proc_status[proc].get('stat'),
                        'start': self.proc_status[proc].get('start'),
                        'time': self.proc_status[proc].get('time'),
                        'command': self.proc_status[proc].get('command')
                    } if proc in self.proc_status.keys() else {
                        'user': None, 'pid': None, 'cpu': None, 'mem': None, 'vsz': None, 'rss': None,
                        'tty': None, 'stat': 'stopped', 'start': None, 'time': None, 'command': None
                    },
                    'server': proc.server.name + "({})".format(proc.server.ip),
                    'sockets': [],
                    'connections': []
                }
                for socket in proc.sockets:
                    if socket.direction == SocketDirection.Listen:
                        listen_define = {
                            'id': socket.id,
                            'name': socket.name,
                            'uri': socket.uri,
                            'ip': socket.ip,
                            'port': socket.port,
                            'status': {
                                'proto': self.proc_status[proc]['listening'][unicode(socket.port)]['proto'],
                                'ip': self.proc_status[proc]['listening'][unicode(socket.port)]['local_ip'],
                                'port': self.proc_status[proc]['listening'][unicode(socket.port)]['local_port'],
                                'stat': u'侦听中'
                            } if proc in self.proc_status.keys() and
                            'listening' in self.proc_status[proc].keys() and
                            unicode(socket.port) in self.proc_status[proc]['listening'].keys() else
                            {'stat': '未侦听'}
                        }
                        proc_define['sockets'].append(listen_define)
                    if socket.direction == SocketDirection.Establish:
                        connection_define = {
                            'id': socket.id,
                            'name': socket.name,
                            'uri': socket.uri,
                            'ip': socket.ip,
                            'port': socket.port,
                            'status': {
                                'proto': self.proc_status[proc]['established'][unicode(socket.port)]['proto'],
                                'ip': self.proc_status[proc]['established'][unicode(socket.port)]['remote_ip'],
                                'port': self.proc_status[proc]['established'][unicode(socket.port)]['remote_port'],
                                'stat': u'已连接'
                            } if proc in self.proc_status.keys() and
                            'established' in self.proc_status[proc].keys() and
                            unicode(socket.port) in self.proc_status[proc]['established'].keys() else
                            {'stat': u'未连接'}
                        }
                        proc_define['connections'].append(connection_define)
                sys_define['detail'].append(proc_define)
            self.rtn.append(sys_define)


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
            return RestProtocol(self.rtn)
        else:
            return RestProtocol(message='System not found', error_code=-1), 404


class ProcStaticApi(Resource, SystemList):
    def __init__(self):
        super(ProcStaticApi, self).__init__()
        self.proc_list = {}
        self.checker = []

    def find_processes(self):
        for child_sys in self.system_list:
            for proc in child_sys.processes:
                key = (proc.server.ip, proc.server.user, proc.server.password, proc.server.platform)
                if key not in self.proc_list.keys():
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
        if not executor:
            logging.warning(
                'Executor init failed with ip: {ip}, user: {user}'
                .format(ip=conf.remote_host, user=conf.remote_user)
            )
            return
        for proc in processes:
            process_list.add((proc.exec_file, proc.param or ''))
            port_list |= set([socket.port for socket in proc.sockets])
        gevent.sleep(0)
        mod = {
            'name': 'psaux' if entry[3].value == 1 else 'cyg_psaux',
            'args': {
                'processes': list(process_list),
            }
        }
        running_results = executor.run(mod).data
        gevent.sleep(0)
        mod = {'name': 'netstat' if entry[3].value == 1 else 'cyg_netstat'}
        if len(port_list) > 0:
            if 'args' not in mod.keys():
                mod['args'] = {}
            mod['args']['ports'] = list(port_list)
        if len(process_list) > 0:
            if 'args' not in mod.keys():
                mod['args'] = {}
            mod['args']['processes'] = list(process_list)
        if 'args' in mod.keys():
            socket_results = executor.run(mod).data
        else:
            socket_results = {}
        gevent.sleep(0)
        # find = lambda x, y: x and x in y

        def find(x, y):
            return x and x in y

        for proc in processes:
            match = False
            for result in running_results:
                exec_list = result['command'].split(' ')
                if proc.server.platform == PlatformType.Linux and \
                   proc.exec_file in exec_list[0] and \
                   reduce(lambda x, y: x or y,
                          [find(proc.param, param) for param in exec_list[1:]],
                          len(exec_list) <= 1):
                    self.proc_status[proc] = result
                    match = True
                    break
                if proc.server.platform == PlatformType.Windows and \
                   proc.exec_file + proc.param in exec_list[0]:
                    self.proc_status[proc] = result
                    match = True
                    break
            if not match:
                self.proc_status[proc] = {
                    'user': None, 'pid': None, 'cpu': None, 'mem': None, 'vsz': None, 'rss': None,
                    'tty': None, 'stat': 'stopped', 'start': None, 'time': None, 'command': None
                }

            if len(proc.sockets) > 0 and self.proc_status[proc]['pid']:
                if 'LISTEN' in socket_results.keys() or 'LISTENING' in socket_results.keys():
                    # 处理Windows Linux平台的不同
                    try:
                        sockets = socket_results['LISTEN']
                    except KeyError:
                        sockets = socket_results['LISTENING']
                    for socket in sockets:
                        if socket['pid'] == self.proc_status[proc]['pid']:
                            if 'listening' not in self.proc_status[proc].keys():
                                self.proc_status[proc]['listening'] = {}
                            self.proc_status[proc]['listening'][socket['local_port']] = socket
                if 'ESTABLISHED' in socket_results.keys():
                    for socket in socket_results['ESTABLISHED']:
                        if socket['pid'] == self.proc_status[proc]['pid']:
                            if 'established' not in self.proc_status[proc].keys():
                                self.proc_status[proc]['established'] = {}
                            self.proc_status[proc]['established'][socket['remote_port']] = socket

    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        if sys:
            self.find_systems(sys)
            self.find_processes()
            for entry, proc_list in self.proc_list.iteritems():
                self.checker.append(
                    gevent.spawn(self.check_proc, entry, proc_list)
                )
                ''' self.checker.append(threading.Thread(
                    target=self.check_proc,
                    args=(entry, proc_list,)
                )) '''
            ''' for tr in self.checker:
                tr.setDaemon(True)
                tr.start()
                gevent.sleep(0)
                tr.join() '''
            # gevent.sleep(0)
            gevent.joinall(self.checker)
            self.make_response()
            return RestProtocol(self.rtn)
        else:
            return RestProtocol(message='System not found', error_code=-1), 404


class ProcVersionApi(Resource):
    def __init__(self):
        super(ProcVersionApi, self).__init__()
        self.proc_list = {}
        self.checker = []
        self.rtn = {}

    def find_processes(self, sys):
        for proc in sys.processes:
            key = (proc.server.ip, sys.user, sys.password)
            if key not in self.proc_list.keys():
                self.proc_list[key] = []
            self.proc_list[key].append(proc)

    def check_proc(self, entry, processes):
        conf = SSHConfig(
            entry[0],
            entry[1],
            entry[2]
        )
        executor = Executor.Create(conf)
        if not executor:
            logging.warning(
                'Executor init failed with ip: {ip}, user: {user}'
                .format(ip=conf.remote_host, user=conf.remote_user)
            )
            return
        for proc in processes:
            if proc.version_method:
                mod = {
                    'name': proc.version_method,
                    'args': {
                        'dir': proc.base_dir,
                        'file': proc.exec_file
                    }
                }
                proc.version = executor.run(mod).lines
            gevent.sleep(0)

    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        if sys:
            self.find_processes(sys)
            for entry, proc_list in self.proc_list.iteritems():
                self.checker.append(
                    gevent.spawn(self.check_proc, entry, proc_list)
                )
            gevent.joinall(self.checker)
            rtn = {
                'name': sys.name,
                'updated_time': arrow.utcnow()
                .to(current_app.config['TIME_ZONE']).format('HH:mm:ss'),
                'version': sys.version,
                'detail': [{
                    'id': proc.id,
                    'process': proc.name,
                    'proc_role': "{}".format(proc.type.name),
                    'version': proc.version,
                    'server':
                        proc.server.name + "({})".format(proc.server.ip),
                } for proc in sys.processes]
            }
            return RestProtocol(rtn)
        else:
            return RestProtocol(message='System not found', error_code=-1), 404


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
                except OperationalError as e:
                    return RestProtocol(
                        message=e.message,
                        error_code=-1
                    ), 404
                else:
                    results = sys_db.execute(text(src.source['sql'])).fetchall()
                    for result in results:
                        tmp = {}
                        for idx in xrange(len(src.source['formatter'])):
                            try:
                                tmp[src.source['formatter'][idx]['key']] = unicode(result[idx])
                            except (NoSuchColumnError, IndexError):
                                tmp[src.source['formatter'][idx]['key']] = \
                                    src.source['formatter'][idx]['default']
                            tmp['updated_time'] = arrow.utcnow()\
                                .to(current_app.config['TIME_ZONE']).format('HH:mm:ss')
                        rtn.append(tmp)
                    sys_db.close()
                    return RestProtocol(rtn)
            else:
                return RestProtocol(
                    message=u'no data source configured for system {}'.format(sys.name),
                    error_code=-1
                )
        else:
            return RestProtocol(message='system not found', error_code=-1), 404


class LoginCheckApi(Resource, SystemList):
    def __init__(self):
        super(LoginCheckApi, self).__init__()
        self.syslog_list = {}
        self.rtn = []
        self.checker = []
        # self.mutex = threading.Lock()
        self.app_context = current_app.app_context()

    def find_syslog(self):
        log_srcs = DataSource.query.filter(
            DataSource.src_type == DataSourceType.FILE,
            DataSource.src_model == DataSourceModel.Seat,
            DataSource.sys_id.in_([x.id for x in self.system_list]),
            DataSource.disabled.is_(False)
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
            if svr not in self.syslog_list.keys():
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
            with self.app_context:
                for k, v in result.data.iteritems():
                    pattern = re.compile(datas['msg_pattern'])
                    data = {}
                    for idx in xrange(len(datas['formatter'])):
                        data[datas['formatter'][idx]['key']] = \
                            datas['formatter'][idx]['default']
                    data['seat_id'] = k
                    data['updated_time'] = arrow.utcnow()\
                        .to(current_app.config['TIME_ZONE']).format('HH:mm:ss')
                    for each in v:
                        ''' try:
                            message = each.get('message').decode('utf-8')
                        except UnicodeDecodeError:
                            message = each.get('mesage').decode('gbk') '''
                        message = each.get('message')
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
                    # self.mutex.acquire()
                    self.rtn.append(data)
                    # self.mutex.release()
        executor.client.close()

    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        self.find_systems(sys)
        if sys:
            self.find_syslog()
            for (k, v) in self.syslog_list.items():
                self.checker.append(gevent.spawn(self.check_log, k, v))
            # gevent.sleep(0)
            gevent.joinall(self.checker)
            return RestProtocol(self.rtn)
        else:
            return RestProtocol(message='system not found', error_code=-1), 404


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
                DataSource.disabled.is_(False)
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
                except OperationalError as e:
                    return RestProtocol(message=e.message, error_code=-1)
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
                                tmp['updated_time'] = arrow.utcnow()\
                                    .to(current_app.config['TIME_ZONE']).format('HH:mm:ss')
                        rtn.append(tmp)
                    sys_db.close()
                    return RestProtocol(rtn)
            else:
                return RestProtocol(
                    message=u'No data source for system {}'.format(sys.name),
                    error_code=-1
                )
        else:
            return RestProtocol(message='System not found', error_code=-1), 404


class ConfigList(object):
    def __init__(self):
        self.system_list = []
        self.rtn = []
        self.check_result = {}

    def find_systems(self, sys):
        for proc in sys.processes:
            if len(proc.config_files) > 0:
                self.system_list.append(sys)
                break
        if len(sys.child_systems) > 0:
            for child_sys in sys.child_systems:
                self.find_systems(child_sys)

    def make_response(self):
        for each_sys in self.system_list:
            sys_configs = []
            for proc in each_sys.processes:
                sys_configs.extend(proc.config_files)
            self.rtn.append({
                'name': each_sys.name,
                'sys_id': each_sys.id,
                'detail': [{
                    'id': conf.id,
                    'uuid': conf.uuid,
                    'name': conf.name,
                    'type': conf.config_type.name,
                    'dir': conf.dir,
                    'file': conf.file,
                    'hash': conf.hash_code,
                    'timestamp':
                        conf.timestamp and
                        conf.timestamp.to(current_app.config['TIME_ZONE']).format('YYYY-MM-DD HH:mm:ss'),
                    'hash_changed': self.check_result.get(conf)
                } for conf in sys_configs]
            })


class ConfigListApi(Resource, ConfigList):
    def __init__(self):
        super(ConfigListApi, self).__init__()

    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        if sys:
            self.find_systems(sys)
            self.make_response()
            return RestProtocol(self.rtn)
        else:
            return RestProtocol(message='system not found', error_code=-1), 404


class ConfigCheckApi(Resource, ConfigList):
    def __init__(self):
        super(ConfigCheckApi, self).__init__()
        self.config_file_list = {}
        self.checker = []

    def find_configs(self):
        for each_sys in self.system_list:
            for proc in each_sys.processes:
                key = (proc.server.ip, each_sys.user, each_sys.password)
                if key not in self.config_file_list.keys():
                    self.config_file_list[key] = []
                self.config_file_list[key].extend(proc.config_files)

    def checkConfig(self, entry, config_files):
        remote_config = SSHConfig(entry[0], entry[1], entry[2])
        exe = Executor.Create(remote_config)
        for conf_file in config_files:
            mod = {
                'name': 'md5',
                'args': {
                    'dir': conf_file.dir,
                    'file': conf_file.file
                }
            }
            result = exe.run(mod)
            if result.return_code == 0:
                ''' conf_file.pre_hash_code = conf_file.hash_code
                conf_file.pre_timestamp = conf_file.timestamp '''
                # conf_file.hash_code = result.lines[0]
                # conf_file.timestamp = arrow.utcnow()
                self.check_result[conf_file] = conf_file.hash_code != result.lines[0]

    def get(self, **kwargs):
        sys = TradeSystem.find(**kwargs)
        if sys:
            self.find_systems(sys)
            self.find_configs()
            for remote, configs in self.config_file_list.iteritems():
                ''' self.checker.append(
                    gevent.spawn(self.checkConfig, remote, configs)
                ) '''
                self.checker.append(threading.Thread(
                    target=self.checkConfig,
                    args=(remote, configs,)
                ))
            for tr in self.checker:
                tr.setDaemon(True)
                tr.start()
                gevent.sleep(0)
                tr.join()
            # gevent.sleep(0)
            # gevent.joinall(self.checker)
            self.make_response()
            return RestProtocol(self.rtn)
        else:
            return RestProtocol(message='system not found', error_code=-1), 404
