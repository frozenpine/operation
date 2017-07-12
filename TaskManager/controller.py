# coding=utf-8

import cPickle as pickle
import logging
import requests

from controller_queue import ControllerQueue
from msg_queue import msg_queue

logging.basicConfig(level="INFO")


class Controller(object):
    def __init__(self):
        self.controller_queue_dict = dict()
        self.callback_dict = dict()

    def get_snapshot(self, controller_queue_uuid):
        """
        获取controller_queue的快照
        :param controller_queue_uuid: controller_queue的controller_queue_uuid
        :return:
        """
        try:
            return self.controller_queue_dict[controller_queue_uuid].to_dict()
        except KeyError:
            return None

    def get_create_time(self, controller_queue_uuid):
        """
        获取controller_queue的创建时间
        :param controller_queue_uuid: controller_queue的controller_queue_uuid
        :return:
        """
        return self.controller_queue_dict[controller_queue_uuid].create_time

    def get_group_block(self, controller_queue_uuid):
        """
        获取controller_queue是否是阻塞队列
        :param controller_queue_uuid: controller_queue的controller_queue_uuid
        :return:
        """
        return self.controller_queue_dict[controller_queue_uuid].group_block

    def controller_queue_exists(self, controller_queue_uuid):
        """
        检测controller_queue字典中是否存在当前controller_queue的controller_queue_uuid
        :param controller_queue_uuid: controller_queue的controller_queue_uuid
        :return:
        """
        return controller_queue_uuid in self.controller_queue_dict

    def init_controller_queue(self, task_dict, force=False):
        """
        初始化controller_queue, 并向controller_queue中添加任务
        :param task_dict: 任务组和任务字典
        :param force 强制
        :return:
        """
        if force:
            for (k, v) in task_dict.iteritems():
                self.controller_queue_dict[k] = ControllerQueue(k, v["group_block"])
                for each in v["group_info"]:
                    self.put_task_to_controller_queue(k, each)
                    with open("dump/{0}.dump".format(k), "wb") as f:
                        f.write(pickle.dumps(self.controller_queue_dict[k].controller_task_list))
                if not v["group_block"]:
                    self.get_tasks_from_controller_queue(k)
        else:
            ret_dict = dict()
            for (k, v) in task_dict.iteritems():
                if self.controller_queue_exists(k):
                    ret_dict.update({
                        k: {
                            "create_time": self.get_create_time(k),
                            "group_task": self.get_snapshot(k)
                        }
                    })
                else:
                    self.controller_queue_dict[k] = ControllerQueue(k, v["group_block"])
                    for each in v["group_info"]:
                        self.put_task_to_controller_queue(k, each)
                        with open("dump/{0}.dump".format(k), "wb") as f:
                            f.write(pickle.dumps(
                                self.controller_queue_dict[k].controller_task_list
                            ))
                    if not v["group_block"]:
                        self.get_tasks_from_controller_queue(k)
            if ret_dict:
                return ret_dict
        return 0

    def del_controller_queue(self, controller_queue_uuid):
        """
        删除指定的controller_queue
        :param controller_queue_uuid: controller_queue的controller_queue_uuid
        :return:
        """
        del self.controller_queue_dict[controller_queue_uuid]

    def put_task_to_controller_queue(self, controller_queue_uuid, task):
        """
        向指定的的controller_queue中添加任务
        :param controller_queue_uuid: controller_queue的controller_queue_uuid
        :param task: 任务字典
        :return:
        """
        self.controller_queue_dict[controller_queue_uuid].put_controller_todo_task_queue(task)

    def peek_task_from_controller_queue(self, controller_queue_uuid, task_uuid):
        """
        比较指定controller_queue的第一个元素的task_uuid
        :param controller_queue_uuid:
        :param task_uuid:
        :return:
        """
        ret = self.controller_queue_dict[controller_queue_uuid]\
            .peek_controller_todo_task_queue(task_uuid)
        return ret

    def get_task_from_controller_queue(self, controller_queue_uuid, run_all=False):
        """
        从指定的controller_queue中取出任务
        :param controller_queue_uuid: controller_queue的controller_queue_uuid
        :param run_all: 执行所有
        :return:
        """
        ret, task = self.controller_queue_dict[controller_queue_uuid]\
            .get_controller_todo_task_queue()
        if ret == -1 or ret == -2:
            return ret, None
        else:
            msg_queue.todo_task_queue.put({"run_all": run_all, "ret": task})
            return ret, task['task_uuid']

    def get_tasks_from_controller_queue(self, controller_queue_uuid):
        """
        从指定的controller_queue中执行多个任务
        :param controller_queue_uuid: controller_queue的controller_queue_uuid
        :return:
        """
        ret = self.get_task_from_controller_queue(controller_queue_uuid, run_all=True)
        if ret == -1 or ret == -2:
            return ret
        else:
            return 0

    def register_callback(self, event, callback):
        """
        向controller中注册回调事件
        :param event: 事件
        :param callback: 回调
        :return:
        """
        self.callback_dict[event] = callback

    def change_task_status(self, controller_queue_uuid, task_uuid, task_status):
        """
        更改task_list中的任务状态
        :param controller_queue_uuid: controller_queue的uuid
        :param task_uuid: task的uuid
        :param task_status: task的状态
        :return:
        """
        self.controller_queue_dict[controller_queue_uuid].change_task_status(task_uuid, task_status)

    def worker_start_callback(self, result):
        """
        任务开始执行 回调函数
        :param result: 回调结果
        :return:
        """
        self.change_task_status(result.controller_queue_uuid, result.task_uuid, result.task_status)
        logging.info("task {0} start".format(result.task_uuid))
        with open("dump/{0}.dump".format(result.controller_queue_uuid), "wb") as f:
            f.write(pickle.dumps(
                self.controller_queue_dict[result.controller_queue_uuid].controller_task_list
            ))
        logging.info(result.to_str())
        ''' requests.post(
            'http://localhost:5000/api/operation/uuid/{id}/callback'.format(id=result.task_uuid),
            json=result.to_dict()
        ) '''
        # 非阻塞队列开始执行后
        if result.run_all and not self.get_group_block(result.controller_queue_uuid):
            self.get_task_from_controller_queue(result.controller_queue_uuid, True)

    def worker_end_callback(self, result):
        """
        任务结束执行 回调函数
        :param result: 回调结果
        :return:
        """
        self.change_task_status(result.controller_queue_uuid, result.task_uuid, result.task_status)
        logging.info("task {0} start".format(result.task_uuid))
        with open("dump/{0}.dump".format(result.controller_queue_uuid), "wb") as f:
            f.write(pickle.dumps(
                self.controller_queue_dict[result.controller_queue_uuid].controller_task_list
            ))
        logging.info(result.to_str())
        requests.post(
            'http://localhost:5000/api/operation/uuid/{id}/callback'.format(id=result.task_uuid),
            json=result.to_dict()
        )
        # 阻塞队列执行完成后
        if result.run_all and \
            self.get_group_block(result.controller_queue_uuid) and \
            result.task_status == 2:
            self.get_task_from_controller_queue(result.controller_queue_uuid, True)

    def run_all(self, controller_queue_uuid):
        return self.get_tasks_from_controller_queue(controller_queue_uuid)

    def run_next(self, controller_queue_uuid):
        return self.get_task_from_controller_queue(controller_queue_uuid)

    def peek(self, controller_queue_uuid, task_uuid):
        return self.peek_task_from_controller_queue(controller_queue_uuid, task_uuid)

    def snapshot(self, controller_queue_uuid):
        return self.get_snapshot(controller_queue_uuid)

    def create_time(self, controller_queue_uuid):
        return self.get_create_time(controller_queue_uuid)
