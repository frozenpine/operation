# coding=utf-8

import json as pickle
import logging
import os

from controller_msg import msg_dict
from controller_queue import ControllerQueue
from msg_queue import msg_queue

# import requests

app_host = os.environ.get("FLASK_HOST") or "127.0.0.1"
app_port = os.environ.get("FLASK_PORT") or 6001

logging.basicConfig(level="INFO")


class Controller(object):
    def __init__(self):
        self.controller_queue_dict = dict()
        self.callback_dict = dict()

    def __get_create_time(self, controller_queue_uuid):
        """
        私有函数
        获取controller_queue的创建时间
        :param controller_queue_uuid: controller_queue的controller_queue_uuid
        """
        return self.controller_queue_dict[controller_queue_uuid].create_time

    def __get_group_block(self, controller_queue_uuid):
        """
        私有函数
        获取controller_queue是否是阻塞队列
        :param controller_queue_uuid: controller_queue的controller_queue_uuid
        """
        return self.controller_queue_dict[controller_queue_uuid].group_block

    def __controller_queue_exists(self, controller_queue_uuid):
        """
        私有函数
        检测controller_queue字典中是否存在当前controller_queue的controller_queue_uuid
        :param controller_queue_uuid: controller_queue的controller_queue_uuid
        """
        return controller_queue_uuid in self.controller_queue_dict

    def __put_task_to_controller_queue(self, controller_queue_uuid, task):
        """
        私有函数
        向指定的的controller_queue中添加任务
        :param controller_queue_uuid: controller_queue的controller_queue_uuid
        :param task: 任务字典
        """
        self.controller_queue_dict[controller_queue_uuid].put_controller_todo_task_queue(task)

    def __create_time(self, controller_queue_uuid):
        """
        私有函数
        获取队列的创建时间
        :param controller_queue_uuid: controller_queue的controller_queue_uuid
        """
        return self.__get_create_time(controller_queue_uuid)

    def register_callback(self, event, callback):
        """
        向worker注册事件回调
        :param event: 事件
        :param callback: 回调
        :return:
        """
        self.callback_dict[event] = callback

    def get_snapshot(self, controller_queue_uuid):
        """
        获取controller_queue的快照
        :param controller_queue_uuid: controller_queue的controller_queue_uuid
        """
        if not self.__controller_queue_exists(controller_queue_uuid):
            return -1, msg_dict[-12]
        else:
            snap = self.controller_queue_dict[controller_queue_uuid].to_dict()
            snap["task_result_list"] = map(lambda x: x.values()[0], snap["task_result_list"])
            snap["task_status_list"] = map(lambda x: x.values()[0], snap["task_status_list"])
            return 0, snap

    def init_controller_queue(self, task_dict, force=False):
        """
        初始化controller_queue, 并向controller_queue中添加任务
        :param task_dict: 任务组和任务字典
        :param force: 强制
        """
        if force:
            for (k, v) in task_dict.iteritems():
                self.controller_queue_dict[k] = ControllerQueue(k, v["group_block"])
                for each in v["group_info"]:
                    self.__put_task_to_controller_queue(k, each)
                    with open("dump/{0}.dump".format(k), "wb") as f:
                        f.write(pickle.dumps(self.controller_queue_dict[k].to_dict()))
                if not v["group_block"]:
                    self.get_tasks_from_controller_queue(k)
        else:
            ret_dict = dict()
            for (k, v) in task_dict.iteritems():
                if self.__controller_queue_exists(k):
                    ret_dict.update({
                        k: {
                            "create_time": self.__get_create_time(k),
                            "group_task": self.get_snapshot(k)
                        }
                    })
                else:
                    self.controller_queue_dict[k] = ControllerQueue(k, v["group_block"])
                    for each in v["group_info"]:
                        self.__put_task_to_controller_queue(k, each)
                        with open("dump/{0}.dump".format(k), "wb") as f:
                            f.write(pickle.dumps(self.controller_queue_dict[k].to_dict()))
                    if not v["group_block"]:
                        self.get_tasks_from_controller_queue(k)
            if ret_dict:
                return 0, ret_dict
        return 0, None

    def del_controller_queue(self, controller_queue_uuid):
        """
        删除指定的controller_queue
        :param controller_queue_uuid: controller_queue的controller_queue_uuid
        """
        if not self.__controller_queue_exists(controller_queue_uuid):
            return -1, msg_dict[-12]
        else:
            del self.controller_queue_dict[controller_queue_uuid]
            return 0, None

    def peek_task_from_controller_queue(self, controller_queue_uuid, task_uuid):
        """
        比较指定controller_queue的第一个元素的task_uuid
        :param controller_queue_uuid: controller_queue的controller_queue_uuid
        :param task_uuid: task的uuid
        """
        if not self.__controller_queue_exists(controller_queue_uuid):
            return -1, msg_dict[-12]
        else:
            ret, msg = self.controller_queue_dict[controller_queue_uuid].peek_controller_todo_task_queue(task_uuid)
            return ret, msg

    def get_task_from_controller_queue(self, controller_queue_uuid, session=None, run_all=False):
        """
        从指定的controller_queue中取出任务
        :param controller_queue_uuid: controller_queue的controller_queue_uuid
        :param session: 执行用户的session
        :param run_all: 执行所有
        """
        if not self.__controller_queue_exists(controller_queue_uuid):
            return -1, msg_dict[-12]
        ret, msg = self.controller_queue_dict[controller_queue_uuid].get_controller_todo_task_queue()
        if ret != 0:
            return ret, msg
        else:
            task_uuid = msg["task_uuid"]
            task_earliest = msg["task_earliest"]
            task_latest = msg["task_latest"]
            task = msg["task"]
            controller_queue_create_time = msg["controller_queue_create_time"]

            msg_queue.todo_task_queue.put(
                {"controller_queue_uuid": controller_queue_uuid,
                 "controller_queue_create_time": controller_queue_create_time, "task_uuid": task_uuid,
                 "task_earliest": task_earliest, "task_latest": task_latest, "task": task, "session": session,
                 "run_all": run_all})
            return 0, task_uuid

    def get_tasks_from_controller_queue(self, controller_queue_uuid, session=None):
        """
        从指定的controller_queue中执行多个任务
        :param controller_queue_uuid: controller_queue的controller_queue_uuid
        :param session: 执行用户的session
        """
        return self.get_task_from_controller_queue(controller_queue_uuid, session, True)

    def put_left_to_controller_queue(self, controller_queue_uuid):
        """
        向指定的controller_queue压回失败任务
        :param controller_queue_uuid: controller_queue的controller_queue_uuid
        """
        if not self.__controller_queue_exists(controller_queue_uuid):
            return -1, msg_dict[-12]
        else:
            ret, msg = self.controller_queue_dict[controller_queue_uuid].put_left_controller_todo_task_queue()
            with open("dump/{0}.dump".format(controller_queue_uuid), "wb") as f:
                f.write(pickle.dumps(self.controller_queue_dict[controller_queue_uuid].to_dict()))
            return ret, msg

    def pop_task_from_controller_queue(self, controller_queue_uuid, task_uuid=None):
        """
        从指定的controller_queue中移除第一个任务
        :param controller_queue_uuid: controller_queue的controller_queue_uuid
        :param task_uuid: task的task_uuid
        """
        if not self.__controller_queue_exists(controller_queue_uuid):
            return -1, msg_dict[-12]
        if task_uuid:
            ret, msg = self.peek_task_from_controller_queue(controller_queue_uuid, task_uuid)
            if ret != 0:
                return ret, msg
            else:
                ret, msg = self.controller_queue_dict[controller_queue_uuid].pop_controller_todo_task_queue()
                return ret, msg
        else:
            ret, msg = self.controller_queue_dict[controller_queue_uuid].pop_controller_todo_task_queue()
            return ret, msg

    def register_callback(self, event, callback):
        """
        向controller中注册回调事件
        :param event: 事件
        :param callback: 回调
        """
        self.callback_dict[event] = callback

    def change_task_status(self, controller_queue_uuid, task_uuid, task_status, task_result):
        """
        更改task_list中的任务状态
        :param controller_queue_uuid: controller_queue的uuid
        :param task_uuid: task的uuid
        :param task_status: task的状态
        :param task_result: task的结果
        """
        self.controller_queue_dict[controller_queue_uuid].change_task_info(task_uuid, task_status, task_result)

    def worker_init_callback(self, result):
        """
        任务初始化 回调函数
        :param result: 回调结果
        """
        self.change_task_status(result.controller_queue_uuid, result.task_uuid, result.task_status, None)
        logging.info("task {0} init, user {1}".format(result.task_uuid, result.session))
        with open("dump/{0}.dump".format(result.controller_queue_uuid), "wb") as f:
            f.write(pickle.dumps(
                self.controller_queue_dict[result.controller_queue_uuid].to_dict()
            ))
        logging.info(result.to_str())
        # requests.post(
        #     "http://{ip}:{port}/api/operation/uuid/{id}/callback".format(
        #         ip=app_host,
        #         port=app_port,
        #         id=result.task_uuid
        #     ),
        #     json=result.to_dict()
        # )

    def worker_start_callback(self, result):
        """
        任务开始执行 回调函数
        :param result: 回调结果
        """
        self.change_task_status(result.controller_queue_uuid, result.task_uuid, result.task_status, None)
        logging.info("task {0} start, user {1}".format(result.task_uuid, result.session))
        with open("dump/{0}.dump".format(result.controller_queue_uuid), "wb") as f:
            f.write(pickle.dumps(
                self.controller_queue_dict[result.controller_queue_uuid].to_dict()
            ))
        logging.info(result.to_str())
        # requests.post(
        #     "http://{ip}:{port}/api/operation/uuid/{id}/callback".format(
        #         ip=app_host,
        #         port=app_port,
        #         id=result.task_uuid
        #     ),
        #     json=result.to_dict()
        # )
        # 非阻塞队列开始执行后
        if result.run_all and not self.__get_group_block(result.controller_queue_uuid):
            self.get_task_from_controller_queue(result.controller_queue_uuid, True)

    def worker_end_callback(self, result):
        """
        任务结束执行 回调函数
        :param result: 回调结果
        """
        self.change_task_status(result.controller_queue_uuid, result.task_uuid, result.task_status, result)
        logging.info("task {0} end, user {1}".format(result.task_uuid, result.session))
        with open("dump/{0}.dump".format(result.controller_queue_uuid), "wb") as f:
            f.write(pickle.dumps(
                self.controller_queue_dict[result.controller_queue_uuid].to_dict()
            ))
        logging.info(result.to_str())
        # requests.post(
        #     "http://{ip}:{port}/api/operation/uuid/{id}/callback".format(
        #         ip=app_host,
        #         port=app_port,
        #         id=result.task_uuid
        #     ),
        #     json=result.to_dict()
        # )
        # 阻塞队列执行完成后
        if result.run_all and self.__get_group_block(result.controller_queue_uuid) and result.task_status[0] == 0:
            self.get_task_from_controller_queue(result.controller_queue_uuid, result.session, True)

    def deserialize(self):
        """
        反序列化
        """
        dump_file_list = os.listdir("dump")
        logging.info("TaskQueue deserializing started")
        for each in dump_file_list:
            with open("dump/{0}".format(each)) as f:
                f_stream = f.read()
            try:
                queue_status = pickle.loads(f_stream)
            except TypeError:
                # 序列化存在问题
                logging.error("TaskQueue deserializing failed")
                return -1, msg_dict[-1]
            else:
                create_time = queue_status["create_time"]
                group_block = queue_status["group_block"]
                queue_id = queue_status["queue_id"]
                task_list = queue_status["task_list"]
                task_result_list = queue_status["task_result_list"]
                task_status_list = queue_status["task_status_list"]
                self.controller_queue_dict[queue_id] = ControllerQueue(queue_id, group_block)
                self.controller_queue_dict[queue_id].create_time = create_time
                self.controller_queue_dict[queue_id].controller_task_list = task_list
                self.controller_queue_dict[queue_id].controller_task_result_list = task_result_list
                self.controller_queue_dict[queue_id].controller_task_status_list = task_status_list
                for i in range(0, len(task_list), 1):
                    if task_status_list[i].values()[0] in (0, 1, 3):
                        self.controller_queue_dict[queue_id].put_controller_todo_task_queue(task_list[i], True)
        logging.info("TaskQueue deserializing ended")
        return 0, None

    def init(self, task_dict, force=False):
        return self.init_controller_queue(task_dict, force)

    def run_all(self, controller_queue_uuid, session=None):
        return self.get_tasks_from_controller_queue(controller_queue_uuid, session)

    def run_next(self, controller_queue_uuid, session=None):
        return self.get_task_from_controller_queue(controller_queue_uuid, session, False)

    def skip_next(self, controller_queue_uuid, task_uuid=None):
        return self.pop_task_from_controller_queue(controller_queue_uuid, task_uuid)

    def peek(self, controller_queue_uuid, task_uuid):
        return self.peek_task_from_controller_queue(controller_queue_uuid, task_uuid)

    def snapshot(self, controller_queue_uuid):
        return self.get_snapshot(controller_queue_uuid)

    def resume(self, controller_queue_uuid):
        return self.put_left_to_controller_queue(controller_queue_uuid)
