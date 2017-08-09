from enum import Enum


class QueueStatus(Enum):
    InitFail = -1
    Empty = -11
    Missing = -12
    NotRecoverable = -13
    Dispatchable = 0
    DispatchedBlock = 11
    RunningBlock = 12
    WaitingBlock = 13
    FailBlock = 14


class TaskStatus(Enum):
    InitFail = -1
    InQueue = 100
    TriggerTimeWaiting = 111
    WorkerWaiting = 112
    TimeRangeExcept = 121
    Running = 200
    Success = 0
    Failed = 1
    Timeout = 2
    Terminated = 3
    Skipped = 4
