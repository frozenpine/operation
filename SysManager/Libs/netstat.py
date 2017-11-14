# -*- coding: UTF-8 -*-
from SysManager.Libs import shell


def run(client, module):
    protocol = module.get('netstat', 'tcp').lower()[0]
    args = module.get('args')
    if args:
        if 'processes' in args.keys():
            process_list = '|'.join(zip(*args['processes'])[0])
        else:
            process_list = ''
        if 'ports' in args.keys():
            port_list = '|'.join(map(lambda x: isinstance(x, int) and unicode(x), args['ports']))
            if isinstance(port_list, int):
                port_list = unicode(port_list)
        else:
            port_list = ''
        mod = {
            'shell': (
                r"netstat -{proto}anp | "
                r"awk '$0 ~/{ports}/ && $NF ~/{procs}/ && $NF !~/^-/ {{print}}'"
            ).format(
                proto=protocol,
                ports=port_list,
                procs=process_list
            )
        }
    else:
        mod = {
            'shell': "netstat -{}anp | awk '$NF !~/^-/{{print}}'".format(protocol)
        }
    return shell.run(client, mod)
