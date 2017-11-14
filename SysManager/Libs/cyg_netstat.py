# -*- coding: UTF-8 -*-
from SysManager.Libs import shell


def run(client, module):
    protocol = module.get('netstat', 'tcp').lower()
    args = module.get('args')
    if args:
        if 'ports' in args.keys():
            port_list = '|'.join(map(lambda x: isinstance(x, int) and unicode(x), args['ports']))
            if isinstance(port_list, int):
                port_list = unicode(port_list)
        else:
            port_list = ''
        mod = {
            'shell': (
                r"""netstat -anop {proto} | """
                r"""awk '$0 ~/{ports}/ {{print}}'"""
            ).format(
                proto=protocol,
                ports=port_list
            )
        }
    else:
        mod = {
            'shell': (
                r"""netstat -anop {proto}"""
            ).format(proto=protocol)
        }
    return shell.run(client, mod)
