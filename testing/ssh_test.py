# -*- coding: UTF-8 -*-
import sys
from os import path

sys.path.append(path.join(path.dirname(sys.argv[0]), '../'))

from SysManager.configs import RemoteConfig, SSHConfig, WinRmConfig
from SysManager.executor import Executor


if __name__ == '__main__':
    # conf = SSHConfig('192.168.92.121', 'root', 'quantdo123456')
    # conf = SSHConfig('192.168.92.26', 'root', 'quantdo123456')
    conf = SSHConfig('192.168.56.2', 'Administrator', '022010blue@safe')
    exe = Executor.Create(conf)

    mod = {
        'name': 'cyg_netstat',
        'args': {
            'ports': [19200, 19300]
        }
    }

    result = exe.run(mod)
    print result.return_code
    for line in result.lines:
        print line
    print result.data
