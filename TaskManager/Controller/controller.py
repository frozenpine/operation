# coding=utf-8

import sys
from os import environ, path

try:
    from TaskManager.protocol import TaskResult, TaskStatus
    from TaskManager.Controller.task_queue_manager import TaskQueueManager
    from TaskManager.Controller.task_dispatcher import TaskDispatcher
    from TaskManager.Controller.events import EventName
    from TaskManager.Controller.msg_loop import MsgQueue, MsgLoop
except ImportError:
    sys.path.append(path.join(path.dirname(__file__), '../'))
    from TaskManager.protocol import TaskResult, TaskStatus
    from TaskManager.Controller.task_queue_manager import TaskQueueManager
    from TaskManager.Controller.task_dispatcher import TaskDispatcher
    from TaskManager.Controller.events import EventName
    from TaskManager.Controller.msg_loop import MsgQueue, MsgLoop

msg_queue = MsgQueue()


class Controller(object):
    def __init__(self):
        rpc_addr = environ.get('RPC_SVR') or '0.0.0.0'
        rpc_port = environ.get('RPC_PORT') or 6000
        controller_svr = environ.get("CONTROLLER_SVR") or '127.0.0.1'
        controller_port = environ.get("CONTROLLER_PORT") or 7000

        self._task_dispatcher = TaskDispatcher(controller_svr, int(controller_port), msg_queue)
        self._task_dispatcher.start()

        self._task_manager = TaskQueueManager(rpc_addr, int(rpc_port), msg_queue)

        self._msg_loop = MsgLoop()
        self._msg_loop.register_callback(EventName.TaskResult, self._task_manager.event_relay)
        self._msg_loop.register_callback(EventName.TaskDispatch, self._task_dispatcher.event_relay)
        self._msg_loop.start()

    def run(self):
        self._task_manager.run()
