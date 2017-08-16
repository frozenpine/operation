# -*- coding: UTF-8 -*-

from listParser import OutputParser


class quantdoLoginParser(OutputParser):
    def __init__(self, output_lines, **kwargs):
        OutputParser.__init__(
            self,
            output_lines=output_lines,
            re_str=
            ur'^.*(?:OnFrontConnected|OnRspUserLogin|OnFrontDisConnected) \d (.*席位\[(\d+)\].*)$',
            key_list=[
                'message', 'seatid'
            ],
            primary_key='seatid',
            skip_headline=False
        )
