# -*- coding: UTF-8 -*-
import re

from listParser import OutputParser


class quantdoLoginParser(OutputParser):
    def __init__(self, output_lines):
        OutputParser.__init__(
            self,
            output_lines=output_lines,
            re_str=
            r'^(.+us) .+EXID:([^,]+),SeatID:([^,]+),.+Main:\d+:(.+)$',
            key_list=[
                'timestamp', 'exid', 'seatid', 'message'
            ],
            primary_key='seatid',
            skip_headline=False
        )
