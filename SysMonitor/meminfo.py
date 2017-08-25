# coding=utf-8

import re


def mem_info():
    # 获取swap和mem信息
    pattern = re.compile("swap|mem", re.IGNORECASE)
    result = dict()
    with open("/proc/meminfo") as f:
        f_stream = f.read()
    mem_info_list = f_stream.splitlines()
    mem_info_list = filter(lambda x: re.match(pattern, x), mem_info_list)
    map(lambda x: result.update({x.replace(" ", "").split(":")[0]: x.replace(" ", "").split(":")[1]}), mem_info_list)
    return result


if __name__ == "__main__":
    mem_info()
