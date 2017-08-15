# coding=utf-8

import json
import logging
import time
from multiprocessing import Pipe, Process
from threading import Thread

import gevent

import get_time
from msg_queue import msg_queue
from SysManager.configs import SSHConfig
from SysManager.excepts import (ConfigInvalid, SSHAuthenticationException,
                                SSHException, SSHNoValidConnectionsError)
from SysManager.executor import Executor
from worker_queue import WorkerQueue


class Result(object):
    def __init__(self, controller_queue_uuid, task_uuid, status_code,
                 status_msg, session, run_all, task_result=None):
        self.controller_queue_uuid = controller_queue_uuid
        self.task_uuid = task_uuid
        self.task_status = (status_code, status_msg)
        self.session = session
        self.run_all = run_all
        if task_result:
            if not isinstance(task_result, dict):
                self.task_result = vars(task_result)
            else:
                self.task_result = task_result
        else:
            self.task_result = task_result

    def to_dict(self):
        """
        转换为字典
        :return: 字典
        """
        return vars(self)

    def to_str(self):
        """
        转换为字符串
        :return: 字符串
        """
        return json.dumps(self.to_dict())

    def type(self):
        """
        判断类型
        :return: 返回init start end
        """
        if self.task_status[0] in (-1, 100, 111, 112, 121):
            return "init"
        if self.task_status[0] in (200,):
            return "start"
        if self.task_status[0] in (0, 1, 2, 3):
            return "end"


class RunTask(Process):
    def __init__(self, controller_queue_uuid, controller_queue_create_time, controller_queue_trigger_time, task_uuid,
                 task_earliest, task_latest, task, pipe_child, session, run_all, idle_process_count):
        Process.__init__(self)
        self.controller_queue_uuid = controller_queue_uuid
        self.controller_queue_create_time = controller_queue_create_time
        self.controller_queue_trigger_time = controller_queue_trigger_time
        self.task_uuid = task_uuid
        self.task = task
        self.task_earliest = task_earliest
        self.task_latest = task_latest
        self.pipe_child = pipe_child
        self.session = session
        self.run_all = run_all
        # 计算是否需要睡眠等待以及当前进程池是否已满
        if idle_process_count < 0:
            pass
        ret_code, ret_msg = get_time.compare_timestamps(self.controller_queue_trigger_time, self.task_earliest,
                                                        self.task_latest)
        if ret_code == 3:
            # 无法执行
            self.send(121, u"超出时间限制", None)
        if ret_code == 2:
            # 需要等待
            self.send(111, u"需要等待{0}秒".format(ret_msg), None)
        if ret_code == 1 and idle_process_count <= 0:
            # 等待进程池空闲
            self.send(112, u"等待进程池空闲", None)
        if ret_code == 1 and idle_process_count > 0:
            # 任务可以直接执行
            self.send(100, u"可以直接执行", None)

    def send(self, status_code, status_msg, task_result):
        """
        管道回传信息
        :param status_code: 任务状态码
        :param status_msg: 任务状态信息
        :param task_result: 任务状态结果
        :return:
        """
        self.pipe_child.send(
            Result(controller_queue_uuid=self.controller_queue_uuid, task_uuid=self.task_uuid,
                   status_code=status_code, status_msg=status_msg, session=self.session, run_all=self.run_all,
                   task_result=task_result)
        )

    def run(self):
        """
        调用Executor执行task
        :return:
        """
        # 实例化SSHConfig初始化判断
        try:
            conf = SSHConfig(**self.task["remote"]["params"])
        except ConfigInvalid, status_msg:
            # 配置文件格式错误
            status_code = -1
            status_msg = status_msg.message
            task_result = None
            self.send(status_code, status_msg, task_result)
            return -1
        # 实例化Executor初始化判断
        try:
            exe = Executor.CreateByWorker(conf)
        except (SSHNoValidConnectionsError, SSHAuthenticationException, SSHException), status_msg:
            status_code = -1
            status_msg = status_msg.message
            task_result = None
            self.send(status_code, status_msg, task_result)
            return -1
        # 开始正式执行
        ret_code, ret_msg = get_time.compare_timestamps(
            self.controller_queue_trigger_time, self.task_earliest, self.task_latest
        )
        if ret_code == 3:
            # 直接跳过不执行
            ''' self.pipe_child.send(
                Result(controller_queue_uuid=self.controller_queue_uuid, task_uuid=self.task_uuid,
                       status_code=121, status_msg=u'超出时间范围', session=self.session, run_all=self.run_all)) '''
            pass
        else:
            if ret_code == 2:
                time.sleep(ret_msg)
            status_code, status_msg = 200, u"开始执行"
            self.pipe_child.send(
                Result(controller_queue_uuid=self.controller_queue_uuid, task_uuid=self.task_uuid,
                       status_code=status_code, status_msg=status_msg, session=self.session, run_all=self.run_all))
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
            self.send(status_code, status_msg, task_result)


class ParentPipe(Thread):
    def __init__(self, pipe_parent, init_callback, start_callback, end_callback):
        Thread.__init__(self)
        self.pipe_parent = pipe_parent
        self.init_callback = init_callback
        self.start_callback = start_callback
        self.end_callback = end_callback

    def run(self):
        """
        监听管道消息
        :return:
        """
        while self.pipe_parent:
            info = self.pipe_parent.recv()
            if info:
                if info.type() == "init":
                    self.init_callback(info)
                if info.type() == "start":
                    self.start_callback(info)
                if info.type() == "end":
                    self.end_callback(info)
            else:
                break


class Worker(object):
    def __init__(self):
        self.worker_queue = WorkerQueue("worker_queue")
        self.process_dict = dict()
        self.callback_dict = dict()

    def loop(self):
        """
        取出worker_queue中的task并实例化executor执行
        :return:
        """
        init_callback = self.callback_dict["init_callback"]
        start_callback = self.callback_dict["start_callback"]
        end_callback = self.callback_dict["end_callback"]
        pipe_parent, pipe_child = Pipe(duplex=False)
        ParentPipe(pipe_parent, init_callback, start_callback, end_callback).start()
        max_process = 2
        while 1:
            ret = msg_queue.todo_task_queue.get()
            controller_queue_uuid = ret["controller_queue_uuid"]
            controller_queue_create_time = ret["controller_queue_create_time"]
            controller_queue_trigger_time = ret["controller_queue_trigger_time"]
            task_uuid = ret["task_uuid"]
            task_earliest = ret["task_earliest"]
            task_latest = ret["task_latest"]
            task = ret["task"]
            run_all = ret["run_all"]
            session = ret["session"]
            idle_process_count = max_process - len(self.process_dict)
            t = RunTask(controller_queue_uuid, controller_queue_create_time, controller_queue_trigger_time, task_uuid,
                        task_earliest, task_latest, task, pipe_child, session, run_all, idle_process_count)
            while 1:
                for k in self.process_dict.keys():
                    if not self.process_dict[k][0].is_alive():
                        self.process_dict.pop(k)
                if len(self.process_dict) < max_process:
                    t.start()
                    start_time = get_time.current_timestamp()
                    self.process_dict.update({task_uuid: [t, start_time]})
                    break
                else:
                    gevent.sleep(0)
            gevent.sleep(0)

    def kill_process_callback(self, task_uuid):
        """
        终止进程回调
        :param task_uuid: task的uuid
        :return:
        """
        if task_uuid in self.process_dict.keys():
            self.process_dict[task_uuid][0].terminate()
            self.process_dict.pop(task_uuid)
            return 0, u"终止进程成功"
        else:
            return -1, u"无此进程"

    def register_callback(self, event, callback):
        """
        向worker注册事件回调
        :param event: 事件
        :param callback: 回调
        :return:
        """
        self.callback_dict[event] = callback
