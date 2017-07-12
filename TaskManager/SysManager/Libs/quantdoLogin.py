# -*- coding: UTF-8 -*-
import grep

def run(client, module):
    dest = module.get('quantdoLogin')
    mod = {
        'grep': dest,
        'args': {
            'pattern': 'OnFrontConnected|OnRspUserLogin|OnFrontDisConnected'
        }
    }
    return grep.run(client, mod)
