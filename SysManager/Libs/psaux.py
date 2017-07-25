# -*- coding: UTF-8 -*-
import shell

def run(client, module):
    args = module.get('args')
    if args:
        if args.has_key('users'):
            userlist = reduce(lambda x, y: x + '|' + y, args['users'])
        else:
            userlist = ""
        if args.has_key('processes'):
            proclist = reduce(lambda x, y: x + '|' + y, args['processes'])
        else:
            proclist = ""
        mod = {
            'shell': "ps aux | awk 'FNR==1{{print;next}}$1 ~/{0}/ && $11 !~/bash|awk|sed|vim?|nano/ && $0 ~/{1}/{{print}}'"\
                .format(userlist, proclist)
        }
    else:
        mod = {
            'shell': "ps aux"
        }
    return shell.run(client, mod)
