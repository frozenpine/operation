# -*- coding: UTF-8 -*-
import grep

def run(client, module):
    dest = module.get('quantdoLogin')
    mod = {
        'grep': dest,
        'args': {
            'pattern': 'OnRspUserLogin'
        }
    }
    return grep.run(client, mod)
