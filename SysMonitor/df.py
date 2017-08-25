# coding=utf-8

import re
import subprocess


def df():
    pattern = re.compile(".+\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+%)\s+(.+)")
    p = subprocess.Popen("df -k", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = p.communicate()
    df_list = stdout.splitlines()
    df_list = filter(lambda x: re.match(pattern, x), df_list)
    result = dict()
    for each in df_list:
        m = re.match(pattern, each)
        temp = dict()
        temp.update(
            {"1K-blocks": float(m.groups()[0]),
             "Used": float(m.groups()[1]),
             "Available": float(m.groups()[2]),
             "Use%": m.groups()[3], })
        result.update({m.groups()[-1]: temp})
    return result


if __name__ == "__main__":
    df()
