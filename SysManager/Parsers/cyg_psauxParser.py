# -*- coding: UTF-8 -*-

from listParser import OutputParser


class cyg_psauxParser(OutputParser):
    def __init__(self, output_lines):
        OutputParser.__init__(
            self, output_lines=output_lines,
            re_str=r'\s*(.+?)\s+(.+?)\s+(.+?)\s+[^\s]+\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+)$',
            key_list=[
                'stat', 'cyg_pid', 'cyg_ppid', 'pid', 'tty', 'uid', 'start', 'command'
            ]
        )
