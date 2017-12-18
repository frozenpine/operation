# coding=utf-8

import json
import socket

import worker_time
from NewTaskManager.Worker import worker_logger as logging
from worker_pool import worker_pool


class Result(object):
    def __init__(self, queue_uuid, task_uuid, status_code, status_msg, session, run_all_flag, task_result=None):
        self.queue_uuid = queue_uuid
        self.task_uuid = task_uuid
        self.status_code = status_code
        self.status_msg = status_msg
        self.session = session
        self.run_all_flag = run_all_flag
        self.task_result = task_result

    def to_dict(self):
        """
        转换为字典
        :return:
        """
        return vars(self)

    def to_str(self):
        """
        转换为字符串
        :return:
        """
        return json.dumps(self.to_dict())

    def type(self):
        if self.status_code in (-1, 100, 111, 112, 121):
            return 'init'
        elif self.status_code in (200,):
            return 'start'
        elif self.status_code in (0, 1, 2, 3, 4):
            return 'end'
        else:
            logging.warning('[node] type unknown: {0}'.format(self.status_code))


class Task(object):
    def __init__(self, queue_uuid, create_time, trigger_time, task_uuid, task_info, task_earliest, task_latest, session,
                 run_all_flag):
        self.queue_uuid = queue_uuid
        self.create_time = create_time
        self.trigger_time = trigger_time
        self.task_uuid = task_uuid
        self.task_info = task_info
        self.task_earliest = task_earliest
        self.task_latest = task_latest
        self.task_info = task_info
        self.session = session
        self.run_all_flag = run_all_flag
        # 初始化socket连接
        self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_client.connect(('127.0.0.1', 7000))
        ret_code, ret_msg = worker_time.compare_timestamps(self.trigger_time, self.task_earliest, self.task_latest)
        if ret_code == 3:
            # 无法执行
            status_code, status_msg = 121, u'超出时间限制'
        elif ret_code == 2:
            # 需要等待
            status_code, status_msg = 111, u'需要等待{0}秒'.format(ret_msg)
        elif ret_code == 1:
            if worker_pool.vacant():
                status_code, status_msg = 100, u'可以直接执行'
            else:
                status_code, status_msg = 112, u'等待进程池空闲'
        else:
            status_code, status_msg = -1, u'未知错误'
        result = Result(self.queue_uuid, self.task_uuid, status_code, status_msg, self.session, self.run_all_flag, None)
        self.send(Result)

    def send(self, data):
        if isinstance(data, Result):
            data = data.to_str()
            self.socket_client.send(data)
            # todo: 设置超时时间
            self.socket_client.recv(8192)
