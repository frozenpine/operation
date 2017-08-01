# -*- coding: UTF-8 -*-
import shell


def run(client, module):
    protocol = module.get('netstat', 'tcp').lower()[0]
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
            'shell': """\
netstat -{proto}anp | \
awk '
    $0 ~/{ports}/ && $NF ~/{procs}/ && $NF !~/^-/ {{print}}
'
                """.format(
                proto=protocol,
                ports=port_list,
                procs=process_list
            )
        }
    else:
        mod = {
            'shell': """\
netstat -{}anp | awk '$NF !~/^-/{{print}}'
                """.format(protocol)
        }
    return shell.run(client, mod)
