# coding=utf-8

import sys
import logging
import time
from multiprocessing import Queue
from multiprocessing import Process
from os import environ, path

sys.path.append(path.join(path.dirname(__file__), '../'))
from NewTaskManager.protocol import TaskResult, TaskStatus
from NewTaskManager.Controller.task_queue_manager import TaskQueueManager
from NewTaskManager.Controller.events import EventName, MessageEvent
# from NewTaskManager.Controller.msg_loop import msg_loop
''' from .msg_loop import MessageLoop
from .socket_server import ControllerSocketServer '''


class Controller(Process):
    def __init__(self):
        # self._to_task_manager = Queue()
        # self._to_task_dispatcher = Queue()
        self._events = Queue()
        self._callback_cache = {}
        rpc_addr = environ.get('TM_HOST') or '0.0.0.0'
        rpc_port = environ.get('TM_PORT') or 6000
        # socket_port = environ.get("SOCKET_PORT") or 7000
        # socket_host = environ.get("SOCKET_HOST") or '0.0.0.0'
        self._task_manager = TaskQueueManager(rpc_addr, rpc_port, self._events)
        self._task_manager.setDaemon(True)
        # self._socket_server = ControllerSocketServer(socket_host, socket_port)

    def run(self):
        self.register_callback(EventName.TaskResult, self._task_manager.result_callback)
        self._task_manager.start()
        self.register_callback(EventName.TaskDispath, self.task_dispath_test)
        self.msg_loop()

    def register_callback(self, event_name, func):
        if event_name not in self._callback_cache:
            self._callback_cache.update({event_name: [func]})
        else:
            self._callback_cache.get(event_name).append(func)
        logging.info(u'回调({func_name})注册事件({evt_name}:{evt_id})成功')

    def unregister_callback(self, event_name, func):
        if event_name not in self._callback_cache:
            logging.warning(u'未找到该事件名称')
        else:
            callback_list = self._callback_cache.get(event_name)
            if func not in callback_list:
                logging.warning(u'未注册该回调函数')
            else:
                callback_list.remove(func)
                if not callback_list:
                    self._callback_cache.pop(event_name)

    def task_dispath_test(self, event):
        logging.info('Task received: {}'.format(event.Data.to_dict()))
        time.sleep(3)
        self._events.put(MessageEvent(
            EventName.TaskResult, TaskResult('123', '456', TaskStatus.Success, None, {})))

    def msg_loop(self):
        while True:
            event = self._events.get()
            if not event.IsNotify:
                if event.IsRegiste:
                    self.register_callback(event.Name, event.Callback)
                else:
                    self.unregister_callback(event.Name, event.Callback)
            else:
                callback_list = self._callback_cache.get(event.Name)
                for func in callback_list:
                    func(event)
