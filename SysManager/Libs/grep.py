# -*- coding: UTF-8 -*-
import shell
import re

def run(client, module):
    dest = module.get('grep')
    args = module.get('args')
    param = ""
    if args:
        pattern = args.get('pattern')
        if not pattern or pattern == '':
            pattern = '""'
        else:
            pattern = ' -E "{}"'.format(pattern)
        ignoreCase = args.get('ignore_case')
        if ignoreCase and re.match(r'[y|Y](es)?|[T|t]rue', ignoreCase):
            param += " -i"
        revers = args.get('reverse_match')
        if revers and re.match(r'[y|Y](es)?|[T|t]rue', revers):
            param += " -v"
        mod = {
            'shell': 'grep{0} {1} {2}'.format(param, pattern, dest)
        }
        return shell.run(client, mod)
