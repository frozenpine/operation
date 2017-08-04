# -*- coding: UTF-8 -*-
import sys
from os import path

sys.path.append(path.join(path.dirname(sys.argv[0]), '../'))

import requests
import winrm
from paramiko import (AutoAddPolicy, PasswordRequiredException, RSAKey,
                      SSHClient)
from paramiko.ssh_exception import (AuthenticationException,
                                    NoValidConnectionsError)

from SysManager import logger as logging
from configs import HttpConfig, Result, SSHConfig, WinRmConfig
from excepts import ImportRSAkeyFaild, ModuleNotFound, SSHNoValidConnectionsError, SSHAuthenticationException, \
    SSHException


class Executor():
    def __init__(self, remote_config, parser=None):
        self.remote_config = remote_config
        self.parser = parser

    @staticmethod
    def Create(remote_config, parser=None, session=None):
        try:
            if isinstance(remote_config, SSHConfig):
                return SSHExecutor(remote_config, parser)
            if isinstance(remote_config, WinRmConfig):
                return WinRmExecutor(remote_config, parser)
            if isinstance(remote_config, HttpConfig):
                return HttpExecutor(remote_config, parser, session)
        except Exception:
            return None

    @staticmethod
    def CreateByWorker(remote_config, parser=None, session=None):
        if isinstance(remote_config, SSHConfig):
            return SSHExecutor(remote_config, parser)
        if isinstance(remote_config, WinRmConfig):
            return WinRmExecutor(remote_config, parser)
        if isinstance(remote_config, HttpConfig):
            return HttpExecutor(remote_config, parser, session)

    def run(self, module):
        import_mod = 'import Libs.{} as mod'.format(module.get('name'))
        try:
            exec import_mod
        except ImportError:
            raise ModuleNotFound(module.get('name'))
        if not self.parser:
            import_parser = 'from Parsers.{0}Parser import {0}Parser as par' \
                .format(module.get('name'))
            try:
                exec import_parser
            except ImportError:
                logging.info(
                    "Trying import with({}) failed.".format(import_parser))
            else:
                self.parser = par
        stdout, stderr = mod.run(client=self.client, module=module)
        self.result = Result()
        self.result.destination = self.remote_config.remote_host
        self.result.return_code = stdout.channel.recv_exit_status()
        self.result.module = module
        if self.result.return_code == 0:
            self.result.lines = [line for line in stdout.readlines()]
            if self.parser:
                self.result.data = self.parser(self.result.lines).format2json()
                self.parser = None
        else:
            self.result.lines = [line for line in stdout.readlines()]
        return self.result


class WinRmExecutor(Executor):
    def __init__(self, remote_config, parser=None):
        Executor.__init__(self, remote_config, parser)
        self.client = self._connect(remote_config)
        self.parser = parser
        self.result = None

    def _connect(self, remote_config):
        if remote_config.encryption:
            return winrm.Session(
                ':'.join([
                    remote_config.remote_host,
                    str(remote_config.remote_port)
                ]),
                auth=(remote_config.remote_user,
                      remote_config.remote_password),
                transport='ssl',
                server_cert_validation='ignore')
        else:
            return winrm.Session(
                ':'.join([
                    remote_config.remote_host,
                    str(remote_config.remote_port)
                ]),
                auth=(remote_config.remote_user,
                      remote_config.remote_password))


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
            raise SSHNoValidConnectionsError
        except AuthenticationException, err:
            logging.error(err)
            raise SSHAuthenticationException
        except Exception, err:
            logging.error(err)
            raise SSHException

    def pKeyConnect(self, ssh_config):
        try:
            pKey = RSAKey.from_private_key_file(filename=ssh_config.ssh_key)
        except PasswordRequiredException:
            if ssh_config.ssh_key_pass:
                pKey = RSAKey.from_private_key_file(
                    filename=ssh_config.ssh_key,
                    password=ssh_config.ssh_key_pass)
            else:
                err_msg = 'Fail to Load RSAKey({}), make sure password for key is correct.' \
                    .format(ssh_config.ssh_key)
                logging.warning(err_msg)
                raise ImportRSAkeyFaild(err_msg)
        else:
            self.client.connect(
                hostname=ssh_config.remote_host,
                port=ssh_config.remote_port,
                username=ssh_config.remote_user,
                pkey=pKey)

    def passConnect(self, ssh_config):
        self.client.connect(
            hostname=ssh_config.remote_host,
            port=ssh_config.remote_port,
            username=ssh_config.remote_user,
            password=ssh_config.remote_password)


class HttpExecutor(Executor):
    def __init__(self, remote_config, parser=None, session=None):
        Executor.__init__(self, remote_config, parser)
        self.session = session
        self.client = requests.Session()

    def run(self, module):
        pass


if __name__ == '__main__':
    conf = SSHConfig('192.168.101.126', 'qdam', 'qdam')
    exe = Executor.Create(conf)
    mod = {
        'name': 'psaux',
        'args': {
            'processes': [
                'qtrade', 'qdata', 'qmdb', 'qquery', 'qicegateway 1',
                'qicegateway 2'
            ]
        }
    }
    '''
    conf = WinRmConfig('192.168.56.2', 'administrator', '022010blue@safe')
    exe = Executor.Create(conf)
    mod = {
        'name': 'windf'
    }
    '''
    result = exe.run(mod)
    for line in result.lines:
        print line
    print result.data
