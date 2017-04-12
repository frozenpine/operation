# -*- coding: UTF-8 -*-

def run(client, module):
    command = module.get('shell')
    args = module.get('args')
    if args:
        base_dir = args.get('chdir')
        if base_dir:
            command = 'cd "{}";{}'.format(base_dir, command)
    return client.exec_command(command)
