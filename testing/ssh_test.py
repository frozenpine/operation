# -*- coding: UTF-8 -*-
import sys
from os import path

sys.path.append(path.join(path.dirname(sys.argv[0]), '../'))

from SysManager.configs import RemoteConfig, SSHConfig, WinRmConfig
from SysManager.executor import Executor


if __name__ == '__main__':
    conf = SSHConfig('192.168.101.163', 'Administrator', 'Quantdo123456')
    exe = Executor.Create(conf)
    mod = {
        'name': 'shell',
        'shell': 'which pwd'
    }
    ''' mod = {
        'name': 'windf',
    } '''
    ''' mod = {
        'name': 'quantdoLogin',
        'quantdoLogin': 'c:\\test\\Syslog.log'
    } '''

    exe = Executor.Create(conf)

    result = exe.run(mod)
    print result.return_code
    for line in result.lines:
        print line
    print result.data
