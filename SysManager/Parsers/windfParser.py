# -*- coding: UTF-8 -*-

from listParser import OutputParser


class windfParser(OutputParser):
    def __init__(self, output_lines):
        OutputParser.__init__(
            self,
            output_lines=output_lines,
            re_str=
            r'(.+?)\s+(\d+)\s+(\d+)$',
            key_list=[
                'mount', 'total', 'available'
            ]
        )
