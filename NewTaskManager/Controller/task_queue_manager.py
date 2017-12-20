<<<<<<< HEAD
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
            # self.wait()
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
        # self._ready = False
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

    def status(self, timeout=None):
        # self.wait(timeout)
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

    def append(self, task, timeout=None):
        """
        添加任务至任务队列的任务列表
        """
        # self.wait(timeout)
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

    def peek(self, task_uuid=None, timeout=None):
        """
        从controller的待做队列中查询第一个task
        :param task_uuid: task的uuid
        """
        # self.wait(timeout)
        # ret = self.todo_task_queue.peek()
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
    def get(self, timeout=None):
        """
        从controller的待做队列中取出task
        """
        # self.wait(timeout)
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
    def skip_failed(self, task_uuid, session=None, timeout=None):
        # self.wait(timeout)
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
    def resume_fail_task(self, timeout=None):
        """
        将失败任务压入待做队列
        """
        # self.wait(timeout)
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
    def skip_task(self, session=None, timeout=None):
        """
        跳过下一项任务
        """
        # self.wait(timeout)
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
        # self.wait()
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
        # self.wait()
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
        # self.wait()
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
=======
# coding=utf-8
""" Zero rpc server 4 TaskManager Controller
"""

import os
import zerorpc
from datetime import datetime
from dateutil.parser import parse
from threading import Thread, Condition
from multiprocessing.queues import JoinableQueue

from NewTaskManager.protocol import JsonSerializable
from NewTaskManager.Common import get_time


def timeout(func):
    def wrapper(self, controller_queue_uuid, *args, **kwargs):
        curr_time = datetime.now()
        if controller_queue_uuid not in self.controller_queue_dict:
            return -12, msg_dict[-12]
        expire_time = parse(self.controller_queue_dict[controller_queue_uuid].expire_time)
        destroy_time = parse(self.controller_queue_dict[controller_queue_uuid].destroy_time)
        if curr_time > destroy_time:
            self.controller_queue_dict.pop(controller_queue_uuid)
            os.remove('dump/{0}.dump'.format(controller_queue_uuid))
            return -12, msg_dict[-12]
        elif destroy_time > curr_time > expire_time:
            self.controller_queue_dict[controller_queue_uuid].controller_queue_status = -14
            with open("dump/{0}.dump".format(controller_queue_uuid), "wb") as f:
                f.write(pickle.dumps(self.controller_queue_dict[controller_queue_uuid].to_dict()))
            if func.func_name != 'snapshot':
                return -14, msg_dict[-14]
        return func(self, controller_queue_uuid, *args, **kwargs)

    return wrapper


class TaskQueueManager(zerorpc.Server):
    def __init__(self, ip, port):
        zerorpc.Server.__init__(self, RPCHandler(self))
        self.bind("tcp://{ip}:{port}".format(ip=ip, port=port))

        self._task_queues = {}


class TaskQueue(JsonSerializable):
    def __init__(self, controller_queue_uuid, group_block, trigger_time):
        self.create_time = get_time.current_ymd_hms()
        self.group_block = group_block
        self.trigger_time = trigger_time
        self.expire_time = get_time.calc_expire_time(self.create_time, self.trigger_time)
        self.destroy_time = get_time.calc_destroy_time(self.create_time, self.trigger_time)
        self.controller_queue_status = 0
        self.controller_queue_uuid = controller_queue_uuid
        self.controller_todo_task_queue = JoinableQueue()
        self.controller_task_list = []
        self.controller_task_status_list = []
        self.controller_task_result_list = []
        self.__exclude__.append('controller_todo_task_queue')

    @staticmethod
    def from_dict(dict_data):
        return TaskQueue(**dict_data)

    def put_controller_todo_task_queue(self, task, deserialize=False):
        """
        将task放入controller的待做队列中
        :param task: task
        :param deserialize: 是否是反序列化
        """
        task_uuid = task["task_uuid"]
        task_earliest = task["earliest"]
        task_latest = task["latest"]
        if "session" in task:
            session = task["session"]
        if not deserialize:
            self.controller_task_list.append(task)
            self.controller_task_status_list.append({task_uuid: None})
            self.controller_task_result_list.append({task_uuid: None})
        task = task["detail"]
        if "session" not in locals():
            self.controller_todo_task_queue.put(
                {"controller_queue_uuid": self.controller_queue_uuid, "controller_queue_create_time": self.create_time,
                 "controller_queue_trigger_time": self.trigger_time, "task_uuid": task_uuid,
                 "task_earliest": task_earliest, "task_latest": task_latest, "task": task})
        else:
            self.controller_todo_task_queue.put(
                {"controller_queue_uuid": self.controller_queue_uuid, "controller_queue_create_time": self.create_time,
                 "controller_queue_trigger_time": self.trigger_time, "task_uuid": task_uuid, "session": session,
                 "task_earliest": task_earliest, "task_latest": task_latest, "task": task})

    def peek_controller_todo_task_queue(self, task_uuid):
        """
        从controller的待做队列中查询第一个task
        :param task_uuid: task的uuid
        """
        if self.controller_todo_task_queue.empty():
            return -1, msg_dict[-11]
        ret = self.controller_todo_task_queue.peek()
        if ret["task_uuid"] == task_uuid:
            return 0, u"该任务为待执行任务"
        else:
            return -1, u"该任务非待执行任务"

    def get_controller_todo_task_queue(self):
        """
        从controller的待做队列中取出task
        """
        if self.controller_todo_task_queue.empty():
            return -1, msg_dict[-11]
        if self.controller_queue_status != 0:
            return -1, msg_dict[self.controller_queue_status]
        if not self.controller_todo_task_queue.empty() and self.controller_queue_status == 0:
            task = self.controller_todo_task_queue.get()
            self.controller_queue_status = 11
            return 0, task

    # 20171025 新增跳过一个失败任务
    def skip_fail_task(self, task_uuid, session):
        if self.controller_queue_status != 14:
            # 队列不可恢复
            # return -1, msg_dict[self.controller_queue_status]
            return -1, u'队列状态不可恢复,当前状态: {}'.format(msg_dict[self.controller_queue_status])
        fail_task_uuid_list = list()
        for each in self.controller_task_status_list:
            if each.values()[0] and each.values()[0][0] in (1, 2, 3):
                # 比对task_uuid
                if task_uuid and task_uuid != each.keys()[0]:
                    return -1, u"队列中失败任务"
                # 如果出现执行失败或者执行超时
                each.update({each.keys()[0]: (4, session)})
                fail_task_uuid_list.append(each.keys()[0])
        for each in self.controller_task_result_list:
            if each.keys()[0] == task_uuid:
                task_status = (4, u"任务跳过成功")
                each.get(task_uuid).update({'task_status': task_status})
        if not fail_task_uuid_list:
            return -1, u"队列无失败任务"
        self.controller_queue_status = 0
        return 0, u"任务跳过成功"

    def put_left_controller_todo_task_queue(self):
        """
        将失败任务压入待做队列
        """
        if self.controller_queue_status != 14:
            # 队列不可恢复
            # return -1, msg_dict[self.controller_queue_status]
            return -1, u'队列状态不可恢复,当前状态: {}'.format(msg_dict[self.controller_queue_status])
        else:
            # 寻找到失败任务的uuid
            fail_task_uuid_list = list()
            for each in self.controller_task_status_list:
                if each.values()[0] and each.values()[0][0] in (1, 2, 3):
                    # 如果出现执行失败或者执行超时
                    each.update({each.keys()[0]: None})
                    fail_task_uuid_list.append(each.keys()[0])
            if not fail_task_uuid_list:
                return -1, u"队列无失败任务"
            # 将失败任务先压入队列中
            temp_queue = JoinableQueue()
            for each in self.controller_task_list:
                if each["task_uuid"] in fail_task_uuid_list:
                    if "session" in each:
                        temp_queue.put(
                            {"controller_queue_uuid": self.controller_queue_uuid,
                             "controller_queue_create_time": self.create_time,
                             "controller_queue_trigger_time": self.trigger_time,
                             "task_uuid": each["task_uuid"], "task_earliest": each["earliest"],
                             "session": each["session"], "task_latest": each["latest"], "task": each["detail"]}
                        )
                    else:
                        temp_queue.put(
                            {"controller_queue_uuid": self.controller_queue_uuid,
                             "controller_queue_create_time": self.create_time,
                             "controller_queue_trigger_time": self.trigger_time,
                             "task_uuid": each["task_uuid"], "task_earliest": each["earliest"],
                             "task_latest": each["latest"], "task": each["detail"]}
                        )
            # 更改task_status_list和task_result_list
            for each1 in fail_task_uuid_list:
                for each2 in self.controller_task_status_list:
                    if each1 == each2.keys()[0]:
                        each2.update({each1: None})
                for each2 in self.controller_task_result_list:
                    if each1 == each2.keys()[0]:
                        each2.update({each1: None})
            # 将原先任务也压入队列
            while not self.controller_todo_task_queue.empty():
                temp_queue.put(self.controller_todo_task_queue.get())
            self.controller_todo_task_queue = temp_queue
            self.controller_queue_status = 0
            return 0, u"队列失败任务恢复成功"

    def pop_controller_todo_task_queue(self, session=None):
        """
        移除待做队列中的第一项
        """
        if self.controller_todo_task_queue.empty():
            return -1, msg_dict[-11]
        task = self.controller_todo_task_queue.get()
        task_uuid = task["task_uuid"]
        # 更改任务状态列表
        for each in self.controller_task_status_list:
            for (k, v) in each.iteritems():
                if k == task_uuid:
                    each[k] = (4, session)
        return 0, u"队列第一项移除成功"

    def change_task_info(self, task_uuid, task_status, session, task_result):
        """
        更改task_status_list和task_result_list中的任务状态
        :param task_uuid: task的uuid
        :param task_status: task的状态
        :param session: 用户session
        :param task_result: task的执行结果
        """
        if task_status[0] == -1:
            # 任务初始化失败
            self.controller_queue_status = -13
        if task_status[0] == 0:
            # 任务执行成功
            self.controller_queue_status = 0
        if task_status[0] in (1, 121):
            # 任务执行失败
            self.controller_queue_status = 14
        if task_status[0] in (111, 112):
            # 任务等待中
            self.controller_queue_status = 13
        if task_status[0] == 200:
            # 任务开始执行
            if not self.group_block:
                # 非阻塞队列
                self.controller_queue_status = 0
            else:
                # 阻塞队列
                self.controller_queue_status = 12
        # 更改任务状态列表
        for each in self.controller_task_status_list:
            for (k, v) in each.iteritems():
                if k == task_uuid:
                    each[k] = (task_status[0], session)
        for each in self.controller_task_result_list:
            for (k, v) in each.iteritems():
                if k == task_uuid and task_result:
                    each[k] = task_result.to_dict()

    def update_task_info(self, task_uuid, task_info):
        if task_uuid not in map(lambda x: x["task_uuid"], self.controller_task_list):
            return -1, u"未找到对应任务"
        else:
            # 更新task_status_list
            for each in self.controller_task_status_list:
                if task_uuid in each.keys():
                    if each.get(task_uuid) == 0:
                        return -1, u"成功任务不可更改"
                    else:
                        each.update({task_uuid: None})
            # 更新task_result_list
            for each in self.controller_task_result_list:
                if task_uuid in each.keys():
                    if isinstance(each.get(task_uuid), list) and each.get(task_uuid)[0] == 0:
                        return -1, u"成功任务不可更改"
                    else:
                        each.update({task_uuid: None})
            # 更新task_list
            for each in self.controller_task_list:
                if task_uuid == each.get("task_uuid"):
                    self.controller_task_list[self.controller_task_list.index(each)] = task_info
                # 获取todo_task_list
                todo_task_list = filter(lambda x: not x.values()[0], self.controller_task_status_list)
                todo_task_list = map(lambda x: x.keys()[0], todo_task_list)
            # 重新压队列
            self.controller_todo_task_queue = JoinableQueue()
            for task_uuid in todo_task_list:
                for each in self.controller_task_list:
                    if each.get("task_uuid") == task_uuid:
                        if "session" in each:
                            self.controller_todo_task_queue.put(
                                {"controller_queue_uuid": self.controller_queue_uuid,
                                 "controller_queue_create_time": self.create_time,
                                 "controller_queue_trigger_time": self.trigger_time, "task_uuid": task_uuid,
                                 "task_earliest": each.get("task_earliest"), "task_latest": each.get("task_latest"),
                                 "task": each.get("detail"), "session": each.get("session")})
                        else:
                            self.controller_todo_task_queue.put(
                                {"controller_queue_uuid": self.controller_queue_uuid,
                                 "controller_queue_create_time": self.create_time,
                                 "controller_queue_trigger_time": self.trigger_time, "task_uuid": task_uuid,
                                 "task_earliest": each.get("task_earliest"), "task_latest": each.get("task_latest"),
                                 "task": each.get("detail")})
            self.controller_queue_status = 0
            return 0, u"更新成功"


class RPCHandler(object):
    def __init__(self, manager):
        self._manager = manager

    def init(self, task_dict, force=False):
        pass

    @timeout
    def run_all(self, controller_queue_uuid, session=None):
        pass

    @timeout
    def run_next(self, controller_queue_uuid, session=None):
        pass

    @timeout
    def skip_next(self, controller_queue_uuid, task_uuid=None, session=None):
        pass

    @timeout
    def peek(self, controller_queue_uuid, task_uuid):
        pass

    @timeout
    def resume(self, controller_queue_uuid):
        pass

    @timeout
    def kill(self, task_uuid):
        pass
>>>>>>> 3162c51b839b98c4a1d76d329cae6bbb3b173bfd
