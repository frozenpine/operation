# -*- coding: UTF-8 -*-

from listParser import OutputParser


class dfParser(OutputParser):
    def __init__(self, output_lines):
        OutputParser.__init__(
            self,
            output_lines=output_lines,
            re_str=
            r'(.+?)\s+(\d+)\s+(\d+)\s+(\d+)\s+(.+%)$',
            key_list=[
                'mount', 'total', 'used', 'available', 'percent'
            ]
        )
