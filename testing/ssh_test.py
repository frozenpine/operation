# -*- coding: UTF-8 -*-
import sys
from os import path

sys.path.append(path.join(path.dirname(sys.argv[0]), '../'))

from SysManager.configs import RemoteConfig, SSHConfig, WinRmConfig
from SysManager.executor import Executor


if __name__ == '__main__':
    conf = SSHConfig('192.168.92.121', 'root', 'quantdo123456')
    # conf = SSHConfig('192.168.92.26', 'root', 'quantdo123456')
    exe = Executor.Create(conf)
    mod = {
        'name': 'customLog',
        'customLog': '/var/log/messages',
        'key_words': {
            'warning': 'level=warning',
            'error': 'level=error'
        }
    }

    exe = Executor.Create(conf)

    result = exe.run(mod)
    print result.return_code
    for line in result.lines:
        print line
    print result.data
