# -*- coding: UTF-8 -*-
import re
from listParser import OutputParser

class quantdoLoginParser(OutputParser):
    def __init__(self, output_lines):
        OutputParser.__init__(
            self,
            output_lines=output_lines,
            re_str=
            r'^(.+us) .+EXID:([^,]+),SeatID:([^,]+),.+席位\[(.+)\]登录(?:(成功).*TradeDate=\[([^]]+)\].*TradeTime=\[([^]]+)\].+|(失败).+)$',
            key_list=[
                'timestamp', 'exid', 'seatid', 'login', 'success', 'trade_date', 'trade_time', 'fail'
            ],
            primary_key='seatid',
            skip_headline=False
        )
