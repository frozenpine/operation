# coding=utf-8

import json
from multiprocessing import Process, Pipe
from threading import Thread

import gevent

import get_time
from SysManager.configs import SSHConfig
from SysManager.executor import Executor
from msg_queue import msg_queue
from worker_queue import WorkerQueue


class Result(object):
    def __init__(self, controller_queue_uuid, task_uuid, task_status, session, run_all, task_result=None):
        status_relation = {100: 1, 0: 2}
        self.controller_queue_uuid = controller_queue_uuid
        self.task_uuid = task_uuid
        self.task_status = task_status
        self.session = session
        self.run_all = run_all
        if self.task_status in status_relation:
            self.task_status = status_relation[self.task_status]
        else:
            self.task_status = 3
        if task_result:
            if not isinstance(task_result, dict):
                self.task_result = vars(task_result)
            else:
                self.task_result = task_result
        else:
            self.task_result = task_result

    def to_dict(self):
        return vars(self)

    def to_str(self):
        return json.dumps(self.to_dict())

    def type(self):
        if not self.task_result:
            return "start"
        else:
            return "end"


class RunTask(Process):
    def __init__(self, controller_queue_uuid, task_uuid, task, pipe_child, session, run_all):
        Process.__init__(self)
        self.controller_queue_uuid = controller_queue_uuid
        self.task_uuid = task_uuid
        self.task = task
        self.pipe_child = pipe_child
        self.session = session
        self.run_all = run_all

    def run(self):
        """
        调用Executor执行task
        :return:
        """
        self.pipe_child.send(Result(self.controller_queue_uuid, self.task_uuid, 100, self.session, self.run_all))
        task_status, task_result = -1, None
        try:
            conf = SSHConfig(**self.task["remote"]["params"])
        except TypeError:
            # SSH格式错误
            task_status = 3
            task_result = {
                "destination": None, "module": None, "return_code": -1, "error_msg": "", "data": {}, "lines": []
            }
        else:
            exe = Executor.Create(conf)
            if exe:
                mod = self.task["mod"]
                if isinstance(mod, dict):
                    # 一个任务
                    task_result = exe.run(mod)
                    task_status = task_result.return_code
                if isinstance(mod, list):
                    # 多个任务
                    for each in mod:
                        task_result = exe.run(each)
                        task_status = task_result.return_code
                        if task_status != 0:
                            break
            else:
                task_status = 3
                task_result = {
                    "destination": None, "module": None, "return_code": -1, "error_msg": "", "data": {}, "lines": []
                }
        self.pipe_child.send(
            Result(self.controller_queue_uuid, self.task_uuid, task_status, self.session, self.run_all, task_result))


class ParentPipe(Thread):
    def __init__(self, pipe_parent, start_callback, end_callback):
        Thread.__init__(self)
        self.pipe_parent = pipe_parent
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
        start_callback = self.callback_dict["start_callback"]
        end_callback = self.callback_dict["end_callback"]
        pipe_parent, pipe_child = Pipe(duplex=False)
        ParentPipe(pipe_parent, start_callback, end_callback).start()
        max_process = 2
        while 1:
            ret = msg_queue.todo_task_queue.get()
            run_all = ret["run_all"]
            session = ret["session"]
            ret = ret["ret"]
            gevent.sleep(0)
            controller_queue_uuid = ret["controller_queue_uuid"]
            task_uuid = ret["task_uuid"]
            task = ret["task"]
            start_time = get_time.current_timestamp()
            t = RunTask(controller_queue_uuid, task_uuid, task, pipe_child, session, run_all)
            while 1:
                for k in self.process_dict.keys():
                    if not self.process_dict[k][0].is_alive():
                        self.process_dict.pop(k)
                if len(self.process_dict) < max_process:
                    t.start()
                    self.process_dict.update({task_uuid: [t, start_time]})
                    break
                else:
                    gevent.sleep(0)
            gevent.sleep(0)

    def register_callback(self, event, callback):
        """
        向worker注册事件回调
        :param event: 事件
        :param callback: 回调
        :return:
        """
        self.callback_dict[event] = callback
