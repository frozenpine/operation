# -*- coding: UTF-8 -*-
import grep


def run(client, module):
    dest = module.get('uftLogin')
    if dest:
        mod = {
            'grep': dest,
            'args': {
                'pattern': 'InitUftApi|HsUftLogin 5 Login rtn'
            }
        }
        return grep.run(client, mod)
