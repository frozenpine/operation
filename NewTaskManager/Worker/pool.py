# coding=utf-8
"""
Worker进程池
"""

import logging
import socket
import time
from multiprocessing import Pool
from multiprocessing import cpu_count

import time_calc
from NewTaskManager.Worker import worker_logger as logging
from NewTaskManager.protocol import TaskStatus, TaskResult, MSG_DICT
from SysManager.configs import SSHConfig
from SysManager.excepts import (ConfigInvalid, SSHAuthenticationException, SSHException, SSHNoValidConnectionsError)
from SysManager.executor import Executor


def init_socket(host, port):
    """
    对于工作进程初始化socket连接
    :param host: 主机
    :param port: 端口
    :return:
    """
    global socket_client
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_client.connect((host, port))
    logging.info('Socket Client Connect To Host: {0}, Port: {1}'.format(host, port))


def send(data):
    """
    发送消息
    :param data: 未序列化的数据
    :return:
    """
    global socket_client
    if isinstance(data, TaskResult):
        dump_data = data.serial()
        # 发送数据
        while 1:
            retry_count = 0
            try:
                socket_client.send(dump_data)
                logging.info('Socket Client Send Success: {0}'.format(data))
            except Exception, e:
                # 因server端socket异常未正常发送
                retry_count = retry_count + 1
                logging.warning('Socket Client Send Error: {0}'.format(e))
                logging.warning('Socket Client Send Retry {0} Time'.format(retry_count))
            else:
                break
        # 接受数据
        while 1:
            retry_count = 0
            try:
                ack = socket_client.recv(8192)
                logging.info('Socket Client Receive Success: {0}'.format(ack))
            except socket.timeout, e:
                # 未收到server端确认信息
                retry_count = retry_count + 1
                logging.warning('Socket Client Receive Error: {0}'.format(e))
                logging.warning('Socket Client Receive Retry {0} Time'.format(retry_count))
            else:
                break


def run(task_info):
    """
    调用Executor执行task
    :return:
    """
    # 获取queue_uuid, task_uuid
    queue_uuid, task_uuid = task_info.queue_uuid, task_info.task_uuid
    # 判断是否满足执行条件
    if not worker_pool.vacant():
        # 进程池满
        logging.warning('TaskUUID: {0}, TaskStatus: {1}'.format(task_uuid, TaskStatus.WorkerWating.value))
        status_code = TaskStatus.WorkerWaiting
        status_msg = MSG_DICT.get(status_code)
    else:
        ret_code, ret_msg = time_calc \
            .compare_timestamps(task_info.trigger_time, task_info.task_earliest, task_info.task_latest)
        if ret_code == 3:
            # 无法执行 退出
            logging.warning('TaskUUID: {0}, TaskStatus: {1}'.format(task_uuid, TaskStatus.TimeRangeExcept.value))
            status_code = TaskStatus.TimeRangeExcept
            status_msg = MSG_DICT.get(status_code)
        elif ret_code == 2:
            # 需要等待
            logging.info('TaskUUID: {0}, TaskStatus: {1}'.format(task_uuid, TaskStatus.WorkerWating.value))
            status_code = TaskStatus.TriggerTimeWaiting.value
            status_msg = u'需要等待{0}秒'.format(ret_msg)
        elif ret_code == 1:
            # 可以执行
            logging.info('TaskUUID: {0}, TaskStatus: {1}'.format(task_uuid, TaskStatus.Runnable.value))
            status_code = TaskStatus.Runnable
            status_msg = MSG_DICT.get(status_code)
        else:
            logging.warning('TaskUUID: {0}, TaskStatus: {1}'.format(task_uuid, TaskStatus.UnKnown.value))
            status_code = TaskStatus.UnKnown
            status_msg = MSG_DICT.get(status_code)
    result = TaskResult(queue_uuid=queue_uuid, task_uuid=task_uuid, status_code=status_code,
                        status_msg=status_msg, session=task_info.session)
    send(result)
    # 超时或未知情况下 退出
    if status_code in (TaskStatus.TimeRangeExcept, TaskStatus.UnKnown):
        return -1
    # 实例化SSHConfig初始化判断
    try:
        conf = SSHConfig(**task_info.task["remote"]["params"])
    except ConfigInvalid, e:
        # 配置文件格式错误 退出
        logging.warning('TaskUUID: {0}, TaskStatus: {1}'.format(task_uuid, TaskStatus.InitFailed.value))
        status_code, status_msg = TaskStatus.InitFailed, e
        result = TaskResult(queue_uuid=queue_uuid, task_uuid=task_uuid, status_code=status_code,
                            status_msg=status_msg, session=task_info.session)
        send(result)
        return -1
    # 实例化Executor初始化判断
    try:
        exe = Executor.CreateByWorker(conf)
    except (SSHNoValidConnectionsError, SSHAuthenticationException, SSHException), e:
        status_code, status_msg = TaskStatus.InitFailed, e
        result = TaskResult(queue_uuid=queue_uuid, task_uuid=task_uuid, status_code=status_code,
                            status_msg=status_msg, session=task_info.session)
        send(result)
        return -1
    # 开始正式执行
    ret_code, ret_msg = time_calc.compare_timestamps(
        task_info.trigger_time, task_info.task_earliest, task_info.task_latest
    )
    if ret_code == 3:
        # 直接跳过不执行
        pass
    else:
        if ret_code == 2:
            time.sleep(ret_msg)
        status_code = TaskStatus.Running
        status_msg = MSG_DICT.get(status_code)
        result = TaskResult(queue_uuid=queue_uuid, task_uuid=task_uuid, status_code=status_code,
                            status_msg=status_msg, session=task_info.session)
        send(result)
        mod = task_info.task["mod"]
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
        else:
            status_code = TaskStatus.UnKnown
            status_msg = MSG_DICT.get(status_code)
        result = TaskResult(queue_uuid=queue_uuid, task_uuid=task_uuid, status_code=status_code,
                            status_msg=status_msg, session=task_info.session, task_result=task_result)
        send(result)


class WorkerPool(object):
    def __init__(self):
        self.running_process = 0
        self.process_count = cpu_count()
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
        # self.worker_pool = Pool(processes=self.process_count, initializer=init_socket, initargs=('127.0.0.1', 7001))
        self.worker_pool = Pool(processes=self.process_count)

    def run(self, event):
        task_info = event.event_data
        self.worker_pool.apply_sync(run, (task_info,))


worker_pool = WorkerPool()
