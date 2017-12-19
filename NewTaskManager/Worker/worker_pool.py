# coding=utf-8

import socket
from multiprocessing import Pool
from multiprocessing import cpu_count

import worker_time
from NewTaskManager.Worker import worker_logger as logging
from SysManager.configs import SSHConfig
from SysManager.excepts import (ConfigInvalid, SSHAuthenticationException, SSHException, SSHNoValidConnectionsError)
from SysManager.executor import Executor
from worker_protocol import TaskStatus


def init_socket(host, port):
    global socket_client
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_client.connect((host, port))


def send(data):
    """
    发送消息
    :param data:
    :return:
    """
    global socket_client
    if isinstance(data, Result):
        dump_data = data.to_str()
        # 发送数据
        while 1:
            retry_count = 0
            try:
                socket_client.send(dump_data)
                logging.info('Socket Client Send Success: {0}'.format(dump_data))
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


def run(task_info):
    """
    调用Executor执行task
    :return:
    """
    # 判断是否满足执行条件
    ret_code, ret_msg = worker_time.compare_timestamps(
        task_info.trigger_time, task_info.task_earliest, task_info.task_latest)
    if ret_code == 3:
        # 无法执行
        status_code, status_msg = TaskStatus.TimeRangeExcept.value, u'超出时间限制'
    elif ret_code == 2:
        # 需要等待
        status_code, status_msg = TaskStatus.TriggerTimeWaiting.value, u'需要等待{0}秒'.format(ret_msg)
    elif ret_code == 1:
        if worker_pool.vacant():
            status_code, status_msg = 100, u'可以直接执行'
        else:
            status_code, status_msg = 112, u'等待进程池空闲'
    else:
        status_code, status_msg = -1, u'未知错误'
    result = Result(task_info.queue_uuid, task_info.task_uuid, status_code, status_msg, task_info.session,
                    task_info.run_all_flag, None)
    socket_client.send(result)
    # 实例化SSHConfig初始化判断
    try:
        conf = SSHConfig(**task_info.task["remote"]["params"])
    except ConfigInvalid, status_msg:
        # 配置文件格式错误
        status_code = -1
        status_msg = status_msg.message
        task_result = None
        send(status_code, status_msg, task_result)
        return -1
    # 实例化Executor初始化判断
    try:
        exe = Executor.CreateByWorker(conf)
    except (SSHNoValidConnectionsError, SSHAuthenticationException, SSHException), status_msg:
        status_code = -1
        status_msg = status_msg.message
        task_result = None
        self.send_info(status_code, status_msg, task_result)
        return -1
    # 开始正式执行
    ret_code, ret_msg = get_time.compare_timestamps(
        self.controller_queue_trigger_time, self.task_earliest, self.task_latest
    )
    if ret_code == 3:
        # 直接跳过不执行
        """
        self.send_obj(
            Result(controller_queue_uuid=self.controller_queue_uuid,
                   task_uuid=self.task_uuid, status_code=121,
                   status_msg=u'超出时间范围', session=self.session,
                   run_all=self.run_all)
        )
        """
        pass
    else:
        if ret_code == 2:
            time.sleep(ret_msg)
        status_code, status_msg = 200, u"开始执行"
        self.send_obj(
            Result(controller_queue_uuid=self.controller_queue_uuid,
                   task_uuid=self.task_uuid, status_code=status_code,
                   status_msg=status_msg, session=self.session,
                   run_all=self.run_all)
        )
        mod = self.task["mod"]
        if isinstance(mod, dict):
            # 一个任务
            task_result = exe.run(mod)
            status_code = task_result.return_code
            if status_code != 0:
                status_code = 1
                status_msg = u"单任务执行失败"
            else:
                status_msg = u"单任务执行成功"
        if isinstance(mod, list):
            # 多个任务
            for each in mod:
                task_result = exe.run(each)
                status_code = task_result.return_code
                if status_code != 0:
                    status_code = 1
                    status_msg = u"多任务执行失败"
                    break
                else:
                    status_msg = u"多任务执行成功"
        self.send_info(status_code, status_msg, task_result)


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
        self.worker_pool = Pool(processes=self.process_count, initializer=init_socket, initargs=('127.0.0.1', 7001))

    def run(self, func, args):
        self.worker_pool.apply_sync(func, args)


worker_pool = WorkerPool()
