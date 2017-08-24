# coding=utf-8

import platform
import re
import subprocess
import time


def linux_stat():
    """
    linux下获取cpu信息
    :return:
    """
    linux_pattern = re.compile("cpu\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)")
    with open("/proc/stat") as f:
        f_stream = f.read()
    stat_list = f_stream.split("\n")
    stat_stream = stat_list[0]
    m = re.match(linux_pattern, stat_stream)
    key_list = ["user", "nice", "system", "idle", "irq", "iowait", "softirq", "stealstolen", "guest"]
    value_list = map(lambda x: float(x), m.groups())
    temp = dict(zip(key_list, value_list))
    return temp


def cygwin_stat():
    """
    cygwin下获取cpu信息
    :return:
    """
    p = subprocess.Popen('typeperf "\Processor(_Total)\% Idle Time" "\Processor(_Total)\% '
                         'Interrupt Time" "\Processor(_Total)\% User Time" "\Processor(_Total)\% '
                         'Privileged Time" "\Processor(_Total)\% Processor Time" "\Processor(_Total)\% '
                         'DPC Time" -si 1 -sc 1', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = p.communicate()
    stat_list = stdout.split("\r\n")
    value_list = stat_list[2][1:]
    key_list = ["idle", "irq", "user", "nice", "system"]
    result = dict(zip(key_list, value_list[: -1]))
    return result


def stat():
    if platform.system() == "Linux":
        first_record = linux_stat()
        first_sum = sum(first_record.values())
        time.sleep(1)
        second_record = linux_stat()
        second_sum = sum(second_record.values())
        result = dict()
        for k in first_record.keys():
            result.update({k: float(second_record[k] - first_record[k])})
        for k in result.keys():
            result.update({k: result[k] / (second_sum - first_sum)})
    else:
        result = cygwin_stat()
    return result


if __name__ == "__main__":
    stat()
