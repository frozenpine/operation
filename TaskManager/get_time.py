# coding=utf-8

import datetime
import time


# 获取当前时间戳
def current_timestamp():
    return time.time()


# 获取当前年月日
def current_ymd():
    return time.strftime("%Y%m%d")


# 获取当前年月日-时分秒
def current_ymd_hms():
    return time.strftime("%Y/%m/%d-%H:%M:%S")


# 计算两个hhmmss的差值
def calc_diff(curr, task):
    task[0], task[1], task[2] = curr[0], curr[1], curr[2]
    curr = map(lambda x: int(x), curr)
    task = map(lambda x: int(x), task)
    curr = datetime.datetime(*tuple(curr))
    task = datetime.datetime(*tuple(task))
    return (task - curr).seconds


def next_second(time_temp):
    h = int(time_temp[0: 2])
    m = int(time_temp[2: 4])
    s = int(time_temp[4: 6])
    s = s + 1
    if s == 60:
        s = 0
        m = m + 1
    if m == 60:
        m = 0
        h = h + 1
    if h == 24:
        h = 0
    return "{:0>2d}{:0>2d}{:0>2d}".format(h, m, s)


def last_second(time_temp):
    h = int(time_temp[0: 2])
    m = int(time_temp[2: 4])
    s = int(time_temp[4: 6])
    s = s - 1
    if s == -1:
        s = 59
        m = m - 1
    if m == -1:
        m = 59
        h = h - 1
    if h == -1:
        h = 23
    return "{:0>2d}{:0>2d}{:0>2d}".format(h, m, s)


# 比较时间戳先后顺序
def compare_timestamps(queue, earliest, latest):
    """
    :return 1 立即执行
            2 等待时间
            3 不能执行
    """
    if not earliest and latest:
        # 当前时间
        curr = current_ymd_hms()
        curr_info = ["1970", "01", "01"] + curr.split("-")[1].split(":")
        # 队列时间
        queue_info = ["1970", "01", "01"] + queue.split("-")[1].split(":")
        # 任务最早时间
        earliest_info = queue_info
        # 任务最晚时间
        latest_info = ["1970", "01", "01"] + latest.split(":")
        if len(latest_info) == 5:
            latest_info.append("00")
        # 均获取最后三位
        curr_temp = "".join(curr_info[-3:])
        queue_temp = "".join(queue_info[-3:])
        earliest_temp = next_second(queue_temp)
        latest_temp = "".join(latest_info[-3:])
    elif not latest and earliest:
        # 当前时间
        curr = current_ymd_hms()
        curr_info = ["1970", "01", "01"] + curr.split("-")[1].split(":")
        # 队列时间
        queue_info = ["1970", "01", "01"] + queue.split("-")[1].split(":")
        # 任务最早时间
        earliest_info = ["1970", "01", "01"] + earliest.split(":")
        if len(earliest_info) == 5:
            earliest_info.append("00")
        # 均获取最后三位
        curr_temp = "".join(curr_info[-3:])
        queue_temp = "".join(queue_info[-3:])
        earliest_temp = "".join(earliest_info[-3:])
        latest_temp = last_second(queue_temp)
    else:
        # 当前时间
        curr = current_ymd_hms()
        curr_info = ["1970", "01", "01"] + curr.split("-")[1].split(":")
        # 队列时间
        queue_info = ["1970", "01", "01"] + queue.split("-")[1].split(":")
        # 任务最早时间
        earliest_info = ["1970", "01", "01"] + earliest.split(":")
        # 任务最晚时间
        latest_info = ["1970", "01", "01"] + latest.split(":")
        if len(earliest_info) == 5:
            earliest_info.append("00")
        if len(latest_info) == 5:
            latest_info.append("00")
        # 均获取最后三位
        curr_temp = "".join(curr_info[-3:])
        queue_temp = "".join(queue_info[-3:])
        earliest_temp = "".join(earliest_info[-3:])
        latest_temp = "".join(latest_info[-3:])
    if curr_temp <= queue_temp <= earliest_temp:
        # 当前12 队列13 任务开始14
        # 任务结束15 不能执行
        if latest_temp > queue_temp:
            return 3, None
        # 任务结束12.5 立即执行
        if latest_temp <= queue_temp:
            return 1, None
    if curr_temp <= earliest_temp <= queue_temp:
        # 当前12 任务开始13 队列14 等待task-curr
        return 2, calc_diff(curr_info, earliest_info)
    if queue_temp <= curr_temp <= earliest_temp:
        # 队列12 当前13 任务开始14 等待task-curr
        return 2, calc_diff(curr_info, earliest_info)
    if queue_temp <= earliest_temp <= curr_temp:
        # 队列12 任务开始13 当前14
        # 任务结束13.5 不能执行
        if latest_temp < curr_temp:
            return 3, None
        # 任务结束15 立即执行
        if latest_temp >= curr_temp:
            return 1, None
    if earliest_temp <= curr_temp <= queue_temp:
        # 任务开始12 当前13 队列14
        # 任务结束12.5 不能执行
        if latest_temp < curr_temp:
            return 3, None
        # 任务结束13.5 立即执行
        if latest_temp >= curr_temp:
            return 1, None
    if earliest_temp <= queue_temp <= curr_temp:
        # 任务开始12 队列13 当前14 等待task+24-curr
        return 2, calc_diff(curr_info, earliest_info) + 86400


if __name__ == "__main__":
    print compare_timestamps("2017/08/01-13:00:00", "", "11:00")
    print compare_timestamps("2017/08/01-13:00:00", "", "15:00")
    print compare_timestamps("2017/08/01-13:00:00", "11:00", "")
    print compare_timestamps("2017/08/01-13:00:00", "15:00", "")
    print compare_timestamps("2017/08/01-13:00:00", "11:00", "12:00")
    print compare_timestamps("2017/08/01-13:00:00", "14:00", "15:00")
