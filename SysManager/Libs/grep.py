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
            'shell': """
                grep{0} {1} {2} 
            """.format(param, pattern, dest)
        }
        stdin, stdout, stderr = shell.run(client, mod)
        stdout.read = change_read_encoding(stdout.read)
        stdout.readlines = change_readlines_encoding(stdout.read)
        stderr.read = change_read_encoding(stderr.read)
        stderr.readlines = change_readlines_encoding(stderr.read)
        return stdin, stdout, stderr

def change_read_encoding(func):
    def _read():
        encoding_list = ["gbk", "utf-8"]
        for each in encoding_list:
            try:
                return func().decode(each).encode('utf-8').replace('\r\n', '\n')
            except UnicodeDecodeError:
                pass
    return _read

def change_readlines_encoding(func):
    def _readlines():
        #return [line for line in func().split('\n') if line != ""]
        for line in func().split('\n'):
            if line != "":
                yield line
    return _readlines
