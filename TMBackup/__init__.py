# coding=utf-8

import logging
import os
from logging.handlers import TimedRotatingFileHandler

from enum import Enum


class QueueStatus(Enum):
    InitFail = -1
    Empty = -11
    Missing = -12
    NotRecoverable = -13
    Expired = -14
    Dispatchable = 0
    DispatchedBlock = 11
    RunningBlock = 12
    WaitingBlock = 13
    FailBlock = 14

    @property
    def IsExcepted(self):
        return self in [QueueStatus.InitFail]

    @property
    def IsUnavailable(self):
        return self in [QueueStatus.Empty, QueueStatus.Missing, QueueStatus.NotRecoverable]

    @property
    def IsAvailable(self):
        return self in [QueueStatus.Dispatchable] or self.IsBlocked

    @property
    def IsBlocked(self):
        return self in [
            QueueStatus.DispatchedBlock, QueueStatus.RunningBlock,
            QueueStatus.WaitingBlock, QueueStatus.FailBlock
        ]


class TaskStatus(Enum):
    InitFail = -1
    Runnable = 100
    TriggerTimeWaiting = 111
    WorkerWaiting = 112
    TimeRangeExcept = 121
    Running = 200
    Success = 0
    Failed = 1
    Timeout = 2
    Terminated = 3
    Skipped = 4

    @property
    def IsExcepted(self):
        return self in [TaskStatus.InitFail, TaskStatus.TimeRangeExcept]

    @property
    def IsInited(self):
        return self in [TaskStatus.Runnable] or self.Waiting

    @property
    def IsWaiting(self):
        return self in [TaskStatus.TriggerTimeWaiting, TaskStatus.WorkerWaiting]

    @property
    def IsDone(self):
        return self in [TaskStatus.Success, TaskStatus.Failed] or self.IsTimeout

    @property
    def IsTimeout(self):
        return self in [TaskStatus.Timeout, TaskStatus.Terminated]


tm_logger = logging.getLogger('tm')
tm_logger.setLevel(logging.INFO)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(filename)s-%(funcName)s[line:%(lineno)d] %(levelname)s %(message)s')
console.setFormatter(formatter)
tm_logger.addHandler(console)

Rthandler = TimedRotatingFileHandler(
    os.path.join(os.path.dirname(__file__), '../Logs/tmSyslog.log'),
    when='midnight',
    interval=1,
    backupCount=15,
    encoding='utf-8'
)
Rthandler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s %(filename)s-%(funcName)s[line:%(lineno)d] %(levelname)s %(message)s'
)
Rthandler.setFormatter(formatter)
tm_logger.addHandler(Rthandler)
