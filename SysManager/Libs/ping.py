# -*- coding: UTF-8 -*-
import shell


def run(client, module):
    args = module.get('args')
    if args:
        if args.has_key('count'):
            count = args.get('count')
        else:
            count = 3
        if args.has_key('dest'):
            iplist = args.get('dest')[0]
            for ip in args.get('dest')[1:]:
                iplist += " {}".format(ip)
            mod = {
                'shell': """
                for ip in {0}; do
                    echo "ping to $ip count {1}:"
                    ping -c {1} $ip | tail -n 2
                done
                """.format(iplist, count)
            }
        else:
            mod = {'shell': 'echo pong!'}
    else:
        mod = {'shell': 'echo pong!'}
    return shell.run(client, mod)
