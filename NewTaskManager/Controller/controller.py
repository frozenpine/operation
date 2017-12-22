# coding=utf-8

import sys
import logging
import time
from multiprocessing import Process
from os import environ, path

try:
    from NewTaskManager.protocol import TaskResult, TaskStatus
    from NewTaskManager.Controller.task_queue_manager import TaskQueueManager
    from NewTaskManager.Controller.task_dispatcher import TaskDispatcher
    from NewTaskManager.Controller.events import EventName
    from NewTaskManager.Controller.msg_loop import MsgQueue, MsgLoop
except ImportError:
    sys.path.append(path.join(path.dirname(__file__), '../'))
    from NewTaskManager.protocol import TaskResult, TaskStatus
    from NewTaskManager.Controller.task_queue_manager import TaskQueueManager
    from NewTaskManager.Controller.task_dispatcher import TaskDispatcher
    from NewTaskManager.Controller.events import EventName
    from NewTaskManager.Controller.msg_loop import MsgQueue, MsgLoop


msg_queue = MsgQueue()


class Controller(Process):
    def __init__(self):
        rpc_addr = environ.get('TM_HOST') or '0.0.0.0'
        rpc_port = environ.get('TM_PORT') or 6000
        socket_port = environ.get("SOCKET_PORT") or 7000
        socket_host = environ.get("SOCKET_HOST") or '0.0.0.0'
        self._msg_loop = MsgLoop()
        self._task_manager = TaskQueueManager(rpc_addr, rpc_port, msg_queue)
        self._task_dispatcher = TaskDispatcher(socket_host, socket_port, msg_queue)
        self._msg_loop.register_callback(EventName.TaskResult, self._task_manager.result_callback)
        self._msg_loop.register_callback(EventName.TaskDispath, self._task_dispatcher.event_relay)
        self._msg_loop.start()
        self._task_dispatcher.start()

    def run(self):
        self._task_manager.run()
