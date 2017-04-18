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
        if args.has_key('param') and len(args.get('param')) > 0:
            paramlist = args.get('param')[0] or ""
            for param in args.get('param')[1:]:
                paramlist += "|{}".format(param or "")
        else:
            paramlist = ""
        mod = {
            'shell': "ps aux | awk 'FNR==1{{print;next}}$1 ~/{0}/ && $11 ~/{1}/ && $12 ~/{2}/{{print}}'"\
                .format(userlist, proclist, paramlist)
        }
    else:
        mod = {
            'shell': "ps aux"
        }
    return shell.run(client, mod)
