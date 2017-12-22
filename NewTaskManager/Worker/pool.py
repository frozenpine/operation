# coding=utf-8
"""
Worker进程池
"""

import json
import socket
import threading
import time
from multiprocessing import Pool

from NewTaskManager.Common import get_time
from NewTaskManager.Worker import worker_logger as logging
from NewTaskManager.protocol import TaskStatus, TaskResult, MSG_DICT
from SysManager.configs import SSHConfig
from SysManager.excepts import (ConfigInvalid, SSHAuthenticationException, SSHException, SSHNoValidConnectionsError)
from SysManager.executor import Executor

socket_object = threading.local()


def init_socket(host, port):
    """
    对于工作进程初始化socket连接
    :param host: 主机
    :param port: 端口
    :return:
    """
    # global socket_client
    # socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # socket_client.connect((host, port))
    socket_object.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_object.socket_client.connect((host, port))
    logging.info('Client Connect To Host: {0}, Port: {1}'.format(host, port))


def send(data):
    """
    发送消息
    :param data: 未序列化的数据
    :return:
    """
    if isinstance(data, TaskResult):
        dump_data = data.serial()
        # 发送数据
        while 1:
            socket_client = socket_object.socket_client
            retry_count = 0
            try:
                logging.info('Client Send Len: {0}'.format(len(dump_data)))
                socket_client.send(dump_data)
                logging.info(u'Client Send: {0}'.format(json.dumps(data.to_dict(), ensure_ascii=False)))
                ack = socket_client.recv(8192)
                logging.info('Client Receive: {0}'.format(ack))
                ack = json.loads(ack)
                if ack.get('ack') == 'Fail':
                    raise Exception('TaskResult Deserialize Error')
            except socket.error, e:
                # 因server端socket异常未正常发送
                retry_count = retry_count + 1
                init_socket('127.0.0.1', 7001)
                logging.warning('Client Send Error, Retry {0}'.format(retry_count))
            else:
                break


def run(task):
    """
    调用Executor执行task
    :return:
    """
    # 获取queue_uuid, task_uuid
    queue_uuid, task_uuid = task.queue_uuid, task.task_uuid
    # 判断是否满足执行条件
    if not worker_pool.vacant():
        # 进程池满
        logging.warning('TaskUUID: {0}, TaskStatus: {1}'.format(task_uuid, TaskStatus.WorkerWating.value))
        status_code = TaskStatus.WorkerWaiting
        status_msg = MSG_DICT.get(status_code)
        result = TaskResult(queue_uuid=queue_uuid, task_uuid=task_uuid, status_code=status_code,
                            status_msg=status_msg, session=task.session)
        send(result)
        return -1
    else:
        ret_code, ret_msg = get_time \
            .compare_timestamps(task.trigger_time, task.task_earliest, task.task_latest)
        if ret_code == 3:
            # 无法执行 直接返回-1
            logging.warning('TaskUUID: {0}, TaskStatus: {1}'.format(task_uuid, TaskStatus.TimeRangeExcept.value))
            status_code = TaskStatus.TimeRangeExcept
            status_msg = MSG_DICT.get(status_code)
            result = TaskResult(queue_uuid=queue_uuid, task_uuid=task_uuid, status_code=status_code,
                                status_msg=status_msg, session=task.session)
            send(result)
            return -1
        elif ret_code == 2:
            # 需要等待
            logging.info('TaskUUID: {0}, TaskStatus: {1}'.format(task_uuid, TaskStatus.WorkerWaiting.value))
            status_code = TaskStatus.TriggerTimeWaiting.value
            status_msg = u'需要等待{0}秒'.format(ret_msg)
            result = TaskResult(queue_uuid=queue_uuid, task_uuid=task_uuid, status_code=status_code,
                                status_msg=status_msg, session=task.session)
            send(result)
        elif ret_code == 1:
            # 可以执行
            logging.info('TaskUUID: {0}, TaskStatus: {1}'.format(task_uuid, TaskStatus.Runnable.value))
            status_code = TaskStatus.Runnable
            status_msg = MSG_DICT.get(status_code)
            result = TaskResult(queue_uuid=queue_uuid, task_uuid=task_uuid, status_code=status_code,
                                status_msg=status_msg, session=task.session)
            send(result)
        else:
            # 异常情况 直接返回-1
            logging.warning('TaskUUID: {0}, TaskStatus: {1}'.format(task_uuid, TaskStatus.UnKnown.value))
            status_code = TaskStatus.UnKnown
            status_msg = MSG_DICT.get(status_code)
            result = TaskResult(queue_uuid=queue_uuid, task_uuid=task_uuid, status_code=status_code,
                                status_msg=status_msg, session=task.session)
            send(result)
            return -1
    # 实例化SSHConfig初始化判断
    try:
        conf = SSHConfig(**task.task_info["remote"]["params"])
    except ConfigInvalid, e:
        # 配置文件格式错误 直接返回-1
        logging.warning('TaskUUID: {0}, TaskStatus: {1}'.format(task_uuid, TaskStatus.InitFailed.value))
        status_code, status_msg = TaskStatus.InitFailed, e
        result = TaskResult(queue_uuid=queue_uuid, task_uuid=task_uuid, status_code=status_code,
                            status_msg=status_msg, session=task.session)
        send(result)
        return -1
    # 实例化Executor初始化判断
    try:
        exe = Executor.CreateByWorker(conf)
    except (SSHNoValidConnectionsError, SSHAuthenticationException, SSHException), e:
        # SSH连接失败 直接返回-1
        status_code, status_msg = TaskStatus.InitFailed, e
        result = TaskResult(queue_uuid=queue_uuid, task_uuid=task_uuid, status_code=status_code,
                            status_msg=status_msg, session=task.session)
        send(result)
        return -1
    # 开始正式执行
    ret_code, ret_msg = get_time.compare_timestamps(
        task.trigger_time, task.task_earliest, task.task_latest
    )
    if ret_code == 2:
        logging.info('Start Sleeping {0} Seconds'.format(ret_msg))
        time.sleep(ret_msg)
    status_code = TaskStatus.Running
    status_msg = MSG_DICT.get(status_code)
    result = TaskResult(queue_uuid=queue_uuid, task_uuid=task_uuid, status_code=status_code,
                        status_msg=status_msg, session=task.session)
    send(result)
    mod = task.task_info["mod"]
    if isinstance(mod, dict):
        # 一个任务
        task_result = exe.run(mod)
        ret_code = task_result.return_code
        if ret_code != 0:
            status_code = TaskStatus.Failed
            status_msg = u"单任务执行失败"
        else:
            status_code = TaskStatus.Success
            status_msg = u"单任务执行成功"
        result = TaskResult(queue_uuid=queue_uuid, task_uuid=task_uuid, status_code=status_code,
                            status_msg=status_msg, session=task.session, task_result=task_result)
        send(result)
        return 0
    elif isinstance(mod, list):
        # 多个任务
        for each in mod:
            task_result = exe.run(each)
            ret_code = task_result.return_code
            if ret_code != 0:
                status_code = TaskStatus.Failed
                status_msg = u"多任务执行失败"
                break
            else:
                status_code = TaskStatus.Success
                status_msg = u"多任务执行成功"
        result = TaskResult(queue_uuid=queue_uuid, task_uuid=task_uuid, status_code=status_code,
                            status_msg=status_msg, session=task.session, task_result=task_result)
        send(result)
        return 0
    else:
        # 异常情况 直接返回 - 1
        status_code = TaskStatus.UnKnown
        status_msg = MSG_DICT.get(status_code)
        result = TaskResult(queue_uuid=queue_uuid, task_uuid=task_uuid, status_code=status_code,
                            status_msg=status_msg, session=task.session)
        send(result)
        return -1


class WorkerPool(object):
    def __init__(self):
        self.running_process = 0
        # self.process_count = cpu_count()
        self.process_count = 2
        self.worker_pool = None

    def vacant(self):
        if self.running_process == self.process_count:
            return False
        else:
            return True

    def add_running_process(self):
        self.running_process += 1

    def minus_running_process(self):
        self.running_process -= 1

    def start(self):
        self.worker_pool = Pool(processes=self.process_count, initializer=init_socket, initargs=('127.0.0.1', 7001))

    def run(self, event):
        task_info = event.event_data
        self.worker_pool.apply_async(run, (task_info,))


worker_pool = WorkerPool()
