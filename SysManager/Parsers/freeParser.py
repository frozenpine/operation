# -*- coding: UTF-8 -*-

from listParser import OutputParser


class freeParser(OutputParser):
    def __init__(self, output_lines):
        OutputParser.__init__(
            self,
            output_lines=output_lines,
            re_str=
            r'(.+?)\s+(.+?)\s+(.+)$',
            key_list=[
                'name', 'total', 'free'
            ],
            primary_key='name'
        )
