# coding=utf-8

import re
import time

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


# 获取当前时间戳
def current_timestamp():
    return time.time()


# 获取当前年月日
def current_ymd():
    return time.strftime("%Y%m%d")


# 获取当前年月日-时分秒
def current_ymd_hms():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def format_datetime(create_time, earliest, latest):
    create_datetime = parse(create_time)
    current_datetime = parse(current_ymd_hms())
    pattern = re.compile(ur'([01]?\d|2[0-3]):[0-5]?\d(:[0-5]?\d)?')
    # 如果存在earliest时间
    if earliest and pattern.search(earliest):
        if create_datetime.hour >= 12 > int(earliest.split(":")[0]):
            temp = parse("{0}-{1}-{2}".format(
                create_datetime.year, create_datetime.month, create_datetime.day)) + relativedelta(days=1)
        else:
            temp = parse("{0}-{1}-{2}".format(create_datetime.year, create_datetime.month, create_datetime.day))
        earliest_datetime = parse("{0}-{1}-{2} {3}:{4}:{5}".format(
            temp.year, temp.month, temp.day, int(earliest.split(":")[0]),
            int(earliest.split(":")[1]), 0))
    else:
        earliest_datetime = None
    if latest and pattern.search(latest):
        if create_datetime.hour >= 12 > int(latest.split(":")[0]):
            temp = parse("{0}-{1}-{2}".format(
                create_datetime.year, create_datetime.month, create_datetime.day)) + relativedelta(days=1)
        else:
            temp = parse("{0}-{1}-{2}".format(create_datetime.year, create_datetime.month, create_datetime.day))
        latest_datetime = parse("{0}-{1}-{2} {3}:{4}:{5}".format(
            temp.year, temp.month, temp.day, int(latest.split(":")[0]),
            int(latest.split(":")[1]), 0))
    else:
        latest_datetime = None
    return create_datetime, current_datetime, earliest_datetime, latest_datetime


def compare_timestamps(create_time, earliest, latest):
    create_datetime, current_datetime, earliest_datetime, latest_datetime \
        = format_datetime(create_time, earliest, latest)
    if not earliest_datetime and not latest_datetime:
        return 1, None
    if not earliest_datetime and latest_datetime:
        if current_datetime <= latest_datetime:
            return 1, None
        else:
            return 3, None
    if earliest_datetime and not latest_datetime:
        if current_datetime >= earliest_datetime:
            return 1, None
        else:
            return 2, (earliest_datetime - current_datetime).seconds
    if earliest_datetime and latest_datetime:
        if earliest_datetime <= current_datetime <= latest_datetime:
            return 1, None
        elif current_datetime <= earliest_datetime <= latest_datetime:
            return 2, (earliest_datetime - current_datetime).seconds
        else:
            return 3, None

# if __name__ == "__main__":
#     # test case 1
#     create_time = "2017-01-01 22:00:00"
#     current_time = "2017-01-01 23:30:00"
#     earliest = "01:00"
#     latest = "02:00"
#     print compare_timestamps(create_time, earliest, latest)
#     # test case 2
#     create_time = "2017-01-01 01:00:00"
#     current_time = "2017-01-01 02:30:00"
#     earliest = "10:00"
#     latest = "11:00"
#     print compare_timestamps(create_time, earliest, latest)
#     # test case 3
#     create_time = "2017-01-01 22:00:00"
#     current_time = "2017-01-01 23:30:00"
#     earliest = ""
#     latest = ""
#     print compare_timestamps(create_time, earliest, latest)
#     # test case 4
#     create_time = "2017-01-01 01:00:00"
#     current_time = "2017-01-01 02:30:00"
#     earliest = ""
#     latest = ""
#     print compare_timestamps(create_time, earliest, latest)
#     # test case 5
#     create_time = "2017-01-01 22:00:00"
#     current_time = "2017-01-01 23:30:00"
#     earliest = "16:00"
#     latest = "17:00"
#     print compare_timestamps(create_time, earliest, latest)
