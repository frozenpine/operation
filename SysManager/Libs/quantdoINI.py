# -*- coding: UTF-8 -*-
import shell

def run(client, module):
    dest = module.get('quantdoINI')
    if dest:
        mod = {
            'shell': (
                "sed 's/#.+$//g' {filename}"
            ).format(filename=dest)
        }
        shell.run(client, mod)
