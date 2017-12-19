# coding=utf-8

import json
import socket

import worker_time
from NewTaskManager.Worker import worker_logger as logging
from SysManager.configs import SSHConfig
from SysManager.excepts import (ConfigInvalid, SSHAuthenticationException,
                                SSHException, SSHNoValidConnectionsError)
from SysManager.executor import Executor
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
            logging.warning('Result Object Has Unknown Type {0}'.format(self.status_code))


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




