# -*- coding: UTF-8 -*-
import logging
from os import path
from paramiko import SSHClient, AutoAddPolicy, RSAKey, PasswordRequiredException
from excepts import ModuleNotFound, SSHConnNotEstablished
from configs import SSHConfig, Result, ErrorCode
from Parsers.psauxParser import psauxParser

class Executor():
    def __init__(self, ssh_config, parser=None):
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.client.load_system_host_keys()
        self.parser = parser
        self.result = Result()
        self.result.destination = ssh_config.ssh_host
        try:
            if ssh_config.ssh_key and path.isfile(ssh_config.ssh_key):
                self.pKeyConnect(ssh_config)
            else:
                self.passConnect(ssh_config)
        except Exception:
            raise

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
                logging.warning(
                    'Fail to Load RSAKey({}), make sure password for key is correct.'\
                        .format(ssh_config.ssh_key)
                )
        try:
            self.client.connect(
                hostname=ssh_config.ssh_host,
                port=ssh_config.ssh_port,
                username=ssh_config.ssh_user,
                pkey=pKey
            )
        except Exception:
            self.result.error_code = ErrorCode.timeout

    def passConnect(self, ssh_config):
        try:
            self.client.connect(
                hostname=ssh_config.ssh_host,
                port=ssh_config.ssh_port,
                username=ssh_config.ssh_user,
                password=ssh_config.ssh_password
            )
        except Exception:
            raise

    def run(self, module):
        import_mod = 'import Libs.{} as mod'.format(module.get('name'))
        try:
            exec import_mod
        except ImportError:
            raise
        if not self.parser:
            import_parser = 'from Parsers.{0}Parser import {0}Parser as par'\
                .format(module.get('name'))
            try:
                exec import_parser
            except ImportError:
                logging.warning("Trying import with({}) failed.".format(import_parser))
            else:
                self.parser = par
        stdin, stdout, stderr = mod.run(client=self.client, module=module)
        self.result.return_code = stdout.channel.recv_exit_status()
        self.result.module = module
        if self.result.return_code == 0:
            self.result.lines = [line.rstrip('\r\n') for line in stdout.readlines()]
            if self.parser:
                self.result.data = self.parser(self.result.lines).format2json()
        else:
            self.result.lines = [line.rstrip('\r\n') for line in stderr.readlines()]
        return self.result

if __name__ == '__main__':
    conf = SSHConfig('192.168.92.26', 'root', 'Quantdo@SH2016!')
    executor = Executor(conf)
    result = executor.run(
        {
            'name': 'quantdoLogin',
            'quantdoLogin': '/root/right.txt',
        }
    )
    #print result.__dict__
    print result.lines
    print result.data
