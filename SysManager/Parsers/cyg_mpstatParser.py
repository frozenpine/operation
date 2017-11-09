# -*- coding: UTF-8 -*-

from listParser import OutputParser


class cyg_mpstatParser(OutputParser):
    def __init__(self, output_lines):
        OutputParser.__init__(
            self,
            output_lines=output_lines,
            re_str=
            r'(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+)$',
            key_list=[
                'name', 'idle', 'irq', 'usr', 'sys'
            ]
        )
