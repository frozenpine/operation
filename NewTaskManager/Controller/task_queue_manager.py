# coding=utf-8
""" Zero rpc server 4 TaskManager Controller
"""

import os
import sys
import threading
import logging
import json
import time
import random
from datetime import datetime
from multiprocessing import Queue, TimeoutError

import zerorpc
from dateutil.parser import parse

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from NewTaskManager.common import get_time
from NewTaskManager.protocol import (MSG_DICT, JsonSerializable, QueueStatus,
                                     Task, TaskResult, TaskStatus)
from NewTaskManager.Controller.excepts import *


class TaskQueueManager(threading.Thread):
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self._task_queues = {}
        self._entrypoint = zerorpc.Server(RPCHandler(self._task_queues))
        self._entrypoint.bind("tcp://{ip}:{port}".format(ip=ip, port=port))

    def run(self):
        self._entrypoint.run()


def dumpper(func):
    def wrapper(self, *args, **kwargs):
        if isinstance(self, JsonSerializable):
            self._condition.acquire()
            try:
                result = func(self, *args, **kwargs)
                directory = os.path.join(os.path.dirname(__file__), 'dump')
                file_name = self.queue_uuid
                self.dump_file(dump_file='{dir}/{file_name}.yaml'.format(dir=directory, file_name=file_name))
            finally:
                self._condition.release()
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

    @staticmethod
    def from_dict(dict_data):
        queue = TaskQueue(**dict_data)
        queue.make_todo_task_queue()
        return queue

    ''' def ready(self):
        return self._ready '''

    def status(self):
        self._condition.acquire()
        ''' if not self._ready:
            raise TimeoutError '''
        try:
            return self.queue_status
        finally:
            self._condition.release()

    ''' def wait(self, timeout=None):
        self._condition.acquire()
        try:
            if not self._ready:
                self._condition.wait(timeout)
        finally:
            self._condition.release() '''

    def append(self, task):
        """
        添加任务至任务队列的任务列表
        """
        self._condition.acquire()
        try:
            self._ready = False
            if self.queue_status == QueueStatus.Initiating:
                self.task_list.append(task)
            else:
                raise QueueError(u'队列未在初始化状态')
        except:
            raise
        finally:
            self._condition.release()

    def extend(self, task_list):
        self._condition.acquire()
        try:
            # self._ready = False
            if self.queue_status == QueueStatus.Initiating:
                self.task_list.extend(task_list)
            else:
                raise QueueError(u'队列未在初始化状态')
        except:
            raise
        finally:
            self._condition.release()

    @dumpper
    def make_todo_task_queue(self):
        """
        将task放入controller的待做队列中
        """
        self._condition.acquire()
        try:
            todo = Queue()
            for task in self.task_list[len(self.task_result_list):]:
                todo.put(task)
            if not todo.empty():
                self.todo_task_queue = todo
                self.queue_status = QueueStatus.Normal
            # self._ready = True
            self._condition.notifyAll()
        finally:
            self._condition.release()

    def peek(self, task_uuid=None):
        """
        从controller的待做队列中查询第一个task
        :param task_uuid: task的uuid
        """
        self._condition.acquire()
        try:
            if self.todo_task_queue.empty():
                return QueueStatus.Empty, MSG_DICT[QueueStatus.Empty]
            task = self.task_list[len(self.task_list) - self.todo_task_queue.qsize()]
            if task_uuid and task_uuid != task.task_uuid:
                return None
            else:
                return task
        finally:
            self._condition.release()

    @dumpper
    def get(self):
        """
        从controller的待做队列中取出task
        """
        self._condition.acquire()
        try:
            if self.todo_task_queue.empty():
                return QueueStatus.Empty, MSG_DICT[QueueStatus.Empty]
            if self.queue_status != QueueStatus.Normal:
                return self.queue_status, MSG_DICT[self.queue_status]
            if not self.todo_task_queue.empty() and self.queue_status == QueueStatus.Normal:
                task = self.todo_task_queue.get()
                self.queue_status = QueueStatus.JobIssued
                return 0, task
        finally:
            self._condition.release()

    @dumpper
    def skip_failed(self, task_uuid, session=None):
        self._condition.acquire()
        try:
            if self.queue_status != QueueStatus.JobFailed:
                # 队列不可恢复
                # return -1, MSG_DICT[self.queue_status]
                return self.queue_status, u'队列状态不可恢复,当前状态: {}'.format(MSG_DICT[self.queue_status])
            last_result = self.task_result_list[-1]
            if task_uuid and last_result.task_uuid != task_uuid:
                return -1, u'非失败任务不可跳过'
            if last_result.status_code != TaskStatus.Failed:
                return -1, u'队列无失败任务'
            else:
                last_result.status_code = TaskStatus.Skipped
                self.queue_status = QueueStatus.Normal
            return 0, u"任务跳过成功"
        finally:
            self._condition.release()

    @dumpper
    def resume_fail_task(self):
        """
        将失败任务压入待做队列
        """
        self._condition.acquire()
        try:
            if self.task_result_list[-1].status_code == TaskStatus.Failed:
                self.task_result_list.pop()
                self.make_todo_task_queue()
            else:
                return -1, u'非失败任务不可恢复'
        finally:
            self._condition.release()

    @dumpper
    def skip_task(self, session=None):
        """
        跳过下一项任务
        """
        self._condition.acquire()
        try:
            if self.todo_task_queue.empty():
                return QueueStatus.Empty, MSG_DICT[QueueStatus.Empty]
            code, next_task = self.get()
            if code == 0:
                self.task_result_list.append(TaskResult(
                    next_task.queue_uuid, next_task.task_uuid, TaskStatus.Skipped, session))
                return 0, u"任务跳过成功"
        finally:
            self._condition.release()

    @dumpper
    def update_status_by_result(self, task_result):
        """
        更改task_status_list和task_result_list中的任务状态
        :param task_uuid: task的uuid
        :param task_status: task的状态
        :param session: 用户session
        :param task_result: task的执行结果
        """
        self._condition.acquire()
        try:
            current_task = self.task_list[len(self.task_list) - self.todo_task_queue.qsize()]
            if task_result.task_uuid != current_task.task_uuid:
                logging.warning(u'任务结果与当前执行任务不匹配！')
                logging.warning(u'当前任务：{}'.format(json.dumps(current_task.to_dict())))
                logging.warning(u'任务结果：{}'.format(json.dumps(task_result.to_dict())))
                return
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
            self._condition.notifyAll()
        finally:
            self._condition.release()

    @dumpper
    def update_status_by_time(self):
        self._condition.acquire()
        try:
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
                self._condition.notifyAll()
                self._timer = threading.Timer(destory_time-current_time, self.update_status_by_time)
                self._timer.setDaemon(True)
                self._timer.start()
        finally:
            self._condition.release()
        if current_time >= destory_time:
            del self._cache[self.queue_uuid]

    @dumpper
    def update_task_define(self, task):
        self._condition.acquire()
        try:
            if task.task_uuid not in map(lambda x: x.task_uuid, self.task_list):
                return -1, u"未找到对应任务"
            elif task.task_uuid in map(lambda x: x.task_uuid, self.task_result_list):
                if task.task_uuid == self.task_result_list[-1].task_uuid:
                    if self.task_result_list[-1].status_code in (
                            TaskStatus.Failed, TaskStatus.Skipped, TaskStatus.Terminated,
                            TaskStatus.Timeout, TaskStatus.InitFailed, TaskStatus.TimeRangeExcept):
                        self.task_result_list.pop()
                    else:
                        return -1, u'当前任务状态({})无法更新任务定义'.format(
                            MSG_DICT[self.task_result_list[-1].status_code])
                else:
                    return -1, u'不可更新已完成任务'
            new_list = self.task_list[:len(self.task_result_list)]
            for old_task in self.task_list[len(self.task_result_list):]:
                if task.task_uuid == old_task.task_uuid:
                    new_list.append(task)
                else:
                    new_list.append(old_task)
            self.task_list = new_list
            self.make_todo_task_queue()
            return 0, u"更新成功"
        finally:
            self._condition.release()


''' def expired(func):
    def wrapper(self, queue_uuid, *args, **kwargs):
        curr_time = datetime.now()
        if not self._queue_exist(queue_uuid):
            return QueueStatus.NotExits, MSG_DICT[QueueStatus.NotExits]
        expire_time = parse(self._cache[queue_uuid].expire_time)
        destroy_time = parse(self._cache[queue_uuid].destroy_time)
        if curr_time > destroy_time:
            self._cache.pop(queue_uuid)
            os.remove('dump/{0}.dump'.format(queue_uuid))
            return QueueStatus.NotExits, MSG_DICT[QueueStatus.NotExits]
        elif destroy_time > curr_time > expire_time:
            self._cache[queue_uuid].queue_status = -14
            with open("dump/{0}.dump".format(queue_uuid), "wb") as f:
                f.write(pickle.dumps(self._manager.queue_dict[queue_uuid].to_dict()))
            if func.func_name != 'snapshot':
                return -14, MSG_DICT[-14]
        return func(self, queue_uuid, *args, **kwargs)

    return wrapper '''


class RPCHandler(object):
    def __init__(self, cache):
        self._cache = cache

    def _queue_exist(self, queue_id):
        return queue_id in self._cache.keys()

    def init(self, queue_dict, force=False):
        if not isinstance(queue_dict, dict):
            return QueueStatus.InitFailed, MSG_DICT[QueueStatus.InitFailed]
        for queue_id, queue_define in queue_dict.iteritems():
            if not force and self._queue_exist(queue_id):
                return QueueStatus.InitFailed, MSG_DICT[QueueStatus.InitFailed]
            queue = TaskQueue(self._cache, queue_id, queue_define['trigger_time'], queue_define['group_block'])
            for task_define in queue_define['group_info']:
                queue.append(Task.from_dict({
                    'queue_uuid': queue_id,
                    'create_time': queue.create_time,
                    'trigger_time': queue.trigger_time,
                    'task_uuid': task_define['task_uuid'],
                    'task_earliest': task_define['earliest'],
                    'task_latest': task_define['latest'],
                    'session': None,
                    'task_info': task_define['detail']
                }))
            queue.make_todo_task_queue()
        self._cache[queue.queue_uuid] = queue

    def run_all(self, queue_uuid, session=None):
        pass

    def run_next(self, queue_uuid, session=None):
        pass

    def skip_next(self, queue_uuid, task_uuid=None, session=None):
        pass

    def peek(self, queue_uuid, task_uuid=None):
        if self._queue_exist(queue_uuid):
            return self._cache[queue_uuid].peek(task_uuid)
        else:
            return QueueStatus.NotExits, MSG_DICT[QueueStatus.NotExits]

    def resume(self, queue_uuid):
        pass

    def kill(self, task_uuid):
        pass
