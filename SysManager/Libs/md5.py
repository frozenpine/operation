# -*- coding: UTF-8 -*-
import shell


def run(client, module):
    args = module.get('args')
    if args:
        directory = args.get('dir')
        file_name = args.get('file')
        mod = {
            "shell": "openssl md5 {file} | cut -d' ' -f2".format(file=file_name),
            'args': {
                'chdir': directory
            }
        }
        return shell.run(client, mod)
