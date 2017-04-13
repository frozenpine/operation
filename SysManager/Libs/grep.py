# -*- coding: UTF-8 -*-
import shell

def run(client, module):
    dest = module.get('grep')
    args = module.get('args')
    if args:
        pattern = args.get('pattern')
        ignoreCase = args.get('ignore_case')
