# coding=utf-8

import logging

from enum import Enum
from gevent.queue import JoinableQueue

import get_time
from controller_msg import msg_dict

logging.basicConfig(level="INFO")


class DispatchResult(Enum):
    pass


class TaskStatus(Enum):
    pass


class ControllerQueue(object):
    def __init__(self, controller_queue_uuid, group_block, trigger_time):
        self.create_time = get_time.current_ymd_hms()
        # self.create_time = "2017-01-01 12:00:00"
        self.group_block = group_block
        self.trigger_time = trigger_time
        self.controller_queue_status = 0
        self.controller_queue_uuid = controller_queue_uuid
        self.controller_todo_task_queue = JoinableQueue()
        self.controller_task_list = list()
        self.controller_task_status_list = list()
        self.controller_task_result_list = list()

    def to_dict(self):
        """
        转换为字典
        """
        return {
            "create_time": self.create_time,
            "trigger_time": self.trigger_time,
            "group_block": self.group_block,
            "controller_queue_status": self.controller_queue_status,
            "controller_queue_uuid": self.controller_queue_uuid,
            "task_list": self.controller_task_list,
            "task_result_list": self.controller_task_result_list,
            "task_status_list": self.controller_task_status_list
        }

    def put_controller_todo_task_queue(self, task, deserialize=False):
        """
        将task放入controller的待做队列中
        :param task: task
        :param deserialize: 是否是反序列化
        """
        task_uuid = task["task_uuid"]
        task_earliest = task["earliest"]
        task_latest = task["latest"]
        if not deserialize:
            self.controller_task_list.append(task)
            self.controller_task_status_list.append({task_uuid: None})
            self.controller_task_result_list.append({task_uuid: None})
        task = task["detail"]
        self.controller_todo_task_queue.put(
            {"controller_queue_uuid": self.controller_queue_uuid, "controller_queue_create_time": self.create_time,
             "controller_queue_trigger_time": self.trigger_time, "task_uuid": task_uuid, "task_earliest": task_earliest,
             "task_latest": task_latest, "task": task})

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

    def pop_controller_todo_task_queue(self):
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
                    each[k] = 4
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
        if task_status[0] == 1:
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
