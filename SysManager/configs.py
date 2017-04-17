# -*- coding: UTF-8 -*-
import sys
import os
import ConfigParser
from enum import Enum
from SysManager import logging
from SysManager.excepts import ConfigInvalid

class GlobalConfig:
    default_ssh_user = None
    default_ssh_key = None

    def __init__(self):
        global_file = os.path.join(
            os.path.dirname(sys.argv[0]),
            'Conf',
            'Global.ini'
        )
        if os.path.exists(global_file):
            ini = ConfigParser.ConfigParser()
            ini.read(global_file)
            for key in [x for x in dir(self) if not x.startswith('_')]:
                try:
                    setattr(self, key, ini.get('Global', key))
                except ConfigParser.NoSectionError:
                    logging.warning(
                        'No section[Global] in INI file({})'\
                            .format(global_file)
                    )
                    break
                except ConfigParser.NoOptionError:
                    continue

class SSHConfig:
    def __init__(self, ip, user, password=None, port=22, pKey=None, key_pass=None):
        if not password and not pKey:
            raise ConfigInvalid('Either "password" or "pKey" must be specified.')
        self.ssh_host = ip
        self.ssh_port = port
        self.ssh_user = user
        self.ssh_password = password
        self.ssh_key = pKey
        self.ssh_key_pass = key_pass

class ErrorCode(Enum):
    timeout = -2,
    invalid_login = -1,
    succeed = 0,
    failed = 1

class Result:
    destination = None
    module = None
    return_code = 0
    error_code = ErrorCode.succeed
    error_msg = ""
    data = {}
    lines = []

if __name__ == '__main__':
    conf = GlobalConfig()
    print conf.__dict__
