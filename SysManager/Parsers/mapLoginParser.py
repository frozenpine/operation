# -*- coding: UTF-8 -*-

from listParser import OutputParser


class mapLoginParser(OutputParser):
    def __init__(self, output_lines):
        OutputParser.__init__(
            self,
            output_lines=output_lines,
            re_str=
            r'^(.+us).+event\s[a-zA-Z]+\s\d+\s([^[]+\[(?:CustCode:)?(\d+).*\].*)',
            key_list=[
                'timestamp', 'message', 'seatid'
            ],
            primary_key='seatid',
            skip_headline=False
        )
