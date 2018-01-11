# coding=utf-8

import sys
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


class Controller(object):
    def __init__(self):
        rpc_addr = environ.get('RPC_SVR') or '0.0.0.0'
        rpc_port = environ.get('RPC_PORT') or 6000
        socket_host = environ.get("SOCKET_HOST") or '127.0.0.1'
        socket_port = environ.get("SOCKET_PORT") or 7000

        self._task_dispatcher = TaskDispatcher(socket_host, socket_port, msg_queue)
        self._task_dispatcher.start()

        self._task_manager = TaskQueueManager(rpc_addr, rpc_port, msg_queue)

        self._msg_loop = MsgLoop()
        self._msg_loop.register_callback(EventName.TaskResult, self._task_manager.event_relay)
        self._msg_loop.register_callback(EventName.TaskDispatch, self._task_dispatcher.event_relay)
        self._msg_loop.start()

    def run(self):
        self._task_manager.run()

# if __name__ == '__main__':
#     controller = Controller()
#     controller.run()
