# coding=utf-8

from enum import Enum


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
