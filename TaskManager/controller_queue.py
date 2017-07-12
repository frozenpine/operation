# coding=utf-8

import logging

from gevent.queue import JoinableQueue
from enum import Enum

import get_time

logging.basicConfig(level="INFO")


class DispatchResult(Enum):
    Dispatched = 0
    EmptyQueue = -1
    QueueBlock = -2

class ControllerQueue(object):
    def __init__(self, controller_queue_uuid, group_block):
        self.create_time = get_time.current_ymd_hms()
        self.group_block = group_block
        self.block_flag = False
        self.controller_queue_uuid = controller_queue_uuid
        self.controller_todo_task_queue = JoinableQueue()
        self.controller_task_list = list()

    def to_dict(self):
        return {
            'create_time': self.create_time,
            'group_block': self.group_block,
            'block_flag': self.block_flag,
            'queue_id': self.controller_queue_uuid,
            'task_list': self.controller_task_list
        }

    def put_controller_todo_task_queue(self, task):
        """
        将task放入controller的待做队列中
        :param task: task
        :return:
        """
        task_uuid = task["task_uuid"]
        task = task["task"]
        self.controller_todo_task_queue.put(
            {"controller_queue_uuid": self.controller_queue_uuid, "task_uuid": task_uuid, "task": task})
        self.controller_task_list.append({task_uuid: 0})

    def peek_controller_todo_task_queue(self, task_uuid):
        """
         从controller的待做队列中查询第一个task
        :return: -1 代表队列为空
                 -2 表示不相等
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
        :return: -1 代表队列为空
                 -2 代表队列被block
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

    def change_task_status(self, task_uuid, task_status):
        """
        更改task_list中的任务状态
        :param task_uuid: task的uuid
        :param task_status: task的状态
        :return:
        """
        for each in self.controller_task_list:
            if task_status == 2:
                self.block_flag = False
            for (k, v) in each.iteritems():
                if k == task_uuid:
                    each[k] = task_status
