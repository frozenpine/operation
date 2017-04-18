# -*- coding: UTF-8 -*-
import logging
from os import path
from paramiko import (
    SSHClient, AutoAddPolicy, RSAKey,
    PasswordRequiredException
)
from paramiko.ssh_exception import NoValidConnectionsError
#from SysManager import logging
from excepts import ModuleNotFound
from configs import SSHConfig, Result, ErrorCode

class Executor():
    def __init__(self, ssh_config, parser=None):
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.client.load_system_host_keys()
        self.parser = parser
        self.result = Result()
        self.result.destination = ssh_config.ssh_host
        try:
            if ssh_config.ssh_key:
                if path.isfile(ssh_config.ssh_key):
                    self.pKeyConnect(ssh_config)
            else:
                self.passConnect(ssh_config)
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
                self.result.error_code = ErrorCode.failed
                self.result.error_msg = err_msg
        else:
            self.client.connect(
                hostname=ssh_config.ssh_host,
                port=ssh_config.ssh_port,
                username=ssh_config.ssh_user,
                pkey=pKey
            )

    def passConnect(self, ssh_config):
        self.client.connect(
            hostname=ssh_config.ssh_host,
            port=ssh_config.ssh_port,
            username=ssh_config.ssh_user,
            password=ssh_config.ssh_password
        )

    def run(self, module):
        import_mod = 'import Libs.{} as mod'.format(module.get('name'))
        try:
            exec import_mod
        except ImportError:
            raise ModuleNotFound
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
        self.result.return_code = stdout.channel.recv_exit_status()
        self.result.module = module
        if self.result.return_code == 0:
            self.result.lines = [line.rstrip('\r\n') for line in stdout.readlines()]
            if self.parser:
                self.result.data = self.parser(self.result.lines).format2json()
        else:
            self.result.lines = [line.rstrip('\r\n') for line in stderr.readlines()]
        self.client.close()
        return self.result

if __name__ == '__main__':
    import sys
    sys.path.append(path.join(path.dirname(sys.argv[0]), '../'))
    conf = SSHConfig('192.168.101.100', 'qdam', 'qdam')
    executor = Executor(conf)
    result = executor.run(
        {
            'name': 'psaux',
            'args': {
                'processes': ['qicegateway'],
                'param': [1]
            }
        }
    )
    #print result.lines
    print result.data
