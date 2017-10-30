# -*- coding: UTF-8 -*-
from paramiko import SSHClient

def run(client, module):
    dest = module.get('quantdoLogin')
    if isinstance(client, SSHClient):
        import grep
    else:
        import wingrep as grep
    mod = {
        'grep': dest,
        'args': {
            'pattern': 'OnFrontConnected|OnRspUserLogin|OnFrontDisConnected'
        }
    }
    return grep.run(client, mod)
