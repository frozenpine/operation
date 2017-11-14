# -*- coding: UTF-8 -*-

from listParser import OutputParser


class cyg_netstatParser(OutputParser):
    def __init__(self, output_lines):
        OutputParser.__init__(
            self,
            output_lines=output_lines,
            re_str=r'\s*(.+?)\s+([^:]+|.*:.*:.*):(.+?)\s+([^:]+|.*:.*:.*):(.+?)\s+(.+?)\s+(.+)$',
            key_list=[
                'proto', 'local_ip', 'local_port',
                'remote_ip', 'remote_port', 'state', 'pid'
            ],
            primary_key='state',
            skip_headline=False
        )
