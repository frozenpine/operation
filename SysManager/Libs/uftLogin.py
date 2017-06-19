# -*- coding: UTF-8 -*-
import grep

def run(client, module):
    dest = module.get('uftLogin')
    mod = {
        'grep': dest,
        'args': {
            'pattern': 'InitSeatInfo|HsUftLogin 5 Login rtn'
        }
    }
    return grep.run(client, mod)
