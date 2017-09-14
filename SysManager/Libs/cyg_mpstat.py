# -*- coding: UTF-8 -*-
import shell


def run(client, module):
    mod = {
        'shell': (
            r"""typeperf "\Processor(_Total)\% Idle Time" """
            r""""\Processor(_Total)\% Interrupt Time" "\Processor(_Total)\% User Time" """
            r""""\Processor(_Total)\% Privileged Time" -si 1 -sc 1 | """
            r"""sed -n '3 s/"//gp' | awk -F, 'BEGIN{print"CPU %idle %irq %usr %sys"} """
            r"""{printf("all %.2f %.2f %.2f %.2f", $2, $3, $4, $5)}' | column -t"""
        )
    }
    return shell.run(client, mod)
