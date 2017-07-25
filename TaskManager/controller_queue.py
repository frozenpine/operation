# coding=utf-8

from enum import Enum
from gevent.queue import JoinableQueue
from app import logging

import get_time

# logging.basicConfig(level="INFO")


class DispatchResult(Enum):
    Dispatched = 0
    EmptyQueue = -1
    QueueBlock = -2
    QueueMissing = -3
    QueueNoError = -4

class TaskStatus(Enum):
    InQueue = 0
    Running = 1
    Success = 2
    Failed = 3
    Skipped = 4


class ControllerQueue(object):
    def __init__(self, controller_queue_uuid, group_block):
        self.create_time = get_time.current_ymd_hms()
        self.group_block = group_block
        self.block_flag = False
        self.controller_queue_uuid = controller_queue_uuid
        self.controller_todo_task_queue = JoinableQueue()
        self.controller_task_list = list()
        self.controller_task_status_list = list()
        self.controller_task_result_list = list()

    def to_dict(self):
        return {
            'create_time': self.create_time,
            'group_block': self.group_block,
            'block_flag': self.block_flag,
            'queue_id': self.controller_queue_uuid,
            'task_list': self.controller_task_list,
            'task_result_list': self.controller_task_result_list,
            'task_status_list': self.controller_task_status_list
        }

    def put_controller_todo_task_queue(self, task, deserialize=False):
        """
        将task放入controller的待做队列中
        :param task: task
        :param deserialize: 是否是反序列化
        :return:
        """
        task_uuid = task["task_uuid"]
        if not deserialize:
            self.controller_task_list.append(task)
            self.controller_task_status_list.append({task_uuid: 0})
            self.controller_task_result_list.append({task_uuid: None})
        task = task["task"]
        self.controller_todo_task_queue.put(
            {"controller_queue_uuid": self.controller_queue_uuid, "task_uuid": task_uuid, "task": task})

    def peek_controller_todo_task_queue(self, task_uuid):
        """
         从controller的待做队列中查询第一个task
        :return: -1 队列为空
                 -2 不相等
        """
        if self.controller_todo_task_queue.empty():
            return -1
        ret = self.controller_todo_task_queue.peek()
        if ret["task_uuid"] == task_uuid:
            return 0
        else:
            return -2

    def get_controller_todo_task_queue(self):
        """
        从controller的待做队列中取出task
        :return: -1 队列为空
                 -2 队列被block
        block_type    group_block    block
           True          True        True
           True          False       False
           False         True        False
           False         False       False
        """
        if self.controller_todo_task_queue.empty():
            return -1, None
        if self.block_flag and self.group_block:
            return -2, None
        if not self.controller_todo_task_queue.empty() and (not self.block_flag or not self.group_block):
            task = self.controller_todo_task_queue.get()
            self.block_flag = True
            return 0, task

    def put_left_controller_todo_task_queue(self):
        """
        将失败任务压入待做队列
        :return: -4 队列无失败任务
        """
        # 寻找到失败任务的uuid
        fail_task_uuid_list = list()
        for each in self.controller_task_status_list:
            if each.values()[0] == 3:
                each.update({each.keys()[0]: 4})
                fail_task_uuid_list.append(each.keys()[0])
        if not fail_task_uuid_list:
            return -4
        # 将失败任务先压入队列中
        temp_queue = JoinableQueue()
        for each in self.controller_task_list:
            if each["task_uuid"] in fail_task_uuid_list:
                temp_queue.put(
                    {"controller_queue_uuid": self.controller_queue_uuid,
                     "task_uuid": each["task_uuid"], "task": each["task"]}
                )
        # 将原先任务也压入队列中
        while not self.controller_todo_task_queue.empty():
            temp_queue.put(self.controller_todo_task_queue.get())
        self.controller_todo_task_queue = temp_queue
        self.block_flag = False
        return 0

    def pop_controller_todo_task_queue(self):
        """
        移除待做队列中的第一项
        :return:
        """
        self.controller_todo_task_queue.get()
        return 0

    def change_task_info(self, task_uuid, task_status, task_result):
        """
        更改task_status_list和task_result_list中的任务状态
        :param task_uuid: task的uuid
        :param task_status: task的状态
        :param task_result: task的执行结果
        :return:
        """
        if task_status == 2:
            # 任务执行成功,更改阻塞状态
            self.block_flag = False
        if task_status == 3:
            # 任务执行失败,继续阻塞
            pass
        # 更改任务状态列表
        for each in self.controller_task_status_list:
            for (k, v) in each.iteritems():
                if k == task_uuid:
                    each[k] = task_status
        for each in self.controller_task_result_list:
            for (k, v) in each.iteritems():
                if k == task_uuid and task_result:
                    each[k] = task_result.to_dict()
