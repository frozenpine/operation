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
    task[0] = curr[0]
    task[1] = curr[1]
    task[2] = curr[2]
    curr = map(lambda x: int(x), curr)
    task = map(lambda x: int(x), task)
    curr = datetime.datetime(*tuple(curr))
    task = datetime.datetime(*tuple(task))
    return (task - curr).seconds


# 比较时间戳先后顺序
def compare_timestamps(queue, task):
    """
    :return 1 立即执行
            2 等待时间
    """
    # 处理curr_timestamp
    curr = current_ymd_hms()
    curr_info = curr.split("-")[0].split("/") + curr.split("-")[1].split(":")
    # 处理timestamp1
    queue_info = queue.split("-")[0].split("/") + queue.split("-")[1].split(":")
    # 处理timestamp2
    task_info = ["", "", ""] + task.split(":")
    if len(task_info) == 5:
        task_info.append("00")
    # 均获取最后三位
    curr_temp = "".join(curr_info[-3:])
    queue_temp = "".join(queue_info[-3:])
    task_temp = "".join(task_info[-3:])
    if curr_temp < queue_temp < task_temp:
        # 当前12 队列13 任务14
        return 1, None
    if curr_temp < task_temp < queue_temp:
        # 当前12 任务13 队列14 等待task-curr
        return 2, calc_diff(curr_info, task_info)
    if queue_temp < curr_temp < task_temp:
        # 队列12 当前13 任务14 等待task-curr
        return 2, calc_diff(curr_info, task_info)
    if queue_temp < task_temp < curr_temp:
        # 队列12 任务13 当前14
        return 1, None
    if task_temp < curr_temp < queue_temp:
        # 任务12 当前13 队列14
        return 1, None
    if task_temp < queue_temp < curr_temp:
        # 任务12 队列13 当前14 等待task+24-curr
        return 2, calc_diff(curr_info, task_info) + 86400


if __name__ == "__main__":
    print compare_timestamps("2017/08/01-16:00:00", "18:00")
