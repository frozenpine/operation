# coding=utf-8

import time


# 获取当前时间戳
def current_timestamp():
    return time.time()


# 获取当前年月日
def current_ymd():
    return time.strftime("%Y%m%d")


# 获取当前年月日-时分秒
def current_ymd_hms():
    return time.strftime("%Y%m%d-%H%M%S")
