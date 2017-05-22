# -*- coding: UTF-8 -*-
import sys
from os import path
from paramiko import (
    SSHClient, AutoAddPolicy, RSAKey,
    PasswordRequiredException
)
from paramiko.ssh_exception import NoValidConnectionsError
import winrm
sys.path.append(path.join(path.dirname(sys.argv[0]), '../'))
<<<<<<< HEAD
from SysManager import logging
from excepts import ModuleNotFound
from configs import (
    RemoteConfig, SSHConfig, WinRmConfig,
    Result, ErrorCode
)
from threading import Thread

class Executor():
    def __init__(self, remote_config, parser=None):
        self.parser = parser
        self.result = Result()
        self.result.destination = remote_config.remote_host

    @staticmethod
    def Create(remote_config, parser=None):
=======
#from SysManager import logging
import logging
from excepts import ModuleNotFound, ImportRSAkeyFaild
from configs import (
    RemoteConfig, SSHConfig, WinRmConfig, HttpConfig,
    Result
)
import urllib
import requests
import re
import json

class Executor():
    def __init__(self, remote_config, parser=None):
        self.remote_config = remote_config
        self.parser = parser

    @staticmethod
    def Create(remote_config, parser=None, session=None):
>>>>>>> 4-qdiam-special
        if isinstance(remote_config, SSHConfig):
            return SSHExecutor(remote_config, parser)
        if isinstance(remote_config, WinRmConfig):
            return WinRmExecutor(remote_config, parser)
<<<<<<< HEAD

    def run(self, module):
        pass
=======
        if isinstance(remote_config, HttpConfig):
            return HttpExecutor(remote_config, parser, session)

    def run(self, module):
        import_mod = 'import Libs.{} as mod'.format(module.get('name'))
        try:
            exec import_mod
        except ImportError:
            raise ModuleNotFound(module.get('name'))
        if not self.parser:
            import_parser = 'from Parsers.{0}Parser import {0}Parser as par'\
                .format(module.get('name'))
            try:
                exec import_parser
            except ImportError:
                logging.info("Trying import with({}) failed.".format(import_parser))
            else:
                self.parser = par
        stdin, stdout, stderr = mod.run(client=self.client, module=module)
        self.result = Result()
        self.result.destination = self.remote_config.remote_host
        self.result.return_code = stdout.channel.recv_exit_status()
        self.result.module = module
        if self.result.return_code == 0:
            self.result.lines = [line.rstrip('\r\n') for line in stdout.readlines()]
            if self.parser:
                self.result.data = self.parser(self.result.lines).format2json()
                self.parser = None
        else:
            self.result.lines = [line.rstrip('\r\n') for line in stderr.readlines()]
        return self.result
>>>>>>> 4-qdiam-special

class WinRmExecutor(Executor):
    def __init__(self, remote_config, parser=None):
        Executor.__init__(self, remote_config, parser)
        self.client = winrm.Session(
            remote_config.remote_host,
            (remote_config.remote_user, remote_config.remote_password)
        )

<<<<<<< HEAD

=======
>>>>>>> 4-qdiam-special
class SSHExecutor(Executor):
    def __init__(self, remote_config, parser=None):
        Executor.__init__(self, remote_config, parser)
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.client.load_system_host_keys()
        try:
            if remote_config.ssh_key:
                if path.isfile(remote_config.ssh_key):
                    self.pKeyConnect(remote_config)
            else:
                self.passConnect(remote_config)
        except NoValidConnectionsError, err:
            logging.error(err)
        except Exception, err:
            logging.error(err)

    def pKeyConnect(self, ssh_config):
        try:
            pKey = RSAKey.from_private_key_file(filename=ssh_config.ssh_key)
        except PasswordRequiredException:
            if ssh_config.ssh_key_pass:
                pKey = RSAKey.from_private_key_file(
                    filename=ssh_config.ssh_key,
                    password=ssh_config.ssh_key_pass
                )
            else:
                err_msg = 'Fail to Load RSAKey({}), make sure password for key is correct.'\
                    .format(ssh_config.ssh_key)
                logging.warning(err_msg)
                raise ImportRSAkeyFaild(err_msg)
        else:
            self.client.connect(
                hostname=ssh_config.remote_host,
                port=ssh_config.remote_port,
                username=ssh_config.remote_user,
                pkey=pKey
            )

    def passConnect(self, ssh_config):
        self.client.connect(
            hostname=ssh_config.remote_host,
            port=ssh_config.remote_port,
            username=ssh_config.remote_user,
            password=ssh_config.remote_password
        )

class HttpExecutor(Executor):
    def __init__(self, remote_config, parser=None, session=None):
        Executor.__init__(self, remote_config, parser)
        self.session = session
        self.client = requests.Session()

    def run(self, module):
        pass

if __name__ == '__main__':
<<<<<<< HEAD
=======
    rtn = []
    result = {}
    '''
    conf = SSHConfig('192.168.92.26', 'root', 'Quantdo@SH2016!')
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
    result['server'] = conf.remote_host
    result['uptime'] = resultlist[0].data
    result['cpu'] = resultlist[1].data
    result['disks'] = resultlist[2].data
    result['memory'] = resultlist[3].data['mem']
    result['swap'] = resultlist[3].data['swap']
>>>>>>> 4-qdiam-special
    conf = SSHConfig('192.168.101.100', 'qdam', 'qdam')
    executor = Executor.Create(conf)
    result = executor.run(
        {
            'name': 'quantdoLogin',
            'quantdoLogin': '/home/qdam/qtrade/bin/Syslog.log'
        }
    )
    for (k, v) in result.data.iteritems():
        data = {
            'seat_id': k,
            'seat_status': u"",
            'conn_count': 0,
            'login_success': 0,
            'login_fail': 0,
            'disconn_count': 0
        }
        for each in v:
            print type(each.get('message'))
            print each.get('message')
            if each.get('message').find('连接成功') >= 0:
                data['seat_status'] = u'连接成功'
                data['conn_count'] += 1
            elif each['message'].find('登录成功') >= 0:
                data['seat_status'] = u'登录成功'
                data['login_success'] += 1
            elif each['message'].find('登录失败') >= 0:
                data['seat_status'] = u'登录失败'
                data['login_fail'] += 1
            elif each['message'].find('断开') >= 0:
                data['seat_status'] = u'连接断开'
                data['disconn_count'] += 1
            else:
                data['seat_status'] = u'未连接'
        rtn.append(data)
    print rtn
    conf = SSHConfig('192.168.101.102', 'quantdo', 'quantdo')
    mod = {
        'name': 'shell',
        'shell': """
            grep ".CaptchaController \[" catalina.out | tail -1 | awk '{print $9}'
        """,
        'args': {
            'chdir': 'apache-tomcat*/logs'
        }
    }
    result = Executor.Create(conf).run(mod)
    for line in result.lines:
        print line
    '''
    conf = HttpConfig(
        ip='10.100.10.10',
        user='yw',
        password='1',
        version='1.0.3'
    )
<<<<<<< HEAD
    #print result.lines
    logging.info(result.data)
    print result.data
=======
    exe = Executor.Create(conf)
    print exe.login
>>>>>>> 4-qdiam-special
