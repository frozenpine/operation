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
            ''' proclist = reduce(
                lambda x, y: '{exe1} .*{param1}|{exe2} .*{param2}'\
                    .format(
                        exe1=x[0], param1=x[1],
                        exe2=y[0], param2=y[1]
                    ),
                args['processes']
            ) '''
            exe_list, param_list = zip(*args['processes'])
            proclist = reduce(
                lambda x, y: x + '|' + y,
                map(lambda x, y: x + '.*' + y + '.*', exe_list, param_list)
            )
        else:
            proclist = ""
        mod = {
            'shell': "ps aux | awk 'FNR==1{{print;next}}$1 ~/{0}/ && $11 !~/bash|awk|sed|vim?|nano/ && $0 ~/{1}/{{print}}'" \
                .format(userlist, proclist)
        }
    else:
        mod = {
            'shell': "ps aux"
        }
    return shell.run(client, mod)
