# -*- coding: UTF-8 -*-


class uptimeParser():
    def __init__(self, output_lines):
        self.output_lines = output_lines

    def format2json(self):
        return self.output_lines[0]
