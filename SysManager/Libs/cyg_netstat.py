# -*- coding: UTF-8 -*-
import shell


def run(client, module):
    protocol = module.get('netstat', 'tcp').lower()
    args = module.get('args')
    if args:
        if args.has_key('ports'):
            port_list = reduce(
                lambda x, y: u':{}' + unicode(x) + u'|' + u':{}' + unicode(y),
                args['ports']
            )
            if isinstance(port_list, int):
                port_list = unicode(port_list)
        else:
            port_list = ''
        mod = {
            'shell': (
                r"""netstat -anobp {proto} | grep -iv time_wait | sed -n '5,$s/^ *//gp' | """
                r"""awk '$0 ~/{ports}/ {{print}}'"""
            ).format(
                proto=protocol,
                ports=port_list
            )
        }
    else:
        mod = {
            'shell': (
                r"""netstat -anop {proto} | grep -iv time_wait | sed -n '5,$s/^ *//p'"""
            ).format(proto=protocol)
        }
    return shell.run(client, mod)
