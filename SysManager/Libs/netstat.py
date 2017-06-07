# -*- coding: UTF-8 -*-
import shell

def run(client, module):
    args = module.get('args')
    if args:
        if args.has_key('processes'):
            process_list = args['processes'][0]
            for proc in args['processes'][1:]:
                process_list += '|{}'.format(proc)
        else:
            process_list = ''
        if args.has_key('ports'):
            port_list = ':{}'.format(args['ports'][0])
            for port in args['ports'][1:]:
                port_list += '|:{}'.format(port)
        else:
            port_list = ''
        mod = {
            'shell': """netstat -tanp | sed 1,2d | \
                awk '$4 ~/{0}/ && \
                $7 ~/{1}/ && $7 !~/^-/\
                {{print}}'""".format(
                    port_list,
                    process_list
                )
        }
    else:
        mod = {
            'shell': """netstat -tanp | sed 1,2d | awk '$7 !~/^-/{print}'"""
        }
    return shell.run(client, mod)
