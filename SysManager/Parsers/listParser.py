# -*- coding: UTF-8 -*-
import re

class OutputParser(object):
    def __init__(self, output_lines, re_str="", 
        key_list=None, primary_key=None, skip_headline=True):
        self.primary_key = primary_key
        self.skip_headline = skip_headline
        self.pattern = re.compile(re_str)
        if not key_list:
            self.key_list = []
        else:
            self.key_list = key_list
        if self.skip_headline:
            self.output_lines = output_lines[1:]
        else:
            self.output_lines = output_lines
        self.result_list = []
        self.result_dict = {}

    def format2json(self):
        # 格式化为json
        key_len = len(self.key_list)
        try:
            primary_position = self.key_list.index(self.primary_key)
        except Exception:
            primary_position = -1
        for each in self.output_lines:
            temp_dict = {}
            each_list = re.findall(self.pattern, each)[0]
            for i in range(0, key_len, 1):
                if i != primary_position:
                    temp_dict[self.key_list[i]] = each_list[i]
            if primary_position < 0:
                self.result_list.append(temp_dict)
            else:
                self.result_dict[each_list[primary_position]] = temp_dict
        if primary_position < 0:
            return self.result_list
        else:
            return self.result_dict
