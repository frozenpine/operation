# coding=utf-8

from enum import Enum

msg_dict = {-1: u"队列初始化失败",
            -11: u"队列为空",
            -12: u"队列不存在",
            -13: u"队列失败不可恢复",
            -14: u'队列已过期',
            0: u"正常调度",
            11: u"任务已下发",
            12: u"任务执行中",
            13: u"任务等待中",
            14: u"任务失败"}


class MsgInfo(Enum):
    InitFailed = -1
    QueueEmpty = -11
    QueueNotExits = -12
    QueueFailNotRecoverable = -13
    OK = 0
    JobIssued = 11
    JobRunning = 12
    JobWaiting = 13
    JobFailed = 14
