# -*- coding: UTF-8 -*-
import shell


def run(client, module):
    protocol = module.get('netstat', 'tcp').lower()
    args = module.get('args')
    if args:
        if args.has_key('processes'):
            ''' process_list = args['processes'][0]
            for proc in args['processes'][1:]:
                process_list += '|{}'.format(proc) '''
            process_list = reduce(lambda x, y: x[0] + '|' + y[0],
                                  args['processes'])
        else:
            process_list = ''
        if args.has_key('ports'):
            ''' port_list = ':{}'.format(args['ports'][0])
            for port in args['ports'][1:]:
                port_list += '|:{}'.format(port) '''
            port_list = reduce(lambda x, y: unicode(x) + u'|' + unicode(y), args['ports'])
        else:
            port_list = ''
        mod = {
            'shell': (
                r"netstat -anobp {proto} | grep -iv time_wait | "
                r"sed -n '5,${{:read;{{/\[.*\]/!{{/information/!{{N;b read}}}}}};s#\r\n *#/#g;s/^ *//g;p}}' | "
                r"grep -iv 'ownership information' | "
                r"awk '$0 ~/{ports}/ && $NF ~/{procs}/ {{print}}'"
            ).format(
                proto=protocol,
                ports=port_list,
                procs=process_list
            )
        }
    else:
        mod = {
            'shell': (
                r"netstat -anobp {proto} | grep -iv time_wait | "
                r"sed -n '5,${{:read;{{/\[.*\]/!{{/information/!{{N;b read}}}}}};s#\r\n *#/#g;s/^ *//g;p}}' | "
                r"grep -iv 'ownership information'"
            ).format(proto=protocol)
        }
    return shell.run(client, mod)
