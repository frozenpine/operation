# -*- coding: UTF-8 -*-
import shell


def run(client, module):
    mod = {
        'shell': (
            r"""cat /proc/meminfo | grep -i -E "mem|swap" | sed -n '/Free/!{N;s/\n//;p}' | """ +
            r"""awk 'BEGIN{print "Name Total Free"} """ +
            r"""{sub("Total:", "", $1);print tolower($1)" "$2" "$4}'| """ +
            r"""column -t"""
        )
    }
    return shell.run(client, mod)
