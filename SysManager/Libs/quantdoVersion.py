# -*- coding: UTF-8 -*-
import shell

def run(client, module):
    args = module.get('args')
    if args:
        directiory = args.get('dir')
        file_name = args.get('file')
        mod = {
            "shell": "{exe} -v".format(exe=file_name),
            'args': {
                'chdir': directiory
            }
        }
        return shell.run(client, mod)
