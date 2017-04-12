# -*- coding: UTF-8 -*-
import shell

def run(client, module):
    args = module.get('args')
    if args:
        if args.has_key('users'):
            userlist = args.get('users')[0]
            for usr in args.get('users')[1:]:
                userlist += "|{}".format(usr)
        else:
            userlist = ""
        if args.has_key('processes'):
            proclist = args.get('processes')[0]
            for proc in args.get('processes')[1:]:
                proclist += "|{}".format(proc)
        else:
            proclist = ""
        mod = {
            'shell': "ps aux | awk 'FNR==1{{print;next}}$1 ~/{0}/ && $11 ~/{1}/{{print}}'"\
                .format(userlist, proclist)
        }
    else:
        mod = {
            'shell': "ps aux"
        }
    return shell.run(client, mod)
