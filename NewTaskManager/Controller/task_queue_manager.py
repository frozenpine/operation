# coding=utf-8
""" Zero rpc server 4 TaskManager Controller
"""

import os
import threading
import json
import time
import random
from Queue import Queue

import zerorpc

from NewTaskManager.Controller import controller_logger as logging
from NewTaskManager.Common import get_time
from NewTaskManager.protocol import (MSG_DICT, JsonSerializable, QueueStatus,
                                     Task, TaskResult, TaskStatus)
from NewTaskManager.Controller.events import EventName
from NewTaskManager.Controller.excepts import QueueError


# class TaskQueueManager(threading.Thread):
class TaskQueueManager(object):
    def __init__(self, rpc_addr, rpc_port, msg_queue):
        # threading.Thread.__init__(self)
        self._msg_queue = msg_queue
        self._task_queues = {}
        self._entrypoint = zerorpc.Server(RPCHandler(self._task_queues, self._msg_queue))
        self._entrypoint.bind("tcp://{ip}:{port}".format(ip=rpc_addr, port=rpc_port))

    def run(self):
        self._entrypoint.run()

    def result_callback(self, event):
        logging.info('Event received: {} {}'.format(event.Name, event.Data.to_dict()))


def locker(func):
    def wrapper(self, *args, **kwargs):
        self._condition.acquire()
        try:
            return func(self, *args, **kwargs)
        finally:
            self._condition.release()
    wrapper.__doc__ = func.__doc__
    return wrapper


def dumpper(func):
    def wrapper(self, *args, **kwargs):
        if isinstance(self, JsonSerializable):
            result = func(self, *args, **kwargs)
            directory = os.path.join(os.path.dirname(__file__), 'dump')
            file_name = self.queue_uuid
            self.dump_file(dump_file='{dir}/{file_name}.yaml'.format(dir=directory, file_name=file_name))
            return result
        else:
            return func(self, *args, **kwargs)
    wrapper.__doc__ = func.__doc__
    return wrapper


class TaskQueue(JsonSerializable):
    def __init__(self, cache, queue_uuid, trigger_time, sync_group=True):
        self.create_time = get_time.current_ymd_hms()
        self.sync_group = sync_group
        self.trigger_time = trigger_time
        self.expire_time = get_time.calc_expire_time(self.create_time, self.trigger_time)
        self.destroy_time = get_time.calc_destroy_time(self.create_time, self.trigger_time)
        self.queue_status = QueueStatus.Initiating
        self.run_all = False
        self.queue_uuid = queue_uuid
        self.todo_task_queue = None
        self.task_list = []
        self.task_result_list = []
        self.__exclude__.append('todo_task_queue')
        self._condition = threading.Condition(threading.RLock())
        self._cache = cache
        expire_timespan = time.mktime(time.strptime(self.expire_time, '%Y-%m-%d %H:%M:%S')) - time.time()
        self._timer = threading.Timer(expire_timespan, self.update_status_by_time)
        self._timer.setDaemon(True)
        self._timer.start()
        cache[self.queue_uuid] = self

    def __del__(self):
        if self._timer:
            del self._timer

    @staticmethod
    def from_dict(dict_data):
        queue = TaskQueue(**dict_data)
        queue.make_todo_task_queue()
        return queue

    @property
    def IsSync(self):
        """
        查看任务队列是否为同步队列
        """
        return self.sync_group

    @property
    def UUID(self):
        """
        返回任务队列的UUID
        """
        return self.queue_uuid

    @property
    @locker
    def Status(self):
        """
        返回任务队列的状态
        """
        return self.queue_status

    @locker
    def append(self, task):
        """
        添加任务至任务列表，该操作不更新待做任务队列
        如需更新待做任务队列，在完成该操作后调用 make_todo_task_queue
        """
        if self.queue_status == QueueStatus.Initiating:
            logging.info('Task added: {}'.format(task.to_dict()))
            self.task_list.append(task)
        else:
            raise QueueError(u'队列未在初始化状态')

    @locker
    def extend(self, task_list):
        """
        扩展任务列表，该操作不更新待做任务队列
        如需更新待做任务队列，在完成该操作后调用 make_todo_task_queue
        """
        if self.queue_status == QueueStatus.Initiating:
            self.task_list.extend(task_list)
        else:
            raise QueueError(u'队列未在初始化状态')

    @locker
    @dumpper
    def make_todo_task_queue(self):
        """
        初始化待做任务队列
        """
        if self.queue_status not in (QueueStatus.Normal, QueueStatus.Initiating):
            logging.warning('Invalid queue status.')
            return False
        todo = Queue()
        for task in self.task_list[len(self.task_result_list):]:
            todo.put(task)
        if not todo.empty():
            self.todo_task_queue = todo
            self.queue_status = QueueStatus.Normal
            return True
        else:
            logging.warning('Todo queue empty')
            return False

    @locker
    def peek(self, task_uuid=None):
        """
        查看下一项待做任务且不从待做任务队列中取出任务
        """
        if self.queue_status == QueueStatus.Empty:
            return self.queue_status
        task = self.task_list[len(self.task_list) - self.todo_task_queue.qsize()]
        if task_uuid and task_uuid != task.task_uuid:
            return None
        else:
            return task

    @locker
    @dumpper
    def get(self):
        """
        从待做队列中取出任务
        """
        if self.todo_task_queue.empty():
            return None
        if self.queue_status != QueueStatus.Normal:
            return self.queue_status
        if not self.todo_task_queue.empty() and self.queue_status == QueueStatus.Normal:
            task = self.todo_task_queue.get()
            self.queue_status = QueueStatus.JobIssued
            self._condition.notifyAll()
            return task

    @locker
    def put(self, data, idx=0):
        """
        向任务队列添加单个任务或任务列表
        该函数将直接更新待做任务队列
        """
        if isinstance(data, Task):
            if idx:
                if idx >= len(self.task_result_list):
                    self.task_list = self.task_list[:idx] + [data] + self.task_list[idx:]
                else:
                    raise Exception('Index in done task list')
            else:
                self.append(data)
        elif isinstance(data, list) or isinstance(data, tuple):
            if idx:
                if idx >= len(self.task_result_list):
                    self.task_list = self.task_list[:idx] + list(data) + self.task_list[idx:]
                else:
                    raise Exception('Index in done task list')
            else:
                self.extend(data)
        else:
            raise Exception('Invalid data input')
        return self.make_todo_task_queue()

    @locker
    @dumpper
    def skip_failed(self, session=None):
        """
        跳过队列中的失败任务
        """
        if self.queue_status != QueueStatus.JobFailed:
            return False
        last_result = self.task_result_list[-1]
        last_result.status_code = TaskStatus.Skipped
        last_result.session = session
        self.queue_status = QueueStatus.Normal
        self._condition.notifyAll()
        return True

    @locker
    @dumpper
    def resume_failed(self):
        """
        将失败任务恢复至待做队列
        """
        if self.queue_status == QueueStatus.JobFailed:
            self.task_result_list.pop()
            self.make_todo_task_queue()
            return True
        else:
            return False

    @locker
    @dumpper
    def skip_task(self, session=None):
        """
        跳过下一项任务
        """
        if self.todo_task_queue.empty():
            return False
        next_task = self.get()
        if isinstance(next_task, Task):
            self.task_result_list.append(TaskResult(
                next_task.queue_uuid, next_task.task_uuid,
                TaskStatus.Skipped, MSG_DICT[TaskStatus.Skipped], session))
            return True
        else:
            return False

    @locker
    @dumpper
    def update_status_by_result(self, task_result):
        """
        根据任务结果更新队列状态
        """
        current_task = self.task_list[len(self.task_list) - self.todo_task_queue.qsize()]
        if task_result.task_uuid != current_task.task_uuid:
            logging.warning(u'任务结果与当前执行任务不匹配！')
            logging.warning(u'当前任务：{}'.format(json.dumps(current_task.to_dict())))
            logging.warning(u'任务结果：{}'.format(json.dumps(task_result.to_dict())))
            return False
        switch = {
            TaskStatus.UnKnown: lambda: QueueStatus.NotRecoverable,
            TaskStatus.InitFailed: lambda: QueueStatus.NotRecoverable,
            TaskStatus.Runnable: lambda: QueueStatus.JobRunning,
            TaskStatus.TriggerTimeWaiting: lambda: QueueStatus.JobWaiting,
            TaskStatus.WorkerWaiting: lambda: QueueStatus.JobWaiting,
            TaskStatus.TimeRangeExcept: lambda: QueueStatus.JobFailed,
            TaskStatus.Running:
                lambda: QueueStatus.JobRunning if self.sync_group else QueueStatus.Normal,
            TaskStatus.Success:
                lambda: QueueStatus.Done if self.todo_task_queue.empty() else QueueStatus.Normal,
            TaskStatus.Failed: lambda: QueueStatus.JobFailed,
            TaskStatus.Timeout: lambda: QueueStatus.JobFailed,
            TaskStatus.Terminated: lambda: QueueStatus.JobFailed,
            TaskStatus.Skipped:
                lambda: QueueStatus.Done if self.todo_task_queue.empty() else QueueStatus.Normal
        }
        self.queue_status = switch[task_result.task_status]()
        return True

    @locker
    @dumpper
    def update_status_by_time(self):
        """
        根据时间触发更新队列状态
        """
        current_time = time.time()
        expire_time = time.mktime(time.strptime(self.expire_time, '%Y-%m-%d %H:%M:%S'))
        destory_time = time.mktime(time.strptime(self.destroy_time, '%Y-%m-%d %H:%M:%S'))
        if (self.queue_status in (QueueStatus.JobIssued, QueueStatus.JobRunning, QueueStatus.JobWaiting) or
                (self.run_all and self.queue_status != QueueStatus.Done)):
            self._timer = threading.Timer(random.randint(1, 5), self.update_status_by_time)
            self._timer.setDaemon(True)
            self._timer.start()
        elif current_time >= expire_time and current_time < destory_time:
            self.queue_status = QueueStatus.Expired
            self._timer = threading.Timer(destory_time-current_time, self.update_status_by_time)
            self._timer.setDaemon(True)
            self._timer.start()
        if current_time >= destory_time:
            del self._cache[self.queue_uuid]

    @locker
    @dumpper
    def update_task_define(self, task):
        """
        更新已有任务的任务定义
        """
        if task.task_uuid not in map(lambda x: x.task_uuid, self.task_list):
            return None
        elif task.task_uuid in map(lambda x: x.task_uuid, self.task_result_list):
            if task.task_uuid == self.task_result_list[-1].task_uuid:
                if self.task_result_list[-1].status_code in (
                        TaskStatus.Failed, TaskStatus.Skipped, TaskStatus.Terminated,
                        TaskStatus.Timeout, TaskStatus.InitFailed, TaskStatus.TimeRangeExcept):
                    self.task_result_list.pop()
                else:
                    return self.task_result_list[-1].status_code
            else:
                return None
        new_list = self.task_list[:len(self.task_result_list)]
        for old_task in self.task_list[len(self.task_result_list):]:
            if task.task_uuid == old_task.task_uuid:
                new_list.append(task)
            else:
                new_list.append(old_task)
        self.task_list = new_list
        self.make_todo_task_queue()
        return task


class TaskQueueCache(object):
    def __init__(self):
        self._sync_queue_cache = {}
        self._async_queue_cache = {}

    def put_queue(self, queue):
        if queue.IsSync:
            self._sync_queue_cache[queue.UUID] = queue
        else:
            self._async_queue_cache[queue.UUID] = queue

    def queue_exist(self, queue_uuid):
        if queue_uuid in self._sync_queue_cache:
            return self._sync_queue_cache
        if queue_uuid in self._async_queue_cache:
            return self._async_queue_cache
        return None

    def destory(self, queue_uuid):
        cache = self.queue_exist(queue_uuid)
        if cache:
            del cache[queue_uuid]
            return True
        else:
            return False


''' def serialize(func):
    def wrapper(*args, **kwargs):
        code, obj = func(*args, **kwargs)
        if isinstance(obj, JsonSerializable):
            return code, obj.to_dict()
        else:
            return code, obj
    wrapper.__doc__ = func.__doc__
    return wrapper '''


class RPCHandler(object):
    def __init__(self, cache, event_queue):
        self._cache = cache
        self._event_queue = event_queue

    def _queue_exist(self, queue_uuid):
        return queue_uuid in self._cache

    def init(self, queue_dict, force=False):
        if not isinstance(queue_dict, dict):
            raise Exception(u'非法的队列初始化数据')
        for queue_uuid, queue_define in queue_dict.iteritems():
            if not force and self._queue_exist(queue_uuid):
                return -1, u'队列已存在'
            queue = TaskQueue(self._cache, queue_uuid, queue_define['trigger_time'], queue_define['group_block'])
            for task_define in queue_define['group_info']:
                queue.append(Task.from_dict({
                    'queue_uuid': queue_uuid,
                    'create_time': queue.create_time,
                    'trigger_time': queue.trigger_time,
                    'task_uuid': task_define['task_uuid'],
                    'task_earliest': task_define['earliest'],
                    'task_latest': task_define['latest'],
                    'session': None,
                    'task_info': task_define['detail']
                }))
            rtn = queue.make_todo_task_queue()
            logging.info(rtn)
            if not rtn:
                return -1, u'Queue[{}]初始化失败'.format(queue_uuid)
        return 0, u'队列初始化完成'

    def run_all(self, queue_uuid, session=None):
        pass

    def run_next(self, queue_uuid, session=None):
        rtn = self._cache[queue_uuid].get()
        if rtn:
            if isinstance(rtn, Task):
                rtn.session = session
                self._event_queue.put_event(EventName.TaskDispath, rtn)
                return 0, u'任务已调度'
            elif isinstance(rtn, QueueStatus):
                return -1, MSG_DICT[rtn]
            else:
                raise Exception(u'未知的任务调度返回')
        else:
            return -1, MSG_DICT[QueueStatus.Empty]

    def skip_next(self, queue_uuid, task_uuid=None, session=None):
        pass

    def peek(self, queue_uuid, task_uuid=None):
        if self._queue_exist(queue_uuid):
            rtn = self._cache[queue_uuid].peek(task_uuid)
            if rtn:
                if isinstance(rtn, Task):
                    return 0, rtn.to_dict()
                elif isinstance(rtn, QueueStatus):
                    return -1, MSG_DICT[rtn]
                else:
                    return -1, u'返回状态未知'
            else:
                return -1, u'Task uuid[{uuid}] 和下一项待做任务不匹配'.format(uuid=task_uuid)
        else:
            return -1, MSG_DICT[QueueStatus.NotExits]

    def resume(self, queue_uuid):
        pass

    def kill(self, task_uuid):
        pass
