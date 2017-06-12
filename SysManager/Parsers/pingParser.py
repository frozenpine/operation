# -*- coding: UTF-8 -*-
import json
import re


class OutputParser(object):
    def __init__(self, output_lines):
        self.output_list = OutputParser.chunk(output_lines.split("\n"), 3)
        self.pattern1 = re.compile(r"ping to (.+) count (\d+)")
        self.pattern2 = re.compile(
            r"(\d+) packets transmitted, (\d+) received, (\d+%) packet loss, time (\d+)ms"
        )
        self.pattern3 = re.compile(
            r"rtt min/avg/max/mdev = (\d+.\d+)/(\d+.\d+)/(\d+.\d+)/(\d+.\d+) ms"
        )
        self.result_list = []

    @staticmethod
    def chunk(l, n):
        # 按数量分割列表
        n = max(1, n)
        return [l[i:i + n] for i in range(0, len(l), n)]

    def format2json(self):
        # 格式化为json
        for each in self.output_list:
            self.process(each)
        return json.dumps(self.result_list)

    def process(self, each):
        # 处理每3行组成的列表
        first_line, second_line, third_line = each[0], each[1], each[2]
        # 处理第一行
        temp1 = re.findall(self.pattern1, first_line)[0]
        hostname, count = temp1[0], temp1[1]
        # 处理第二行
        temp2 = re.findall(self.pattern2, second_line)[0]
        received, loss, time = temp2[1], temp2[2], temp2[3]
        # 处理第三行
        if third_line != "":
            temp3 = re.findall(self.pattern3, third_line)[0]
            min, avg, max, mdev = temp3[0], temp3[1], temp3[2], temp3[3]
            self.result_list.append({
                hostname: {
                    "count": count,
                    "reveiced": received,
                    "loss": loss,
                    "time": time,
                    "min": min,
                    "avg": avg,
                    "max": max,
                    "mdev": mdev
                }
            })
        else:
            self.result_list.append({
                hostname: {
                    "count": count,
                    "reveiced": received,
                    "loss": loss,
                    "time": time
                }
            })
