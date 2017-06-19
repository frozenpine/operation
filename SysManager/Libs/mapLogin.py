# -*- coding: UTF-8 -*-
import grep

def run(client, module):
    dest = module.get('mapLogin')
    mod = {
        'grep': dest,
        'args': {
            'pattern': 'OnConnected|OnRspUserLogin|OnDisConnected'
        }
    }
    return grep.run(client, mod)
