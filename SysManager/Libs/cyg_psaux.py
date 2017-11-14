# -*- coding: UTF-8 -*-
import shell


def run(client, module):
    args = module.get('args')
    if args:
        if 'processes' in args.keys():
            exe_list, param_list = zip(*args['processes'])
            proc_list = '|'.join(map(lambda x, y: x + '.*' + y + '.*', exe_list, param_list))
        else:
            proc_list = ""
        mod = {
            'shell': (
                r"""ps -a | sed '1s/^/STAT &/; 2,$s/^/R &/' | """
                r"""awk 'FNR==1{{print;next}}"""
                r"""$9 !~/bash|awk|sed|vim?|nano/ && $0 ~/{0}/{{print}}'"""
            ).format(proc_list)
        }
    else:
        mod = {
            'shell': r"""ps -a | sed '1s/^/STAT &/; 2,$s/^/R &/'"""
        }
    return shell.run(client, mod)
