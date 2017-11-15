# -*- coding: UTF-8 -*-
from SysManager.Libs import shell


def run(client, module):
    protocol = module.get('netstat', 'tcp').lower()
    args = module.get('args')
    if args:
        if 'ports' in args.keys():
            port_list = '|'.join(map(lambda x: isinstance(x, int) and u':' + unicode(x), args['ports']))
            if isinstance(port_list, int):
                port_list = unicode(port_list)
        else:
            port_list = ''
        mod = {
            'shell': (
                r"""netstat -anop {proto} | """
                r"""awk 'FNR > 3 && $0 ~/{ports}/ {{print}}'"""
            ).format(
                proto=protocol,
                ports=port_list
            )
        }
    else:
        mod = {
            'shell': (
                r"""netstat -anop {proto} | sed -n '4,$ p'"""
            ).format(proto=protocol)
        }
    return shell.run(client, mod)
